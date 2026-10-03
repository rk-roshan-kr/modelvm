"""Resource-Aware Cognitive Scheduler.

Implements the multi-objective scheduling objective defined in PDR Section 10:
Score(m) = F_capability - α M_cost - β L_load - γ E_energy - δ E_eviction + η F_future
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from modelvm.core.manifest import ModelManifest
from modelvm.core.types import Capability
from modelvm.pager.memory_manager import ModelPager
from modelvm.registry.catalog import ModelCatalog


@dataclass
class SchedulingScoreBreakdown:
    """Detailed mathematical breakdown of a candidate model's score."""
    model_id: str
    model_name: str
    total_score: float
    f_capability: float      # Task fit
    m_cost: float            # Normalized memory footprint
    l_load: float            # Loading latency
    e_energy: float          # Energy / computation factor
    e_eviction: float        # Eviction penalty
    f_future: float          # Future demand bonus
    is_resident: bool        # Whether model is already loaded in RAM
    ram_required: float

    def to_dict(self) -> Dict:
        return {
            "model_id": self.model_id,
            "model_name": self.model_name,
            "total_score": round(self.total_score, 4),
            "f_capability": round(self.f_capability, 4),
            "m_cost": round(self.m_cost, 4),
            "l_load": round(self.l_load, 4),
            "e_energy": round(self.e_energy, 4),
            "e_eviction": round(self.e_eviction, 4),
            "f_future": round(self.f_future, 4),
            "is_resident": self.is_resident,
            "ram_required": self.ram_required,
        }


class CognitiveScheduler:
    """Multi-objective scheduler balancing capability, memory footprint, loading costs, and future working sets."""

    def __init__(
        self,
        catalog: ModelCatalog,
        pager: ModelPager,
        alpha: float = 0.20,   # Memory cost weight
        beta: float = 0.25,    # Load latency weight
        gamma: float = 0.10,   # Energy cost weight
        delta: float = 0.30,   # Eviction cost weight
        eta: float = 0.35,     # Future demand bonus weight
    ):
        self.catalog = catalog
        self.pager = pager
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.eta = eta

    def compute_score(
        self,
        model: ModelManifest,
        target_capability: Capability,
        future_capabilities: Optional[List[Capability]] = None,
        future_model_ids: Optional[Set[str]] = None,
    ) -> SchedulingScoreBreakdown:
        """Evaluates Score(m) for a single candidate model."""
        # 1. Capability Fit F_capability
        base_match = model.capability_score(target_capability)
        f_cap = base_match * model.quality

        # 2. Memory Cost M_cost (normalized by active budget)
        budget = max(1.0, self.pager.memory_budget_gb)
        m_cost = min(1.0, model.ram_required / budget)

        # 3. Loading Latency L_load
        is_resident = self.pager.is_resident(model.id)
        if is_resident:
            # Cache hit: 0 loading time!
            l_load = 0.0
        else:
            # Normalized against a nominal 5-second cold-load
            l_load = min(1.0, model.load_time / 5.0)

        # 4. Energy Cost E_energy
        # Estimated based on model size, quantization, and architecture factor
        param_factor = min(1.0, model.parameters_billion / 32.0)
        e_energy = param_factor * model.energy_cost_factor

        # 5. Eviction Cost E_eviction
        # If model is already resident, eviction penalty is zero.
        # If loading this model forces evicting currently resident models, calculate penalty.
        e_eviction = 0.0
        if not is_resident:
            free_ram = self.pager.free_memory_gb
            if free_ram < model.ram_required:
                deficit = model.ram_required - free_ram
                # Penalty scales with deficit and whether resident models are needed later
                resident_future_clash = False
                if future_model_ids:
                    for res_id in self.pager._resident.keys():
                        if res_id in future_model_ids:
                            resident_future_clash = True
                            break
                eviction_base = min(1.0, deficit / budget)
                e_eviction = eviction_base * (1.8 if resident_future_clash else 1.0)

        # 6. Future Demand F_future
        # If the model satisfies capabilities needed in subsequent stages
        f_future = 0.0
        future_caps = future_capabilities or []
        for next_cap in future_caps:
            if model.capability_score(next_cap) >= 0.7:
                f_future += 0.5
        if future_model_ids and model.id in future_model_ids:
            f_future += 0.5
        f_future = min(1.0, f_future)

        # Total multi-objective score
        total_score = (
            f_cap
            - (self.alpha * m_cost)
            - (self.beta * l_load)
            - (self.gamma * e_energy)
            - (self.delta * e_eviction)
            + (self.eta * f_future)
        )

        return SchedulingScoreBreakdown(
            model_id=model.id,
            model_name=model.name,
            total_score=total_score,
            f_capability=f_cap,
            m_cost=m_cost,
            l_load=l_load,
            e_energy=e_energy,
            e_eviction=e_eviction,
            f_future=f_future,
            is_resident=is_resident,
            ram_required=model.ram_required,
        )

    def select_best_model(
        self,
        target_capability: Capability,
        future_capabilities: Optional[List[Capability]] = None,
        future_model_ids: Optional[Set[str]] = None,
        candidate_models: Optional[List[ModelManifest]] = None,
    ) -> Tuple[ModelManifest, List[SchedulingScoreBreakdown]]:
        """Evaluates all candidate models and returns the highest-scoring model and all score breakdowns."""
        all_candidates = candidate_models or self.catalog.all_models()
        # Filter candidate models that fit within the memory budget
        budget = self.pager.memory_budget_gb
        models = [m for m in all_candidates if m.ram_required <= budget]
        if not models:
            models = sorted(all_candidates, key=lambda m: m.ram_required)
            if not models:
                raise RuntimeError("No models registered in catalog")

        breakdowns: List[SchedulingScoreBreakdown] = []
        for model in models:
            score_obj = self.compute_score(
                model=model,
                target_capability=target_capability,
                future_capabilities=future_capabilities,
                future_model_ids=future_model_ids,
            )
            breakdowns.append(score_obj)

        # Sort descending by total score
        breakdowns.sort(key=lambda s: s.total_score, reverse=True)
        winner_id = breakdowns[0].model_id
        winner_model = self.catalog.get(winner_id)
        if not winner_model:
            winner_model = models[0]

        return winner_model, breakdowns
