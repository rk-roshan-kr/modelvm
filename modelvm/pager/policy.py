"""Eviction policies for the Model Pager."""

from __future__ import annotations
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set
from modelvm.core.manifest import ModelManifest


class EvictionPolicy(ABC):
    """Abstract base class for model eviction policies."""

    @abstractmethod
    def select_eviction_candidates(
        self,
        resident_models: Dict[str, ModelManifest],
        required_ram_gb: float,
        available_ram_gb: float,
        protected_ids: Optional[Set[str]] = None,
        future_demanded_ids: Optional[Set[str]] = None,
    ) -> List[ModelManifest]:
        """Selects a sequence of resident models to evict to satisfy required RAM."""
        pass


class LRUEvictionPolicy(EvictionPolicy):
    """Least Recently Used (LRU) policy."""

    def select_eviction_candidates(
        self,
        resident_models: Dict[str, ModelManifest],
        required_ram_gb: float,
        available_ram_gb: float,
        protected_ids: Optional[Set[str]] = None,
        future_demanded_ids: Optional[Set[str]] = None,
    ) -> List[ModelManifest]:
        protected = protected_ids or set()
        candidates = [m for m in resident_models.values() if m.id not in protected]
        # Sort by oldest last_accessed
        candidates.sort(key=lambda m: m.last_accessed)

        to_evict: List[ModelManifest] = []
        freed = 0.0
        deficit = required_ram_gb - available_ram_gb

        for model in candidates:
            if freed >= deficit:
                break
            to_evict.append(model)
            freed += model.ram_required

        return to_evict


class CostAwareEvictionPolicy(EvictionPolicy):
    """Cost-Aware Eviction policy that balances RAM freed, reload latency, and predicted future demand.
    
    Prefers evicting models that:
    1. Are NOT in the predicted future working set.
    2. Have low re-loading latency (fast to bring back if needed).
    3. Have not been accessed recently.
    """

    def select_eviction_candidates(
        self,
        resident_models: Dict[str, ModelManifest],
        required_ram_gb: float,
        available_ram_gb: float,
        protected_ids: Optional[Set[str]] = None,
        future_demanded_ids: Optional[Set[str]] = None,
    ) -> List[ModelManifest]:
        protected = protected_ids or set()
        future = future_demanded_ids or set()
        candidates = [m for m in resident_models.values() if m.id not in protected]

        now = time.time()

        def eviction_priority_score(m: ModelManifest) -> float:
            # Higher score = more desirable to EVICT first
            future_penalty = 1000.0 if m.id in future else 0.0
            recency_sec = max(0.1, now - m.last_accessed)
            # Evict if: old, low reload cost, high memory yield, not needed in future
            reload_cost = m.load_time * 2.0
            return (recency_sec * 0.5) + (m.ram_required * 1.5) - reload_cost - future_penalty

        # Sort descending by priority to evict
        candidates.sort(key=eviction_priority_score, reverse=True)

        to_evict: List[ModelManifest] = []
        freed = 0.0
        deficit = required_ram_gb - available_ram_gb

        for model in candidates:
            if freed >= deficit:
                break
            to_evict.append(model)
            freed += model.ram_required

        return to_evict
