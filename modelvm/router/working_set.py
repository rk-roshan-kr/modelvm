"""Predictive Cognitive Working Set.

Analogous to an OS working-set model, predicts upcoming required capabilities
and models to optimize caching, eviction protection, and prefetching.
Uses the unified multi-objective model ranking policy from CognitiveScheduler.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
from modelvm.core.manifest import ModelManifest
from modelvm.core.types import Capability
from modelvm.registry.catalog import ModelCatalog
from modelvm.router.task_decomposer import CognitiveStagePlan


class CognitiveWorkingSetPredictor:
    """Predicts future cognitive working sets across multi-stage execution."""

    def __init__(
        self,
        catalog: ModelCatalog,
        lookahead_window: int = 3,
        scheduler: Optional[Any] = None,
    ):
        self.catalog = catalog
        # Canonical operating lookahead horizon k=3
        self.lookahead_window = max(1, min(lookahead_window, 10))
        self.scheduler = scheduler

    def set_scheduler(self, scheduler: Any) -> None:
        """Connects the scheduler for unified model ranking."""
        self.scheduler = scheduler

    def predict_future_capabilities(
        self,
        planned_stages: List[CognitiveStagePlan],
        current_stage_index: int,
    ) -> List[Capability]:
        """Returns the sequence of upcoming capabilities within the lookahead window."""
        future_stages = planned_stages[current_stage_index + 1 : current_stage_index + 1 + self.lookahead_window]
        return [s.capability for s in future_stages]

    def predict_future_capabilities_weighted(
        self,
        planned_stages: List[CognitiveStagePlan],
        current_stage_index: int,
    ) -> List[Tuple[Capability, float]]:
        """Returns upcoming capabilities paired with distance decay weights."""
        future_stages = planned_stages[current_stage_index + 1 : current_stage_index + 1 + self.lookahead_window]
        return [(s.capability, max(0.1, 1.0 - (0.2 * i))) for i, s in enumerate(future_stages)]

    def predict_future_model_ids(
        self,
        planned_stages: List[CognitiveStagePlan],
        current_stage_index: int,
    ) -> Set[str]:
        """Identifies model IDs likely to be needed in the next k stages using unified scheduler ranking."""
        future_caps = self.predict_future_capabilities(planned_stages, current_stage_index)
        needed_model_ids: Set[str] = set()

        for cap in future_caps:
            if self.scheduler:
                ranked = self.scheduler.rank_models_for_capability(cap)
                if ranked:
                    needed_model_ids.add(ranked[0][0].id)
            else:
                candidates = self.catalog.get_by_capability(cap)
                if candidates:
                    needed_model_ids.add(candidates[0].id)

        return needed_model_ids

    def recommend_prefetch_model(
        self,
        planned_stages: List[CognitiveStagePlan],
        current_stage_index: int,
        free_memory_gb: float,
        resident_ids: Set[str],
        memory_budget_gb: float = 8.0,
        lambda_memory_cost: float = 1.0,  # Latency-equivalent seconds per 100% budget consumption
        mu_energy_cost: float = 0.5,      # Latency-equivalent seconds for energy overhead
    ) -> Optional[str]:
        """Prefetch utility: U_prefetch = P(future) * Delta_L_avoided - lambda * M_cost - mu * E_prefetch.
        
        Calculates expected latency savings in seconds vs memory & energy costs,
        ensuring all terms have consistent dimensional units (seconds).
        """
        if self.lookahead_window <= 1:
            return None
        future_stages = planned_stages[current_stage_index + 1 : current_stage_index + 1 + self.lookahead_window]
        budget = max(1.0, memory_budget_gb)
        prefetch_utilities: Dict[str, float] = {}

        for j, stage in enumerate(future_stages, start=1):
            if self.scheduler:
                ranked = self.scheduler.rank_models_for_capability(stage.capability)
                candidates: List[ModelManifest] = [item[0] for item in ranked]
            else:
                candidates = self.catalog.get_by_capability(stage.capability)

            if not candidates:
                continue
            best_cand = candidates[0]

            if best_cand.id not in resident_ids:
                if best_cand.ram_required <= free_memory_gb:
                    # Distance-based future demand probability (j=1 -> 1.0)
                    future_prob = max(0.1, 1.0 - (0.2 * (j - 1)))
                    # Avoided latency is cold page-in time
                    delta_l_avoided = best_cand.load_time
                    # Normalized memory cost
                    m_cost = best_cand.ram_required / budget
                    # Normalized energy cost
                    param_norm = min(1.0, best_cand.parameters_billion / 32.0)
                    e_cost = param_norm * best_cand.energy_cost_factor

                    # Dimensionally consistent utility in seconds
                    utility = (future_prob * delta_l_avoided) - (lambda_memory_cost * m_cost) - (mu_energy_cost * e_cost)

                    # Positive utility admission gate
                    if utility > 0.0:
                        if best_cand.id not in prefetch_utilities or utility > prefetch_utilities[best_cand.id]:
                            prefetch_utilities[best_cand.id] = utility

        if prefetch_utilities:
            best_model_id = max(prefetch_utilities, key=prefetch_utilities.get)
            return best_model_id

        return None
