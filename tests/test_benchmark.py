"""Tests for Benchmark Evaluator and Critical Ablation Study."""

import unittest
from modelvm.benchmark.ablation import AblationStudyRunner
from modelvm.core.types import AblationMode


class TestBenchmark(unittest.TestCase):
    def test_ablation_study_execution(self):
        runner = AblationStudyRunner(memory_budget_gb=8.0)
        report = runner.run_study("Analyze this scientific paper and write code.")

        self.assertIn(AblationMode.A_STATIC_ROUTER.value, report.runs)
        self.assertIn(AblationMode.B_DYNAMIC_NO_CSP.value, report.runs)
        self.assertIn(AblationMode.C_DYNAMIC_WITH_CSP.value, report.runs)
        self.assertIn(AblationMode.D_FULL_MODELVM.value, report.runs)

        d_metrics = report.runs[AblationMode.D_FULL_MODELVM.value]
        a_metrics = report.runs[AblationMode.A_STATIC_ROUTER.value]

        # Mode D should achieve superior quality coverage over static router
        self.assertGreater(d_metrics.capability_coverage_score, a_metrics.capability_coverage_score)
        self.assertGreater(d_metrics.memory_savings_percent, 80.0)


if __name__ == "__main__":
    unittest.main()
