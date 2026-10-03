"""Tests for Model Pager and memory budget enforcement."""

import unittest
from modelvm.core.types import PagingAction
from modelvm.pager.memory_manager import ModelPager
from modelvm.pager.policy import CostAwareEvictionPolicy, LRUEvictionPolicy
from modelvm.registry.catalog import ModelCatalog


class TestModelPager(unittest.TestCase):
    def setUp(self):
        self.catalog = ModelCatalog()
        self.pager = ModelPager(catalog=self.catalog, memory_budget_gb=8.0)

    def test_budget_enforcement_and_eviction(self):
        # 1. Page in research-expert (3.1 GB)
        ev1 = self.pager.page_in("research-expert")
        self.assertEqual(ev1.action, PagingAction.PAGE_IN)
        self.assertEqual(self.pager.active_memory_gb, 3.1)
        self.assertEqual(self.pager.free_memory_gb, 4.9)

        # 2. Page in mathematics-expert (2.4 GB)
        ev2 = self.pager.page_in("mathematics-expert")
        self.assertEqual(ev2.action, PagingAction.PAGE_IN)
        self.assertAlmostEqual(self.pager.active_memory_gb, 5.5, places=1)
        self.assertAlmostEqual(self.pager.free_memory_gb, 2.5, places=1)

        # 3. Cache hit on research-expert
        ev3 = self.pager.page_in("research-expert")
        self.assertEqual(ev3.action, PagingAction.CACHE_HIT)
        self.assertEqual(self.pager.cache_hits, 1)

        # 4. Page in general-reasoner (7.1 GB).
        # Since active is 5.5 and free is 2.5, loading 7.1 GB MUST trigger eviction to stay within 8.0 GB!
        ev4 = self.pager.page_in("general-reasoner")
        self.assertLessEqual(self.pager.active_memory_gb, 8.0)
        self.assertTrue(self.pager.is_resident("general-reasoner"))
        self.assertGreater(self.pager.total_evictions, 0)

    def test_page_out(self):
        self.pager.page_in("coding-expert")
        self.assertTrue(self.pager.is_resident("coding-expert"))
        self.pager.page_out("coding-expert")
        self.assertFalse(self.pager.is_resident("coding-expert"))
        self.assertEqual(self.pager.active_memory_gb, 0.0)


if __name__ == "__main__":
    unittest.main()
