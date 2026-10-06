#!/usr/bin/env python3
"""scripts/run_r3_workload_sweeps.py: Reproduces EXP-R3 Workload Generalization Sweeps.

Evaluates scheduler generalization across divergent workload distributions reported in Section 9.3:
- W_A (Research-Heavy): Research -> Research -> Synthesis -> Research -> Physics
- W_B (Compute-Heavy):  Math -> Coding -> Math -> Physics -> Math
- W_C (Coding-Heavy):   Coding -> Coding -> Research -> Coding -> Synthesis
- W_D (Mixed Balanced): Research -> Math -> Coding -> Physics -> Synthesis

Policies evaluated:
1. Capability-Greedy Selection
2. Memory-Aware Greedy Selection
3. ModelVM Multi-Objective Scheduler
4. Exact Finite-State Dynamic Programming Oracle (modelvm.scheduler.offline_oracle)

Outputs:
- docs/r3_workload_generalization_results.json
- docs/r3_trials.csv
"""

from __future__ import annotations
import csv
import json
import os
import random
import sys
from typing import Dict, List, Tuple
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modelvm.core.types import Capability
from modelvm.pager.memory_manager import ModelPager
from modelvm.pager.policy import CostAwareEvictionPolicy, LRUEvictionPolicy
from modelvm.registry.catalog import ModelCatalog
from modelvm.router.task_decomposer import CognitiveStagePlan
from modelvm.router.working_set import CognitiveWorkingSetPredictor
from modelvm.scheduler.cognitive_scheduler import CognitiveScheduler
from modelvm.scheduler.offline_oracle import solve_exact_dp_oracle

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

WORKLOADS = {
    "W_A": {
        "title": "Research-Heavy",
        "description": "Literature -> Literature -> Synthesis -> Literature -> Physics",
        "stages": [
            Capability.RESEARCH,
            Capability.RESEARCH,
            Capability.GENERAL,
            Capability.RESEARCH,
            Capability.PHYSICS,
        ],
    },
    "W_B": {
        "title": "Compute-Heavy",
        "description": "Math -> Coding -> Math -> Physics -> Math",
        "stages": [
            Capability.MATHEMATICS,
            Capability.CODING,
            Capability.MATHEMATICS,
            Capability.PHYSICS,
            Capability.MATHEMATICS,
        ],
    },
    "W_C": {
        "title": "Coding-Heavy",
        "description": "Coding -> Coding -> Research -> Coding -> Synthesis",
        "stages": [
            Capability.CODING,
            Capability.CODING,
            Capability.RESEARCH,
            Capability.CODING,
            Capability.GENERAL,
        ],
    },
    "W_D": {
        "title": "Mixed Balanced",
        "description": "Research -> Math -> Coding -> Physics -> Synthesis",
        "stages": [
            Capability.RESEARCH,
            Capability.MATHEMATICS,
            Capability.CODING,
            Capability.PHYSICS,
            Capability.GENERAL,
        ],
    },
}

POLICIES = [
    "Capability-Greedy",
    "Memory-Aware Greedy",
    "ModelVM Scheduler",
    "Offline Oracle",
]


def bootstrap_ci(data: List[float], num_resamples: int = 2000) -> Tuple[float, float]:
    """Computes empirical non-parametric bootstrap 95% percentile confidence interval."""
    if len(data) == 0:
        return (0.0, 0.0)
    resamples = [float(np.mean(np.random.choice(data, size=len(data), replace=True))) for _ in range(num_resamples)]
    return (round(float(np.percentile(resamples, 2.5)), 3), round(float(np.percentile(resamples, 97.5)), 3))


def run_r3_sweeps(num_trials_per_cell: int = 10, docs_dir: str = "docs"):
    catalog = ModelCatalog()
    all_trials_records = []
    aggregated_results = {}

    for w_key, w_info in WORKLOADS.items():
        w_title = w_info["title"]
        stages = w_info["stages"]

        # 1. Compute exact offline prescient oracle schedule
        oracle_res = solve_exact_dp_oracle(stages, catalog, memory_budget_gb=8.0, base_tokens=115.0)
        cost_oracle = oracle_res.cost_oracle

        aggregated_results[w_key] = {
            "workload_key": w_key,
            "title": w_title,
            "description": w_info["description"],
            "oracle_cost_sec": cost_oracle,
            "oracle_optimal_sequence": oracle_res.optimal_sequence,
            "policies": {},
        }

        stage_plans = [
            CognitiveStagePlan(stage_index=i, title=f"Stage_{i}", description=f"Stage {i} execution", capability=c)
            for i, c in enumerate(stages)
        ]

        for policy_name in POLICIES:
            trial_gp: List[float] = []
            trial_q: List[float] = []
            trial_page: List[float] = []
            trial_rel: List[float] = []
            trial_dur: List[float] = []
            trial_reg: List[float] = []

            for trial_idx in range(1, num_trials_per_cell + 1):
                is_mvm = "ModelVM" in policy_name
                is_oracle = "Oracle" in policy_name

                pager = ModelPager(
                    catalog=catalog,
                    memory_budget_gb=8.0,
                    policy=CostAwareEvictionPolicy() if is_mvm else LRUEvictionPolicy(),
                )
                scheduler = CognitiveScheduler(catalog=catalog, pager=pager)
                predictor = CognitiveWorkingSetPredictor(catalog=catalog, lookahead_window=3, scheduler=scheduler)

                tot_page = 0.0
                tot_exec = 0.0
                quals: List[float] = []
                selected_sequence: List[str] = []

                for i, s in enumerate(stage_plans):
                    cap = s.capability

                    if policy_name == "Capability-Greedy":
                        cands = sorted(
                            catalog.all_models(),
                            key=lambda m: (m.capability_score(cap), m.parameters_billion),
                            reverse=True,
                        )
                        model = cands[0]
                        pe = pager.page_in(model.id)
                    elif policy_name == "Memory-Aware Greedy":
                        res_cands = [
                            catalog.get(mid)
                            for mid in pager._resident
                            if catalog.get(mid) and catalog.get(mid).capability_score(cap) >= 0.70
                        ]
                        if res_cands:
                            model = max(res_cands, key=lambda x: x.capability_score(cap))
                        else:
                            qual_cands = [m for m in catalog.all_models() if m.capability_score(cap) >= 0.70]
                            model = min(qual_cands, key=lambda x: x.ram_required) if qual_cands else catalog.all_models()[0]
                        pe = pager.page_in(model.id)
                    elif policy_name == "ModelVM Scheduler":
                        future_caps = predictor.predict_future_capabilities(stage_plans, i)
                        future_model_ids = predictor.predict_future_model_ids(stage_plans, i)
                        model, _ = scheduler.select_best_model(
                            cap, future_capabilities=future_caps, future_model_ids=future_model_ids
                        )
                        pe = pager.page_in(model.id, future_demanded_ids=future_model_ids)

                        # Predictive prefetch if headroom permits
                        cand = predictor.recommend_prefetch_model(
                            stage_plans, i, pager.free_memory_gb, set(pager._resident.keys()), pager.memory_budget_gb
                        )
                        if cand:
                            cm = catalog.get(cand)
                            if cm and (pager.free_memory_gb - cm.ram_required) >= 1.0:
                                pager.prefetch(cand, future_demanded_ids=future_model_ids)
                    elif is_oracle:
                        target_id = oracle_res.optimal_sequence[i]
                        model = catalog.get(target_id) or catalog.all_models()[0]
                        pe = pager.page_in(model.id)
                    else:
                        raise ValueError(f"Unknown policy {policy_name}")

                    selected_sequence.append(model.id)
                    tot_page += pe.duration_sec

                    # Empirical token generation latency with slight stochastic variance (+/- 2 tok)
                    tok_jitter = random.gauss(0, 2.0)
                    e_sec = round(max(0.1, model.latency * (115.0 + tok_jitter)), 3)
                    tot_exec += e_sec

                    # Proxy quality: capability score times model intrinsic quality rating
                    cap_match = model.capability_score(cap)
                    quals.append(round(min(1.0, cap_match * model.quality), 3))

                tot_dur = round(tot_page + tot_exec, 3)
                q_mean = round(float(np.mean(quals)), 3)
                gp = round((len(stage_plans) * q_mean) / tot_dur, 3)
                reloads_count = int(pager.total_reloads)

                # Regret relative to exact DP offline oracle cost
                if is_oracle:
                    regret_pct = 0.0
                else:
                    regret_pct = round(max(0.0, float((tot_dur - cost_oracle) / cost_oracle) * 100.0), 2)

                trial_dur.append(tot_dur)
                trial_page.append(round(tot_page, 3))
                trial_rel.append(float(reloads_count))
                trial_q.append(q_mean)
                trial_gp.append(gp)
                trial_reg.append(regret_pct)

                all_trials_records.append({
                    "workload_id": w_key,
                    "workload_title": w_title,
                    "policy": policy_name,
                    "trial_id": trial_idx,
                    "goodput_stages_per_sec": gp,
                    "quality_score": q_mean,
                    "paging_time_sec": round(tot_page, 3),
                    "execution_time_sec": round(tot_exec, 3),
                    "total_duration_sec": tot_dur,
                    "reloads_count": reloads_count,
                    "cost_oracle_sec": cost_oracle,
                    "regret_vs_oracle_pct": regret_pct,
                    "sequence": " -> ".join(selected_sequence),
                })

            gp_mean = round(float(np.mean(trial_gp)), 3)
            gp_ci = bootstrap_ci(trial_gp)
            q_mean = round(float(np.mean(trial_q)), 3)
            q_ci = bootstrap_ci(trial_q)
            page_mean = round(float(np.mean(trial_page)), 2)
            page_ci = bootstrap_ci(trial_page)
            rel_mean = round(float(np.mean(trial_rel)), 1)
            rel_ci = bootstrap_ci(trial_rel)
            reg_mean = round(float(np.mean(trial_reg)), 1)
            reg_ci = bootstrap_ci(trial_reg)

            aggregated_results[w_key]["policies"][policy_name] = {
                "goodput": {"mean": gp_mean, "ci95": list(gp_ci)},
                "quality": {"mean": q_mean, "ci95": list(q_ci)},
                "paging_time_sec": {"mean": page_mean, "ci95": list(page_ci)},
                "reloads": {"mean": rel_mean, "ci95": list(rel_ci)},
                "regret_vs_oracle_pct": {"mean": reg_mean, "ci95": list(reg_ci)},
            }

    # Export CSV
    os.makedirs(docs_dir, exist_ok=True)
    csv_path = os.path.join(docs_dir, "r3_trials.csv")
    fieldnames = [
        "workload_id",
        "workload_title",
        "policy",
        "trial_id",
        "goodput_stages_per_sec",
        "quality_score",
        "paging_time_sec",
        "execution_time_sec",
        "total_duration_sec",
        "reloads_count",
        "cost_oracle_sec",
        "regret_vs_oracle_pct",
        "sequence",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_trials_records)

    # Export JSON
    json_path = os.path.join(docs_dir, "r3_workload_generalization_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(aggregated_results, f, indent=2)

    return aggregated_results


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docs_dir = os.path.join(root_dir, "docs")

    print("=" * 80)
    print("MODELVM ROBUSTNESS EXPERIMENT (EXP-R3): WORKLOAD GENERALIZATION SWEEPS")
    print("=" * 80)

    results = run_r3_sweeps(num_trials_per_cell=10, docs_dir=docs_dir)

    for w_key, data in results.items():
        print(f"\n--- {w_key}: {data['title']} (Exact DP Oracle Cost: {data['oracle_cost_sec']:.2f} s) ---")
        print(f"{'Policy':<22} | {'Goodput (stg/s)':<17} | {'Quality (Q)':<15} | {'Paging (s)':<14} | {'Reloads':<10} | {'Regret (%)'}")
        print("-" * 92)
        for pol_name, m in data["policies"].items():
            gp_str = f"{m['goodput']['mean']:.3f} [{m['goodput']['ci95'][0]:.3f}, {m['goodput']['ci95'][1]:.3f}]"
            q_str = f"{m['quality']['mean']:.3f} [{m['quality']['ci95'][0]:.2f}, {m['quality']['ci95'][1]:.2f}]"
            p_str = f"{m['paging_time_sec']['mean']:.2f} [{m['paging_time_sec']['ci95'][0]:.1f}, {m['paging_time_sec']['ci95'][1]:.1f}]"
            r_str = f"{m['reloads']['mean']:.1f} [{m['reloads']['ci95'][0]:.1f}, {m['reloads']['ci95'][1]:.1f}]"
            reg_str = f"{m['regret_vs_oracle_pct']['mean']:.1f}% [{m['regret_vs_oracle_pct']['ci95'][0]:.1f}%, {m['regret_vs_oracle_pct']['ci95'][1]:.1f}%]"
            print(f"{pol_name:<22} | {gp_str:<17} | {q_str:<15} | {p_str:<14} | {r_str:<10} | {reg_str}")

    print("\n" + "=" * 80)
    print("Archived raw trials to: docs/r3_trials.csv")
    print("Saved aggregated results to: docs/r3_workload_generalization_results.json")
    print("=" * 80)


if __name__ == "__main__":
    main()
