"""Model Pager: Virtual memory subsystem managing model residency within a strict RAM/VRAM budget."""

from __future__ import annotations
import time
from typing import Callable, Dict, List, Optional, Set
from modelvm.core.manifest import ModelManifest
from modelvm.core.types import ModelStatus, PagingAction, PagingEvent
from modelvm.pager.policy import CostAwareEvictionPolicy, EvictionPolicy, LRUEvictionPolicy
from modelvm.registry.catalog import ModelCatalog


class ModelPager:
    """Virtual memory manager for heterogeneous open-weight models.
    
    See PDR Section 4 & 11:
    - Maintains an active RAM/VRAM budget (e.g. 8.0 GB)
    - Dynamically pages models in from the 52.7 GB library
    - Evicts or unloads models when capacity is exceeded or role is done
    - Emits real-time telemetry events
    """

    def __init__(
        self,
        catalog: ModelCatalog,
        memory_budget_gb: float = 8.0,
        policy: Optional[EvictionPolicy] = None,
    ):
        self.catalog = catalog
        self.memory_budget_gb = memory_budget_gb
        self.policy: EvictionPolicy = policy or CostAwareEvictionPolicy()
        
        self._resident: Dict[str, ModelManifest] = {}
        self._pinned: Set[str] = set()
        
        # Telemetry & Performance Counters
        self.peak_memory_gb: float = 0.0
        self.total_page_ins: int = 0
        self.total_page_outs: int = 0
        self.total_evictions: int = 0
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.total_paging_time_sec: float = 0.0
        
        self.event_log: List[PagingEvent] = []
        self._listeners: List[Callable[[PagingEvent], None]] = []

    @property
    def active_memory_gb(self) -> float:
        """Sum of RAM required by all currently resident models."""
        return round(sum(m.ram_required for m in self._resident.values()), 2)

    @property
    def free_memory_gb(self) -> float:
        """Available memory before reaching the hard budget."""
        return round(max(0.0, self.memory_budget_gb - self.active_memory_gb), 2)

    def is_resident(self, model_id: str) -> bool:
        """Checks if a model is currently in active memory."""
        return model_id in self._resident

    def add_listener(self, listener: Callable[[PagingEvent], None]) -> None:
        """Registers a callback for live paging events."""
        self._listeners.append(listener)

    def _emit(self, event: PagingEvent) -> None:
        """Records and broadcasts a paging event."""
        self.event_log.append(event)
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"[ModelPager] Listener error: {e}")

    def page_in(
        self,
        model_id: str,
        protected_ids: Optional[Set[str]] = None,
        future_demanded_ids: Optional[Set[str]] = None,
    ) -> PagingEvent:
        """Pages a model into active memory, evicting other models if necessary.
        
        If the model is already resident, registers a CACHE_HIT (0s latency).
        """
        model = self.catalog.get(model_id)
        if not model:
            raise ValueError(f"Model '{model_id}' not found in catalog")

        now = time.time()

        # Cache Hit
        if model_id in self._resident:
            self.cache_hits += 1
            model.last_accessed = now
            model.access_count += 1
            model.status = ModelStatus.RESIDENT
            
            event = PagingEvent(
                action=PagingAction.CACHE_HIT,
                model_id=model_id,
                ram_gb=model.ram_required,
                active_memory_gb=self.active_memory_gb,
                memory_budget_gb=self.memory_budget_gb,
                reason=f"Model '{model.name}' already resident in cache",
                duration_sec=0.0,
            )
            self._emit(event)
            return event

        # Cache Miss
        self.cache_misses += 1
        protected = set(protected_ids or set())
        protected.add(model_id)

        # Check if model fits in budget
        if model.ram_required > self.memory_budget_gb:
            raise MemoryError(
                f"Model '{model.name}' requires {model.ram_required} GB, exceeding total budget of {self.memory_budget_gb} GB"
            )

        # Evict models if needed to make room
        if self.free_memory_gb < model.ram_required:
            self._evict_for(
                required_ram_gb=model.ram_required,
                protected_ids=protected,
                future_demanded_ids=future_demanded_ids,
            )

        # Page-in model
        start_time = time.time()
        # Simulated loading latency (or actual file load in real runtime)
        load_duration = model.load_time
        
        model.status = ModelStatus.RESIDENT
        model.last_accessed = now
        model.access_count += 1
        self._resident[model_id] = model
        
        self.total_page_ins += 1
        self.total_paging_time_sec += load_duration

        if self.active_memory_gb > self.peak_memory_gb:
            self.peak_memory_gb = self.active_memory_gb

        event = PagingEvent(
            action=PagingAction.PAGE_IN,
            model_id=model_id,
            ram_gb=model.ram_required,
            active_memory_gb=self.active_memory_gb,
            memory_budget_gb=self.memory_budget_gb,
            reason=f"Loaded '{model.name}' (+{model.ram_required} GB)",
            duration_sec=load_duration,
            metadata={"quantization": model.quantization, "load_time_sec": model.load_time},
        )
        self._emit(event)
        return event

    def _evict_for(
        self,
        required_ram_gb: float,
        protected_ids: Set[str],
        future_demanded_ids: Optional[Set[str]] = None,
    ) -> List[PagingEvent]:
        """Selects and unloads resident models to free up required RAM."""
        candidates = self.policy.select_eviction_candidates(
            resident_models=self._resident,
            required_ram_gb=required_ram_gb,
            available_ram_gb=self.free_memory_gb,
            protected_ids=protected_ids,
            future_demanded_ids=future_demanded_ids,
        )

        events: List[PagingEvent] = []
        for model in candidates:
            evict_event = self.page_out(
                model_id=model.id,
                action=PagingAction.EVICT,
                reason=f"Evicted to free {model.ram_required} GB for incoming model",
            )
            events.append(evict_event)
            self.total_evictions += 1
            if self.free_memory_gb >= required_ram_gb:
                break

        return events

    def page_out(
        self,
        model_id: str,
        action: PagingAction = PagingAction.PAGE_OUT,
        reason: str = "Unloaded model",
    ) -> PagingEvent:
        """Unloads a model from active memory back to disk storage."""
        model = self._resident.get(model_id)
        if not model:
            # Model already on disk
            return PagingEvent(
                action=action,
                model_id=model_id,
                ram_gb=0.0,
                active_memory_gb=self.active_memory_gb,
                memory_budget_gb=self.memory_budget_gb,
                reason=f"Model '{model_id}' was not resident",
                duration_sec=0.0,
            )

        unload_time = 0.05  # Memory release is nearly instantaneous
        del self._resident[model_id]
        if model_id in self._pinned:
            self._pinned.remove(model_id)

        model.status = ModelStatus.DISK
        self.total_page_outs += 1

        event = PagingEvent(
            action=action,
            model_id=model_id,
            ram_gb=model.ram_required,
            active_memory_gb=self.active_memory_gb,
            memory_budget_gb=self.memory_budget_gb,
            reason=reason,
            duration_sec=unload_time,
        )
        self._emit(event)
        return event

    def prefetch(
        self,
        model_id: str,
        protected_ids: Optional[Set[str]] = None,
        future_demanded_ids: Optional[Set[str]] = None,
    ) -> Optional[PagingEvent]:
        """Prefetches a model into memory ahead of time if space permits without thrashing."""
        if self.is_resident(model_id):
            return None
        model = self.catalog.get(model_id)
        if not model:
            return None

        # Prefetch if free memory is sufficient or lowest eviction penalty
        if self.free_memory_gb >= model.ram_required:
            event = self.page_in(
                model_id=model_id,
                protected_ids=protected_ids,
                future_demanded_ids=future_demanded_ids,
            )
            event.action = PagingAction.PREFETCH
            event.reason = f"Prefetched '{model.name}' into spare memory (+{model.ram_required} GB)"
            return event
        return None

    def reset(self) -> None:
        """Clears all resident models and resets counters."""
        for m in list(self._resident.values()):
            m.status = ModelStatus.DISK
        self._resident.clear()
        self._pinned.clear()
        self.peak_memory_gb = 0.0
        self.total_page_ins = 0
        self.total_page_outs = 0
        self.total_evictions = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_paging_time_sec = 0.0
        self.event_log.clear()

    def get_status(self) -> Dict:
        """Returns comprehensive virtual memory status."""
        resident_list = [
            {
                "id": m.id,
                "name": m.name,
                "ram_required": m.ram_required,
                "capabilities": [c.value for c in m.capabilities],
                "last_accessed": m.last_accessed,
                "access_count": m.access_count,
            }
            for m in self._resident.values()
        ]
        
        disk_list = [
            {
                "id": m.id,
                "name": m.name,
                "ram_required": m.ram_required,
                "capabilities": [c.value for c in m.capabilities],
            }
            for m in self.catalog.all_models()
            if m.id not in self._resident
        ]

        hit_rate = (
            round(self.cache_hits / (self.cache_hits + self.cache_misses), 3)
            if (self.cache_hits + self.cache_misses) > 0
            else 0.0
        )

        return {
            "active_memory_gb": self.active_memory_gb,
            "memory_budget_gb": self.memory_budget_gb,
            "free_memory_gb": self.free_memory_gb,
            "peak_memory_gb": round(self.peak_memory_gb, 2),
            "total_library_size_gb": self.catalog.total_library_size_gb(),
            "resident_count": len(self._resident),
            "disk_count": len(disk_list),
            "cache_hit_rate": hit_rate,
            "total_page_ins": self.total_page_ins,
            "total_page_outs": self.total_page_outs,
            "total_evictions": self.total_evictions,
            "resident_models": resident_list,
            "disk_models": disk_list,
        }
