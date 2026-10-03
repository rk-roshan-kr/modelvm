"""Tests for Cognitive Kernel end-to-end execution."""

import unittest
from modelvm.core.types import AblationMode
from modelvm.executor.kernel import CognitiveKernel


class TestCognitiveKernel(unittest.TestCase):
    def setUp(self):
        self.kernel = CognitiveKernel(memory_budget_gb=8.0)

    def test_pdr_example_execution(self):
        goal = "Analyze this scientific paper, reproduce its numerical result, write the implementation, and explain the physical meaning."
        summary = self.kernel.execute_task(goal=goal, ablation_mode=AblationMode.D_FULL_MODELVM)

        # 1. Verification of 5 cognitive stages
        self.assertEqual(summary.total_stages, 5)
        self.assertEqual(len(summary.stage_results), 5)

        # 2. Hard budget respected
        self.assertLessEqual(summary.peak_resident_memory_gb, 8.0)
        self.assertGreater(summary.memory_savings_ratio, 0.80)  # > 80% memory savings

        # 3. Final state packet accumulated facts and calculations
        final_csp = summary.final_csp
        self.assertGreater(len(final_csp.get("facts", [])), 0)
        self.assertGreater(len(final_csp.get("calculations", [])), 0)
        self.assertIn("simulation_code.py", final_csp.get("artifacts", {}))


if __name__ == "__main__":
    unittest.main()
