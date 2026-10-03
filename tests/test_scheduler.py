"""Tests for Cognitive Scheduler multi-objective scoring."""

import unittest
from modelvm.core.types import Capability
from modelvm.pager.memory_manager import ModelPager
from modelvm.registry.catalog import ModelCatalog
from modelvm.scheduler.cognitive_scheduler import CognitiveScheduler


class TestCognitiveScheduler(unittest.TestCase):
    def setUp(self):
        self.catalog = ModelCatalog()
        self.pager = ModelPager(catalog=self.catalog, memory_budget_gb=8.0)
        self.scheduler = CognitiveScheduler(catalog=self.catalog, pager=self.pager)

    def test_mathematics_expert_scoring(self):
        # Best model for mathematics should be qwen-math-7b (mathematics-expert)
        winner, breakdowns = self.scheduler.select_best_model(
            target_capability=Capability.MATHEMATICS,
        )
        self.assertEqual(winner.id, "mathematics-expert")
        self.assertGreater(breakdowns[0].total_score, breakdowns[1].total_score)

    def test_resident_model_cache_bonus(self):
        # If mathematics-expert is already resident, its L_load is 0.0
        self.pager.page_in("mathematics-expert")
        winner, breakdowns = self.scheduler.select_best_model(
            target_capability=Capability.MATHEMATICS,
        )
        math_score = next(b for b in breakdowns if b.model_id == "mathematics-expert")
        self.assertEqual(math_score.l_load, 0.0)
        self.assertTrue(math_score.is_resident)

    def test_future_demand_incentive(self):
        # When coding is needed in future stages, coding-expert receives f_future bonus
        score_no_future = self.scheduler.compute_score(
            model=self.catalog.get("coding-expert"),
            target_capability=Capability.RESEARCH,
            future_capabilities=[Capability.PHYSICS],
        )
        score_with_future = self.scheduler.compute_score(
            model=self.catalog.get("coding-expert"),
            target_capability=Capability.RESEARCH,
            future_capabilities=[Capability.CODING],
        )
        self.assertGreater(score_with_future.f_future, score_no_future.f_future)
        self.assertGreater(score_with_future.total_score, score_no_future.total_score)


if __name__ == "__main__":
    unittest.main()
