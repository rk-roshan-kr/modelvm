"""Predictive Cognitive Working Set.

Analogous to an OS working-set model, predicts upcoming required capabilities
and models to optimize caching, eviction protection, and prefetching.
"""

from __future__ import annotations
from typing import List, Optional, Set
from modelvm.core.types import Capability
from modelvm.registry.catalog import ModelCatalog
from modelvm.router.task_decomposer import CognitiveStagePlan


class CognitiveWorkingSetPredictor:
    """Predicts future cognitive working sets across multi-stage execution."""

    def __init__(self, catalog: ModelCatalog, lookahead_window: int = 2):
        self.catalog = catalog
        self.lookahead_window = lookahead_window

    def predict_future_capabilities(
        self,
        planned_stages: List[CognitiveStagePlan],
        current_stage_index: int,
    ) -> List[Capability]:
        """Returns the sequence of upcoming capabilities within the lookahead window."""
        future_stages = planned_stages[current_stage_index + 1 : current_stage_index + 1 + self.lookahead_window]
        return [s.capability for s in future_stages]

    def predict_future_model_ids(
        self,
        planned_stages: List[CognitiveStagePlan],
        current_stage_index: int,
    ) -> Set[str]:
        """Identifies model IDs likely to be needed in the next k stages."""
        future_caps = self.predict_future_capabilities(planned_stages, current_stage_index)
        needed_model_ids: Set[str] = set()

        for cap in future_caps:
            candidates = self.catalog.get_by_capability(cap)
            if candidates:
                # Top candidate for this capability
                needed_model_ids.add(candidates[0].id)

        return needed_model_ids

    def recommend_prefetch_model(
        self,
        planned_stages: List[CognitiveStagePlan],
        current_stage_index: int,
        free_memory_gb: float,
        resident_ids: Set[str],
    ) -> Optional[str]:
        """Suggests a model to prefetch if spare RAM is available without forcing eviction."""
        future_model_ids = self.predict_future_model_ids(planned_stages, current_stage_index)
        for model_id in future_model_ids:
            if model_id not in resident_ids:
                model = self.catalog.get(model_id)
                if model and model.ram_required <= free_memory_gb:
                    return model_id
        return None
