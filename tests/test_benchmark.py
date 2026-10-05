"""Tests for Benchmark Evaluator, Independent Verifier, and Critical Ablation Study."""

import unittest
from modelvm.benchmark.ablation import AblationStudyRunner
from modelvm.core.state_packet import CalculationItem
from modelvm.core.types import AblationMode
from modelvm.core.verifier import ArithmeticVerifier


class TestBenchmark(unittest.TestCase):
    def test_ablation_study_execution(self):
        runner = AblationStudyRunner(memory_budget_gb=8.0)
        report = runner.run_study()

        self.assertIn(AblationMode.A_STATIC_ROUTER.value, report.runs)
        self.assertIn(AblationMode.B_DYNAMIC_NO_CSP.value, report.runs)
        self.assertIn(AblationMode.C_DYNAMIC_WITH_CSP.value, report.runs)
        self.assertIn(AblationMode.D_FULL_MODELVM.value, report.runs)

        d_metrics = report.runs[AblationMode.D_FULL_MODELVM.value]
        a_metrics = report.runs[AblationMode.A_STATIC_ROUTER.value]

        # Mode D should achieve superior quality coverage and structural completeness over static router
        self.assertGreater(d_metrics.capability_coverage_score, a_metrics.capability_coverage_score)
        self.assertGreater(d_metrics.csp_structural_completeness, a_metrics.csp_structural_completeness)
        self.assertGreater(d_metrics.memory_savings_percent, 80.0)

    def test_compute_quality_from_csp_function(self):
        from modelvm.benchmark.evaluator import compute_quality_from_csp
        csp = {
            "facts": ["A", "B", "C"],  # 3 * 0.05 = 0.15
            "calculations": [
                {"expression": "E=mc^2", "result": "valid", "verified": True},
                {"expression": "F=ma", "result": "valid", "verified": True},
            ],  # 2 * 0.10 = 0.20
            "evidence": [
                {"claim": "X", "confidence": 0.90},
                {"claim": "Y", "confidence": 0.80},
            ],  # avg 0.85 * 0.50 = 0.425
            "uncertainties": [],
        }
        quality = compute_quality_from_csp(csp)
        # Expected: 0.15 + 0.20 + 0.425 = 0.775
        self.assertAlmostEqual(quality, 0.775, places=2)

    def test_arithmetic_verifier(self):
        # 1. Valid arithmetic expression
        calc_valid = CalculationItem(
            expression="k = 2.5 * 14.2**2",
            result="504.1",
            units="N/m",
        )
        self.assertFalse(calc_valid.verified)
        is_verified = ArithmeticVerifier.verify_item(calc_valid)
        self.assertTrue(is_verified)
        self.assertTrue(calc_valid.verified)
        self.assertEqual(calc_valid.verification_method, "arithmetic")

        # 2. Incorrect calculation (result does not match expression)
        calc_invalid = CalculationItem(
            expression="k = 2.5 * 14.2**2",
            result="9999.0",
        )
        is_verified_inv = ArithmeticVerifier.verify_item(calc_invalid)
        self.assertFalse(is_verified_inv)
        self.assertFalse(calc_invalid.verified)
        self.assertIsNone(calc_invalid.verification_method)


if __name__ == "__main__":
    unittest.main()
