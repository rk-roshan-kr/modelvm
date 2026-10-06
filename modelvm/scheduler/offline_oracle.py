"""Offline Prescient Oracle: Exact finite-state dynamic programming comparator.

Provides a mathematically optimal offline oracle over (stage_index, resident_model_subset)
that accounts for variable-size model footprints and cold-load latencies under an arbitrary
memory budget (B_RAM).
"""

from __future__ import annotations
import itertools
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple, Union
from pydantic import BaseModel, Field

from modelvm.core.manifest import ModelManifest
from modelvm.core.types import Capability
from modelvm.registry.catalog import ModelCatalog
from modelvm.router.task_decomposer import CognitiveStagePlan


class OracleScheduleResult(BaseModel):
    """Result of exact dynamic programming offline oracle execution."""
    cost_oracle: float
    paging_time_sec: float
    execution_time_sec: float
    total_reloads: int
    optimal_sequence: List[str]
    resident_history: List[List[str]]
    stage_breakdown: List[Dict[str, Any]] = Field(default_factory=list)


def find_feasible_resident_subsets(
    catalog: ModelCatalog,
    memory_budget_gb: float = 8.0,
) -> List[FrozenSet[str]]:
    """Enumerate all feasible resident model subsets R with sum(ram) <= memory_budget_gb."""
    models = catalog.all_models()
    feasible: List[FrozenSet[str]] = []
    for r in range(len(models) + 1):
        for comb in itertools.combinations(models, r):
            if sum(m.ram_required for m in comb) <= memory_budget_gb:
                feasible.append(frozenset(m.id for m in comb))
    return feasible


def solve_exact_dp_oracle(
    stages: Union[List[CognitiveStagePlan], List[Capability], List[str]],
    catalog: ModelCatalog,
    memory_budget_gb: float = 8.0,
    base_tokens: float = 115.0,
    min_capability_score: float = 0.70,
) -> OracleScheduleResult:
    """Computes the exact globally optimal prescient schedule via finite-state dynamic programming.

    State space at each stage t is the set of feasible resident model subsets R (under memory_budget_gb).
    Transition cost from R_prev to R_curr when executing stage t on capable model m in R_curr:
        TransitionCost = sum_{mid in R_curr \\ R_prev} load_time(mid) + latency(m) * base_tokens

    This is an exact global optimum over both routing decisions and variable-size caching.
    """
    models = {m.id: m for m in catalog.all_models()}
    feasible_sets = find_feasible_resident_subsets(catalog, memory_budget_gb=memory_budget_gb)

    # Normalize stage capabilities
    norm_caps: List[Capability] = []
    for s in stages:
        if isinstance(s, CognitiveStagePlan):
            norm_caps.append(s.capability)
        elif isinstance(s, Capability):
            norm_caps.append(s)
        else:
            norm_caps.append(Capability(str(s)))

    # DP table: dp[R] = (min_cost, paging_time, exec_time, reloads, seen_models, path)
    # path is list of (model_id, R_curr, paging_cost, exec_cost)
    dp: Dict[FrozenSet[str], Tuple[float, float, float, int, FrozenSet[str], List[Tuple[str, FrozenSet[str], float, float]]]] = {
        frozenset(): (0.0, 0.0, 0.0, 0, frozenset(), [])
    }

    for t, cap in enumerate(norm_caps):
        capable_models = [m for m in models.values() if m.capability_score(cap) >= min_capability_score]
        if not capable_models:
            # Fallback to all models if none meet the strict capability threshold
            capable_models = list(models.values())

        new_dp: Dict[FrozenSet[str], Tuple[float, float, float, int, FrozenSet[str], List[Tuple[str, FrozenSet[str], float, float]]]] = {}

        for R_prev, (prev_cost, prev_page, prev_exec, prev_rel, prev_seen, prev_path) in dp.items():
            for R_curr in feasible_sets:
                for m in capable_models:
                    if m.id in R_curr:
                        new_models = R_curr - R_prev
                        p_cost = sum(models[mid].load_time for mid in new_models)
                        e_cost = round(m.latency * base_tokens, 3)
                        tot_cost = round(prev_cost + p_cost + e_cost, 3)
                        tot_page = round(prev_page + p_cost, 3)
                        tot_exec = round(prev_exec + e_cost, 3)
                        reloads = prev_rel + sum(1 for mid in new_models if mid in prev_seen)
                        new_seen = prev_seen | new_models

                        if R_curr not in new_dp or tot_cost < new_dp[R_curr][0]:
                            step_record = (m.id, R_curr, p_cost, e_cost)
                            new_dp[R_curr] = (tot_cost, tot_page, tot_exec, reloads, new_seen, prev_path + [step_record])

        dp = new_dp

    best_R = min(dp, key=lambda r: dp[r][0])
    cost, page, exe, rel, seen, path = dp[best_R]

    breakdown = []
    optimal_seq = []
    res_hist = []
    for step_idx, (mid, r_set, p_c, e_c) in enumerate(path):
        optimal_seq.append(mid)
        res_hist.append(sorted(list(r_set)))
        breakdown.append({
            "stage_index": step_idx,
            "executing_model": mid,
            "resident_models": sorted(list(r_set)),
            "paging_cost_sec": p_c,
            "exec_cost_sec": e_c,
            "total_step_cost_sec": round(p_c + e_c, 3),
        })

    return OracleScheduleResult(
        cost_oracle=cost,
        paging_time_sec=page,
        execution_time_sec=exe,
        total_reloads=rel,
        optimal_sequence=optimal_seq,
        resident_history=res_hist,
        stage_breakdown=breakdown,
    )


def evaluate_sequence_cost(
    stages: Union[List[CognitiveStagePlan], List[Capability], List[str]],
    model_sequence: List[str],
    catalog: ModelCatalog,
    memory_budget_gb: float = 8.0,
    base_tokens: float = 115.0,
    policy: str = "lru",
) -> Dict[str, Union[float, int, List[str]]]:
    """Evaluates the model-based cost of an explicit model routing sequence under LRU caching."""
    models = {m.id: m for m in catalog.all_models()}
    resident: List[str] = []
    tot_page = 0.0
    tot_exec = 0.0
    reloads = 0
    seen: Set[str] = set()

    for mid in model_sequence:
        m = models[mid]
        tot_exec += round(m.latency * base_tokens, 3)
        if mid in resident:
            # Hit: update access timestamp (move to end)
            resident.remove(mid)
            resident.append(mid)
        else:
            # Miss
            if mid in seen:
                reloads += 1
            seen.add(mid)
            # Evict until fits
            while sum(models[x].ram_required for x in resident) + m.ram_required > memory_budget_gb:
                resident.pop(0)  # Evict oldest
            resident.append(mid)
            tot_page += m.load_time

    tot_page = round(tot_page, 3)
    tot_exec = round(tot_exec, 3)
    total_cost = round(tot_page + tot_exec, 3)

    return {
        "cost": total_cost,
        "paging_time_sec": tot_page,
        "execution_time_sec": tot_exec,
        "reloads": reloads,
        "sequence": list(model_sequence),
    }
