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

    def test_working_set_lookahead_and_prefetch_scoring(self):
        from modelvm.router.working_set import CognitiveWorkingSetPredictor
        from modelvm.router.task_decomposer import CognitiveStagePlan

        stages = [
            CognitiveStagePlan(stage_index=0, title="Stage 0", capability=Capability.RESEARCH, description=""),
            CognitiveStagePlan(stage_index=1, title="Stage 1", capability=Capability.MATHEMATICS, description=""),
            CognitiveStagePlan(stage_index=2, title="Stage 2", capability=Capability.CODING, description=""),
            CognitiveStagePlan(stage_index=3, title="Stage 3", capability=Capability.PHYSICS, description=""),
            CognitiveStagePlan(stage_index=4, title="Stage 4", capability=Capability.SYNTHESIS, description=""),
        ]

        predictor = CognitiveWorkingSetPredictor(catalog=self.catalog, lookahead_window=4)
        self.assertEqual(predictor.lookahead_window, 4)

        future_caps = predictor.predict_future_capabilities(stages, current_stage_index=0)
        self.assertEqual(len(future_caps), 4)
        self.assertEqual(future_caps, [Capability.MATHEMATICS, Capability.CODING, Capability.PHYSICS, Capability.SYNTHESIS])

        weighted_caps = predictor.predict_future_capabilities_weighted(stages, current_stage_index=0)
        self.assertEqual(len(weighted_caps), 4)
        self.assertEqual(weighted_caps[0][1], 1.0)
        self.assertAlmostEqual(weighted_caps[1][1], 0.8)

        # Prefetch recommendation should score candidate models based on ROI
        prefetch_winner = predictor.recommend_prefetch_model(
            planned_stages=stages,
            current_stage_index=0,
            free_memory_gb=5.0,
            resident_ids={"research-analyst"},
            memory_budget_gb=8.0,
        )
        self.assertIsNotNone(prefetch_winner)
        # Should be a valid model ID for one of the upcoming capabilities
        self.assertIn(prefetch_winner, ["mathematics-expert", "coding-expert", "physics-expert", "synthesizer-master"])


if __name__ == "__main__":
    unittest.main()
