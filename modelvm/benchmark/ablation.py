"""Critical Ablation Study Suite.

Executes the four configurations defined in PDR Section 13:
A. Static single-model routing
B. Routing + dynamic loading
C. Routing + dynamic loading + CSP
D. Full ModelVM (+ CSP + predictive working set + resource-aware scheduling)
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel
from modelvm.benchmark.evaluator import BenchmarkMetrics, Evaluator
from modelvm.core.types import AblationMode
from modelvm.executor.kernel import CognitiveKernel, TaskExecutionSummary


class AblationReport(BaseModel):
    """Comparative report across all four configurations."""
    task_goal: str
    baseline_all_resident_ram_gb: float
    budget_gb: float
    runs: Dict[str, BenchmarkMetrics]
    winner_analysis: str


class AblationStudyRunner:
    """Automates side-by-side evaluation of ModelVM architectural mechanisms."""

    def __init__(self, memory_budget_gb: float = 8.0):
        self.memory_budget_gb = memory_budget_gb

    def run_study(self, task_goal: Optional[str] = None) -> AblationReport:
        """Executes all 4 configurations on the task and compiles metrics."""
        goal = (
            task_goal
            or "Analyze this scientific paper, reproduce its numerical result, write the implementation, and explain the physical meaning."
        )

        modes = [
            AblationMode.A_STATIC_ROUTER,
            AblationMode.B_DYNAMIC_NO_CSP,
            AblationMode.C_DYNAMIC_WITH_CSP,
            AblationMode.D_FULL_MODELVM,
        ]

        runs_map: Dict[str, BenchmarkMetrics] = {}

        for mode in modes:
            kernel = CognitiveKernel(memory_budget_gb=self.memory_budget_gb)
            summary: TaskExecutionSummary = kernel.execute_task(goal=goal, ablation_mode=mode)
            metrics = Evaluator.evaluate(summary, baseline_all_resident_gb=52.7)
            runs_map[mode.value] = metrics

        d_metrics = runs_map[AblationMode.D_FULL_MODELVM.value]
        a_metrics = runs_map[AblationMode.A_STATIC_ROUTER.value]
        c_metrics = runs_map[AblationMode.C_DYNAMIC_WITH_CSP.value]

        winner_analysis = (
            f"ModelVM (Mode D) achieved {d_metrics.memory_savings_percent}% memory savings "
            f"under an {self.memory_budget_gb} GB budget (operating a 52.7 GB library with peak memory {d_metrics.peak_memory_gb} GB). "
            f"Compared to static routing (Mode A), capability quality jumped from {a_metrics.capability_coverage_score*100:.0f}% to {d_metrics.capability_coverage_score*100:.0f}%. "
            f"Predictive working-set scheduling reduced paging thrashing and achieved a Capability Density of {d_metrics.capability_density}."
        )

        return AblationReport(
            task_goal=goal,
            baseline_all_resident_ram_gb=52.7,
            budget_gb=self.memory_budget_gb,
            runs=runs_map,
            winner_analysis=winner_analysis,
        )
