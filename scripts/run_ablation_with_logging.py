"""Supplementary Material Generator: Executes Full Ablation Study with Verbose Logging.

Generates:
1. docs/ablation_benchmark_results.json - Raw JSON execution trace and metrics
2. docs/appendix_ablation_results.md - Formatted appendix document for research paper submission
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modelvm.core.types import AblationMode, FactorialConfig
from modelvm.executor.kernel import CognitiveKernel
from modelvm.benchmark.evaluator import Evaluator
from modelvm.benchmark.ablation import FactorialStudyRunner


def run_full_ablation_suite():
    budget_gb = 8.0
    task_goal = "Analyze this scientific paper, reproduce its numerical result, write the implementation, and explain the physical meaning."
    baseline_all_resident_gb = 52.7

    print("==================================================")
    print("Executing 2^3 Full Factorial Study on Dynamic Paging Substrate")
    print("==================================================")
    factorial_runner = FactorialStudyRunner(memory_budget_gb=budget_gb)
    factorial_report = factorial_runner.run_study(task_goal=task_goal)

    modes = [
        AblationMode.A_STATIC_ROUTER,
        AblationMode.B_DYNAMIC_NO_CSP,
        AblationMode.C_DYNAMIC_WITH_CSP,
        AblationMode.D_FULL_MODELVM,
    ]

    results_data = {
        "timestamp": datetime.now().isoformat(),
        "task_goal": task_goal,
        "memory_budget_gb": budget_gb,
        "baseline_all_resident_gb": baseline_all_resident_gb,
        "factorial_report": {
            "main_effects": {
                "Factor_A_CSP": factorial_report.main_effect_csp,
                "Factor_B_WS": factorial_report.main_effect_ws,
                "Factor_C_Scheduler": factorial_report.main_effect_scheduler,
            },
            "interactions": {
                "CSP_x_WS": factorial_report.interaction_csp_ws,
                "CSP_x_Scheduler": factorial_report.interaction_csp_sched,
                "WS_x_Scheduler": factorial_report.interaction_ws_sched,
                "Three_Way": factorial_report.three_way_interaction,
            },
            "runs": {k: v.model_dump() for k, v in factorial_report.runs.items()},
        },
        "modes": {}
    }

    markdown_sections = []
    markdown_sections.append("# Appendix: Empirical Ablation Benchmark Results\n")
    markdown_sections.append(f"**Execution Timestamp:** `{results_data['timestamp']}`  ")
    markdown_sections.append(f"**Target Task:** *{task_goal}*  ")
    markdown_sections.append(f"**RAM Budget Constraint:** `{budget_gb} GB` | **All-Resident Catalog Baseline:** `{baseline_all_resident_gb} GB`\n")
    markdown_sections.append("---\n")

    # 2^3 Factorial Summary Table
    markdown_sections.append("## 1. Orthogonal 2³ Factorial Ablation Matrix (Dynamic Paging Substrate)\n")
    markdown_sections.append("| Configuration ID | Paging | Factor A: CSP | Factor B: WS | Factor C: Sched | Peak RAM | MSR (%) | Quality (CCS) | Cap Density | Paging (s) | Verified Calcs |")
    markdown_sections.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

    factorial_configs_order = [
        (FactorialConfig.REF_STATIC_MONOLITH, "❌ None", "❌ Off", "❌ Off", "❌ Off"),
        (FactorialConfig.C0_PAGING_BASE, "✅ Active", "❌ Off", "❌ Off", "❌ Off"),
        (FactorialConfig.C1_CSP, "✅ Active", "✅ On", "❌ Off", "❌ Off"),
        (FactorialConfig.C2_WS, "✅ Active", "❌ Off", "✅ On", "❌ Off"),
        (FactorialConfig.C3_SCHEDULER, "✅ Active", "❌ Off", "❌ Off", "✅ On"),
        (FactorialConfig.C4_CSP_WS, "✅ Active", "✅ On", "✅ On", "❌ Off"),
        (FactorialConfig.C5_CSP_SCHEDULER, "✅ Active", "✅ On", "❌ Off", "✅ On"),
        (FactorialConfig.C6_WS_SCHEDULER, "✅ Active", "❌ Off", "✅ On", "✅ On"),
        (FactorialConfig.C7_FULL_MODELVM, "✅ Active", "✅ On", "✅ On", "✅ On"),
    ]

    for cfg, pg_str, csp_str, ws_str, sc_str in factorial_configs_order:
        m = factorial_report.runs[cfg.value]
        markdown_sections.append(
            f"| `{cfg.value}` | {pg_str} | {csp_str} | {ws_str} | {sc_str} | "
            f"{m.peak_memory_gb} GB | {m.memory_savings_percent}% | **{m.capability_coverage_score:.2f}** | "
            f"{m.capability_density:.2f} | {m.paging_overhead_sec:.1f}s | {m.calculations_verified} |"
        )

    markdown_sections.append("\n### Statistical Factor Effects & Interactions (Yates Analysis)\n")
    markdown_sections.append(f"```text\n{factorial_report.statistical_summary}\n```\n")
    markdown_sections.append("---\n")

    summary_rows = []

    for mode in modes:
        print(f"\n==================================================")
        print(f"Executing Mode: {mode.value}")
        print(f"==================================================")
        
        kernel = CognitiveKernel(memory_budget_gb=budget_gb)
        summary = kernel.execute_task(goal=task_goal, ablation_mode=mode)
        metrics = Evaluator.evaluate(summary, baseline_all_resident_gb=baseline_all_resident_gb)
        
        mode_data = {
            "metrics": metrics.model_dump(),
            "final_csp": summary.final_csp,
            "stage_results": [s.model_dump() for s in summary.stage_results],
        }
        results_data["modes"][mode.value] = mode_data

        summary_rows.append(
            f"| `{mode.value}` | {metrics.peak_memory_gb} GB | {metrics.memory_savings_percent}% | "
            f"**{metrics.capability_coverage_score:.2f}** | {metrics.capability_density:.2f} | "
            f"{metrics.total_time_sec:.2f}s | {metrics.paging_overhead_sec:.1f}s | {metrics.cache_hit_rate*100:.1f}% | "
            f"{metrics.facts_preserved} | {metrics.calculations_verified} |"
        )

    # Markdown Summary Table
    markdown_sections.append("## 1. Comprehensive Cross-Configuration Comparison\n")
    markdown_sections.append("| Mode | Peak RAM | MSR (%) | Quality (CCS) | Cap Density | Total Time | Paging Overhead | Cache Hit | Facts | Verified Calcs |")
    markdown_sections.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    markdown_sections.extend(summary_rows)
    markdown_sections.append("\n---\n")

    # Detailed Mode-by-Mode Breakdowns
    markdown_sections.append("## 2. Detailed Stage Traces & Memory Events\n")
    for mode in modes:
        m_data = results_data["modes"][mode.value]
        m_metrics = m_data["metrics"]
        markdown_sections.append(f"### Configuration: `{mode.value}`\n")
        markdown_sections.append(f"- **Peak Resident Memory:** {m_metrics['peak_memory_gb']} GB (Savings: {m_metrics['memory_savings_percent']}%)")
        markdown_sections.append(f"- **Quality Score (CCS):** {m_metrics['capability_coverage_score']} (Derived from {m_metrics['facts_preserved']} facts, {m_metrics['calculations_verified']} verified calcs)")
        markdown_sections.append(f"- **Cache Hit Rate:** {m_metrics['cache_hit_rate']*100:.1f}% | Paging Overhead: {m_metrics['paging_overhead_sec']}s\n")
        
        markdown_sections.append("#### Stage Execution Log:")
        markdown_sections.append("| Stage Index | Stage Title | Capability | Executing Model | Time (s) | Paging Action |")
        markdown_sections.append("| :---: | :--- | :--- | :--- | :---: | :--- |")
        for res in m_data["stage_results"]:
            markdown_sections.append(
                f"| {res['stage_index']} | {res['stage_title']} | `{res['capability']}` | `{res['model_id']}` | {res['execution_duration_sec']:.2f}s | {res['paging_action']} |"
            )
        markdown_sections.append("")

    # Save JSON artifact
    os.makedirs("docs", exist_ok=True)
    json_path = os.path.join("docs", "ablation_benchmark_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2)
    print(f"\nSaved raw JSON results to: {json_path}")

    # Save Markdown artifact
    md_path = os.path.join("docs", "appendix_ablation_results.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_sections))
    print(f"Saved formatted markdown appendix to: {md_path}")


if __name__ == "__main__":
    run_full_ablation_suite()
