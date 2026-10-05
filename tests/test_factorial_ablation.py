"""Tests for the 2^3 Factorial Ablation Matrix and Hardware Telemetry."""

import unittest
from modelvm.benchmark.ablation import FactorialStudyRunner, FactorialReport
from modelvm.core.types import FactorialConfig
from modelvm.telemetry.hardware import HardwareTelemetry


class TestFactorialAblation(unittest.TestCase):
    def test_hardware_telemetry_snapshot(self):
        telemetry = HardwareTelemetry()
        snap = telemetry.take_snapshot()
        self.assertGreater(snap.process_rss_mb, 0.0)
        self.assertIsNotNone(snap.device_name)

        # Test measured transition
        called = False
        def dummy_transition():
            nonlocal called
            called = True
            return "ok"

        res, trans = telemetry.measure_transition("test-model", "PAGE_IN", dummy_transition)
        self.assertEqual(res, "ok")
        self.assertTrue(called)
        self.assertGreaterEqual(trans.wall_clock_duration_sec, 0.0)
        self.assertEqual(trans.model_id, "test-model")
        self.assertEqual(len(telemetry.get_history()), 1)

    def test_factorial_study_matrix_coverage(self):
        runner = FactorialStudyRunner(memory_budget_gb=8.0)
        report: FactorialReport = runner.run_study()

        # 1. Verify all 9 configurations are executed
        expected_configs = [
            FactorialConfig.REF_STATIC_MONOLITH.value,
            FactorialConfig.C0_PAGING_BASE.value,
            FactorialConfig.C1_CSP.value,
            FactorialConfig.C2_WS.value,
            FactorialConfig.C3_SCHEDULER.value,
            FactorialConfig.C4_CSP_WS.value,
            FactorialConfig.C5_CSP_SCHEDULER.value,
            FactorialConfig.C6_WS_SCHEDULER.value,
            FactorialConfig.C7_FULL_MODELVM.value,
        ]
        for cfg in expected_configs:
            self.assertIn(cfg, report.runs)

        # 2. Main effect of Factor A (CSP) should be positive and substantial
        self.assertGreater(report.main_effect_csp, 0.0)

        # 3. Mode C7 (Full ModelVM) should achieve high memory savings and top capability coverage
        c7_metrics = report.runs[FactorialConfig.C7_FULL_MODELVM.value]
        ref_metrics = report.runs[FactorialConfig.REF_STATIC_MONOLITH.value]
        c0_metrics = report.runs[FactorialConfig.C0_PAGING_BASE.value]

        self.assertGreater(c7_metrics.memory_savings_percent, 80.0)
        self.assertGreater(c7_metrics.capability_coverage_score, c0_metrics.capability_coverage_score)
        self.assertGreater(c7_metrics.capability_coverage_score, ref_metrics.capability_coverage_score)

        # 4. Statistical summary string should be populated with effects
        self.assertIn("Main Effect of CSP", report.statistical_summary)
        self.assertIn("Main Effect of Working Set", report.statistical_summary)
        self.assertIn("Main Effect of Scheduler", report.statistical_summary)
        self.assertIn("3-Way Interaction", report.statistical_summary)


if __name__ == "__main__":
    unittest.main()
