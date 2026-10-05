"""Cognitive Kernel: Central runtime orchestrating paging, scheduling, and execution."""

from __future__ import annotations
import time
from typing import Any, Callable, Dict, List, Optional, Set, Union
from pydantic import BaseModel, Field

from modelvm.core.manifest import ModelManifest
from modelvm.core.state_packet import CognitiveStatePacket
from modelvm.core.types import AblationMode, Capability, FactorialConfig, PagingAction, PagingEvent, TaskStatus
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
    ablation_mode: Union[AblationMode, FactorialConfig, str]
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
        lookahead_k: int = 3,
        pager: Optional[ModelPager] = None,
    ):
        if pager is not None:
            self.pager = pager
            self.catalog = pager.catalog
        else:
            self.catalog = catalog or ModelCatalog()
            self.pager = ModelPager(catalog=self.catalog, memory_budget_gb=memory_budget_gb)
        self.scheduler = CognitiveScheduler(catalog=self.catalog, pager=self.pager)
        self.decomposer = TaskDecomposer()
        self.working_set_predictor = CognitiveWorkingSetPredictor(
            catalog=self.catalog, lookahead_window=lookahead_k, scheduler=self.scheduler
        )
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

    def execute_factorial_task(
        self,
        goal: str,
        config: FactorialConfig,
        custom_stages: Optional[List[CognitiveStagePlan]] = None,
    ) -> TaskExecutionSummary:
        """Executes a cognitive task under an explicit configuration of the 2^3 factorial matrix."""
        is_monolith = (config == FactorialConfig.REF_STATIC_MONOLITH)
        use_csp = config in (
            FactorialConfig.C1_CSP,
            FactorialConfig.C4_CSP_WS,
            FactorialConfig.C5_CSP_SCHEDULER,
            FactorialConfig.C7_FULL_MODELVM,
        )
        use_ws = config in (
            FactorialConfig.C2_WS,
            FactorialConfig.C4_CSP_WS,
            FactorialConfig.C6_WS_SCHEDULER,
            FactorialConfig.C7_FULL_MODELVM,
        )
        use_scheduler = config in (
            FactorialConfig.C3_SCHEDULER,
            FactorialConfig.C5_CSP_SCHEDULER,
            FactorialConfig.C6_WS_SCHEDULER,
            FactorialConfig.C7_FULL_MODELVM,
        )
        return self._execute_configured_task(
            goal=goal,
            config_id=config,
            is_monolith=is_monolith,
            use_csp=use_csp,
            use_ws=use_ws,
            use_scheduler=use_scheduler,
            custom_stages=custom_stages,
        )

    def execute_task(
        self,
        goal: str,
        ablation_mode: AblationMode = AblationMode.D_FULL_MODELVM,
        custom_stages: Optional[List[CognitiveStagePlan]] = None,
    ) -> TaskExecutionSummary:
        """Executes a full cognitive task under the virtual memory architecture."""
        is_monolith = (ablation_mode == AblationMode.A_STATIC_ROUTER)
        use_csp = (ablation_mode in (AblationMode.C_DYNAMIC_WITH_CSP, AblationMode.D_FULL_MODELVM))
        use_ws = (ablation_mode == AblationMode.D_FULL_MODELVM)
        use_scheduler = (ablation_mode in (AblationMode.C_DYNAMIC_WITH_CSP, AblationMode.D_FULL_MODELVM))

        return self._execute_configured_task(
            goal=goal,
            config_id=ablation_mode,
            is_monolith=is_monolith,
            use_csp=use_csp,
            use_ws=use_ws,
            use_scheduler=use_scheduler,
            custom_stages=custom_stages,
        )

    def _execute_configured_task(
        self,
        goal: str,
        config_id: Union[AblationMode, FactorialConfig, str],
        is_monolith: bool,
        use_csp: bool,
        use_ws: bool,
        use_scheduler: bool,
        custom_stages: Optional[List[CognitiveStagePlan]] = None,
    ) -> TaskExecutionSummary:
        start_time = time.time()
        self.pager.reset()

        # 1. Configure paging policy
        if is_monolith:
            chosen_single = self.catalog.get("general-reasoner") or self.catalog.all_models()[0]
            self.pager.page_in(chosen_single.id)
            self.pager.policy = LRUEvictionPolicy()
        elif use_ws:
            self.pager.policy = CostAwareEvictionPolicy()
        else:
            self.pager.policy = LRUEvictionPolicy()

        # 2. Task Decomposition
        stages = custom_stages or self.decomposer.decompose(goal)
        current_csp = CognitiveStatePacket(goal=goal, stage_index=0)
        stage_results: List[StageExecutionResult] = []
        escalation_count = 0

        # 3. Cognitive Execution Loop
        for i, stage in enumerate(stages):
            stage_start = time.time()
            target_cap = stage.capability

            # Predict Working Set (Future Demand)
            if use_ws and not is_monolith:
                future_caps = self.working_set_predictor.predict_future_capabilities(stages, i)
                future_model_ids = self.working_set_predictor.predict_future_model_ids(stages, i)
            else:
                future_caps = []
                future_model_ids = set()

            # Schedule / Select Model
            breakdowns_data: List[Dict] = []
            if is_monolith:
                selected_model = self.catalog.get("general-reasoner") or self.catalog.all_models()[0]
                paging_event = PagingEvent(
                    action=PagingAction.CACHE_HIT,
                    model_id=selected_model.id,
                    ram_gb=selected_model.ram_required,
                    active_memory_gb=self.pager.active_memory_gb,
                    reason="Static resident general model",
                    duration_sec=0.0,
                )
            elif use_scheduler:
                selected_model, breakdowns = self.scheduler.select_best_model(
                    target_capability=target_cap,
                    future_capabilities=future_caps,
                    future_model_ids=future_model_ids,
                )
                breakdowns_data = [b.to_dict() for b in breakdowns]
                paging_event = self.pager.page_in(
                    model_id=selected_model.id,
                    future_demanded_ids=future_model_ids,
                )
            else:
                # Greedy first-fit model selection
                matches = self.catalog.get_by_capability(target_cap)
                selected_model = matches[0] if matches else (self.catalog.get("general-reasoner") or self.catalog.all_models()[0])
                paging_event = self.pager.page_in(
                    model_id=selected_model.id,
                    future_demanded_ids=future_model_ids,
                )

            # Optional Prefetch for Next Step if Spare Memory Exists with Safety Margin
            if use_ws and not is_monolith:
                prefetch_cand = self.working_set_predictor.recommend_prefetch_model(
                    planned_stages=stages,
                    current_stage_index=i,
                    free_memory_gb=self.pager.free_memory_gb,
                    resident_ids=set(self.pager._resident.keys()),
                    memory_budget_gb=self.pager.memory_budget_gb,
                )
                if prefetch_cand:
                    model = self.catalog.get(prefetch_cand)
                    # Safety margin: only prefetch if it leaves >= 1.0 GB free memory buffer
                    if model and (self.pager.free_memory_gb - model.ram_required) >= 1.0:
                        self.pager.prefetch(prefetch_cand, future_demanded_ids=future_model_ids)

            # Execute Stage on Model
            exec_start = time.time()
            if not use_csp:
                # Without CSP: Degrade state to lossy unstructured window
                lossy_input = CognitiveStatePacket(goal=goal, stage_index=i)
                if current_csp.facts:
                    lossy_input.facts = current_csp.facts[-1:]
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
            if not use_csp:
                current_csp = CognitiveStatePacket(
                    goal=goal,
                    stage_index=i + 1,
                    current_capability=target_cap.value,
                    facts=list(set(current_csp.facts[-1:] + stage_output.facts)),
                    calculations=stage_output.calculations,
                    evidence=stage_output.evidence,
                    artifacts={**current_csp.artifacts, **stage_output.artifacts},
                    history_trace=current_csp.history_trace + stage_output.history_trace,
                )
            else:
                current_csp.merge_update(stage_output)

            # Confidence Assessment & Escalation Check with Loop Protection
            confidence_obj = self.confidence_controller.evaluate_stage_result(
                csp=current_csp,
                executing_model=selected_model,
                target_capability=target_cap,
            )
            escalated = False
            max_escalations_per_stage = 2
            while (
                use_csp
                and use_scheduler
                and not is_monolith
                and confidence_obj.escalation_needed
                and escalation_count < max_escalations_per_stage
            ):
                escalation_count += 1
                curr_quality = selected_model.capability_score(target_cap) * selected_model.quality
                epsilon = 0.02

                qualifying_candidates = [
                    m for m in self.catalog.all_models()
                    if m.id != selected_model.id
                    and m.ram_required <= self.pager.memory_budget_gb
                    and ((m.capability_score(target_cap) * m.quality) - curr_quality) >= epsilon
                ]

                if qualifying_candidates:
                    esc_model, esc_breakdowns = self.scheduler.select_best_model(
                        target_capability=target_cap,
                        future_capabilities=future_caps,
                        future_model_ids=future_model_ids,
                        candidate_models=qualifying_candidates,
                    )
                elif confidence_obj.suggested_model_id:
                    esc_model = self.catalog.get(confidence_obj.suggested_model_id)
                else:
                    esc_model = None

                if esc_model and esc_model.id != selected_model.id:
                    self.pager.page_in(esc_model.id, future_demanded_ids=future_model_ids)
                    esc_output = self.backend.execute_stage(
                        model=esc_model,
                        stage_title=f"[Escalation {escalation_count}] {stage.title}",
                        stage_description=f"Resolve uncertainties: {confidence_obj.reason}",
                        capability=target_cap,
                        input_csp=current_csp,
                    )
                    current_csp.merge_update(esc_output)
                    selected_model = esc_model
                    escalated = True

                    confidence_obj = self.confidence_controller.evaluate_stage_result(
                        csp=current_csp,
                        executing_model=selected_model,
                        target_capability=target_cap,
                    )
                else:
                    break

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
            ablation_mode=config_id,
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
