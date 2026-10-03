"""Cognitive Kernel: Central runtime orchestrating paging, scheduling, and execution."""

from __future__ import annotations
import time
from typing import Callable, Dict, List, Optional, Set
from pydantic import BaseModel, Field

from modelvm.core.manifest import ModelManifest
from modelvm.core.state_packet import CognitiveStatePacket
from modelvm.core.types import AblationMode, Capability, PagingAction, PagingEvent, TaskStatus
from modelvm.executor.backends import ModelBackend, SimulationBackend
from modelvm.pager.memory_manager import ModelPager
from modelvm.pager.policy import CostAwareEvictionPolicy, LRUEvictionPolicy
from modelvm.registry.catalog import ModelCatalog
from modelvm.router.confidence import ConfidenceAssessment, ConfidenceController
from modelvm.router.task_decomposer import CognitiveStagePlan, TaskDecomposer
from modelvm.router.working_set import CognitiveWorkingSetPredictor
from modelvm.scheduler.cognitive_scheduler import CognitiveScheduler, SchedulingScoreBreakdown


class StageExecutionResult(BaseModel):
    """Telemetry and output for a single cognitive execution stage."""
    stage_index: int
    stage_title: str
    capability: Capability
    model_id: str
    model_name: str
    model_ram_gb: float
    paging_action: PagingAction
    paging_duration_sec: float
    execution_duration_sec: float
    total_stage_duration_sec: float
    active_memory_gb: float
    confidence_score: float
    escalated: bool = False
    csp_snapshot: Dict
    score_breakdowns: List[Dict] = Field(default_factory=list)


class TaskExecutionSummary(BaseModel):
    """Final summary metrics of a multi-stage task execution."""
    task_goal: str
    ablation_mode: AblationMode
    status: TaskStatus
    total_stages: int
    peak_resident_memory_gb: float
    memory_budget_gb: float
    total_library_size_gb: float
    memory_savings_ratio: float
    capability_density: float
    total_duration_sec: float
    total_paging_time_sec: float
    total_execution_time_sec: float
    cache_hit_rate: float
    stage_results: List[StageExecutionResult]
    final_csp: Dict


class CognitiveKernel:
    """The ModelVM Cognitive Operating System Kernel."""

    def __init__(
        self,
        catalog: Optional[ModelCatalog] = None,
        memory_budget_gb: float = 8.0,
        backend: Optional[ModelBackend] = None,
    ):
        self.catalog = catalog or ModelCatalog()
        self.pager = ModelPager(catalog=self.catalog, memory_budget_gb=memory_budget_gb)
        self.scheduler = CognitiveScheduler(catalog=self.catalog, pager=self.pager)
        self.decomposer = TaskDecomposer()
        self.working_set_predictor = CognitiveWorkingSetPredictor(catalog=self.catalog)
        self.confidence_controller = ConfidenceController()
        self.backend = backend or SimulationBackend()

        self._stage_listeners: List[Callable[[StageExecutionResult], None]] = []

    def add_stage_listener(self, listener: Callable[[StageExecutionResult], None]) -> None:
        """Subscribes to live stage completion events."""
        self._stage_listeners.append(listener)

    def _broadcast_stage(self, result: StageExecutionResult) -> None:
        for listener in self._stage_listeners:
            try:
                listener(result)
            except Exception as e:
                print(f"[CognitiveKernel] Listener error: {e}")

    def execute_task(
        self,
        goal: str,
        ablation_mode: AblationMode = AblationMode.D_FULL_MODELVM,
        custom_stages: Optional[List[CognitiveStagePlan]] = None,
    ) -> TaskExecutionSummary:
        """Executes a full cognitive task under the virtual memory architecture."""
        start_time = time.time()
        self.pager.reset()

        # 1. Configure kernel according to ablation mode
        if ablation_mode == AblationMode.A_STATIC_ROUTER:
            # Mode A: Single monolithic model (e.g. general reasoner) handles all steps
            chosen_single = self.catalog.get("general-reasoner") or self.catalog.all_models()[0]
            self.pager.page_in(chosen_single.id)

        elif ablation_mode == AblationMode.C_DYNAMIC_WITH_CSP:
            # Mode C: LRU eviction, no predictive working set
            self.pager.policy = LRUEvictionPolicy()

        else:
            # Mode D: Cost-Aware eviction with predictive working set
            self.pager.policy = CostAwareEvictionPolicy()

        # 2. Task Decomposition
        stages = custom_stages or self.decomposer.decompose(goal)
        current_csp = CognitiveStatePacket(goal=goal, stage_index=0)
        stage_results: List[StageExecutionResult] = []

        # 3. Cognitive Execution Loop
        for i, stage in enumerate(stages):
            stage_start = time.time()
            target_cap = stage.capability

            # Predict Working Set (Future Demand)
            if ablation_mode in (AblationMode.D_FULL_MODELVM,):
                future_caps = self.working_set_predictor.predict_future_capabilities(stages, i)
                future_model_ids = self.working_set_predictor.predict_future_model_ids(stages, i)
            else:
                future_caps = []
                future_model_ids = set()

            # Schedule Model
            breakdowns_data: List[Dict] = []
            if ablation_mode == AblationMode.A_STATIC_ROUTER:
                selected_model = self.catalog.get("general-reasoner") or self.catalog.all_models()[0]
                paging_event = PagingEvent(
                    action=PagingAction.CACHE_HIT,
                    model_id=selected_model.id,
                    ram_gb=selected_model.ram_required,
                    active_memory_gb=self.pager.active_memory_gb,
                    reason="Static resident general model",
                    duration_sec=0.0,
                )
            else:
                selected_model, breakdowns = self.scheduler.select_best_model(
                    target_capability=target_cap,
                    future_capabilities=future_caps,
                    future_model_ids=future_model_ids,
                )
                breakdowns_data = [b.to_dict() for b in breakdowns]

                # Page Model In
                paging_event = self.pager.page_in(
                    model_id=selected_model.id,
                    future_demanded_ids=future_model_ids,
                )

            # Optional Prefetch for Next Step if Spare Memory Exists (Full ModelVM)
            if ablation_mode == AblationMode.D_FULL_MODELVM:
                prefetch_cand = self.working_set_predictor.recommend_prefetch_model(
                    planned_stages=stages,
                    current_stage_index=i,
                    free_memory_gb=self.pager.free_memory_gb,
                    resident_ids=set(self.pager._resident.keys()),
                )
                if prefetch_cand:
                    self.pager.prefetch(prefetch_cand, future_demanded_ids=future_model_ids)

            # Execute Stage on Paged Model
            exec_start = time.time()
            if ablation_mode == AblationMode.B_DYNAMIC_NO_CSP:
                # Mode B: Degrade state packet to unstructured lossy text
                lossy_input = CognitiveStatePacket(goal=goal, stage_index=i)
                # Lost 60% of facts, dropped calculations, lost assumptions
                if current_csp.facts:
                    lossy_input.facts = current_csp.facts[:1]
                stage_output = self.backend.execute_stage(
                    model=selected_model,
                    stage_title=stage.title,
                    stage_description=stage.description,
                    capability=target_cap,
                    input_csp=lossy_input,
                )
            else:
                stage_output = self.backend.execute_stage(
                    model=selected_model,
                    stage_title=stage.title,
                    stage_description=stage.description,
                    capability=target_cap,
                    input_csp=current_csp,
                )
            exec_duration = time.time() - exec_start

            # Merge State Packet
            current_csp.merge_update(stage_output)

            # Confidence Assessment & Escalation Check
            confidence_obj = self.confidence_controller.evaluate_stage_result(
                csp=current_csp,
                executing_model=selected_model,
                target_capability=target_cap,
            )
            escalated = False

            if confidence_obj.escalation_needed and confidence_obj.suggested_model_id:
                # Escalate to higher capacity model
                escalate_id = confidence_obj.suggested_model_id
                esc_model = self.catalog.get(escalate_id)
                if esc_model and esc_model.id != selected_model.id:
                    self.pager.page_in(esc_model.id)
                    esc_output = self.backend.execute_stage(
                        model=esc_model,
                        stage_title=f"[Escalation] {stage.title}",
                        stage_description=f"Resolve uncertainties: {confidence_obj.reason}",
                        capability=target_cap,
                        input_csp=current_csp,
                    )
                    current_csp.merge_update(esc_output)
                    selected_model = esc_model
                    escalated = True

            total_stage_time = time.time() - stage_start

            stage_res = StageExecutionResult(
                stage_index=i,
                stage_title=stage.title,
                capability=target_cap,
                model_id=selected_model.id,
                model_name=selected_model.name,
                model_ram_gb=selected_model.ram_required,
                paging_action=paging_event.action,
                paging_duration_sec=paging_event.duration_sec,
                execution_duration_sec=exec_duration,
                total_stage_duration_sec=total_stage_time,
                active_memory_gb=self.pager.active_memory_gb,
                confidence_score=confidence_obj.confidence_score,
                escalated=escalated,
                csp_snapshot=current_csp.to_dict(),
                score_breakdowns=breakdowns_data,
            )
            stage_results.append(stage_res)
            self._broadcast_stage(stage_res)

        total_duration = time.time() - start_time
        total_library_size = self.catalog.total_library_size_gb()
        peak_memory = self.pager.peak_memory_gb

        # Compute PDR Section 12 Headline Metrics
        memory_savings = (
            round(1.0 - (peak_memory / total_library_size), 3)
            if total_library_size > 0
            else 0.0
        )
        capability_density = (
            round(len(stages) / max(0.1, peak_memory), 3)
        )

        hit_rate = (
            round(self.pager.cache_hits / (self.pager.cache_hits + self.pager.cache_misses), 3)
            if (self.pager.cache_hits + self.pager.cache_misses) > 0
            else 0.0
        )

        return TaskExecutionSummary(
            task_goal=goal,
            ablation_mode=ablation_mode,
            status=TaskStatus.COMPLETED,
            total_stages=len(stages),
            peak_resident_memory_gb=peak_memory,
            memory_budget_gb=self.pager.memory_budget_gb,
            total_library_size_gb=total_library_size,
            memory_savings_ratio=memory_savings,
            capability_density=capability_density,
            total_duration_sec=round(total_duration, 3),
            total_paging_time_sec=round(self.pager.total_paging_time_sec, 3),
            total_execution_time_sec=round(total_duration - self.pager.total_paging_time_sec, 3),
            cache_hit_rate=hit_rate,
            stage_results=stage_results,
            final_csp=current_csp.to_dict(),
        )
