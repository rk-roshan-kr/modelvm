"""Tests for ModelProfiler and empirical capability measurement."""

import unittest
from modelvm.core.types import Capability
from modelvm.registry.catalog import ModelCatalog
from modelvm.registry.profiler import ModelProfiler, CapabilityProbe


class TestModelProfiler(unittest.TestCase):
    def setUp(self):
        self.catalog = ModelCatalog()
        self.profiler = ModelProfiler()

    def test_single_model_profile(self):
        math_model = self.catalog.get("mathematics-expert")
        profile = self.profiler.profile_model(math_model)
        self.assertEqual(profile.model_id, "mathematics-expert")
        self.assertIn("mathematics", profile.scores)
        # Mathematics expert should have high score on math probes
        self.assertGreaterEqual(profile.scores["mathematics"], 0.6)

    def test_catalog_profile_and_matrix_generation(self):
        matrix = self.profiler.profile_catalog(self.catalog, apply_to_manifests=True)
        self.assertEqual(len(matrix), len(self.catalog.list_models()))
        
        # Verify manifests now have empirical capabilities populated
        for m in self.catalog.list_models():
            self.assertGreater(len(m.empirical_capabilities), 0)
            score = m.capability_score(Capability.MATHEMATICS)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)

    def test_probe_arithmetic_verifier(self):
        probe = CapabilityProbe(
            probe_id="test-probe",
            capability=Capability.MATHEMATICS,
            prompt="Compute 10 + 20",
            expected_answer="30",
            evaluation_type="arithmetic",
        )
        self.assertTrue(self.profiler.evaluate_probe_response(probe, "The result is 30."))
        self.assertTrue(self.profiler.evaluate_probe_response(probe, "30"))
        self.assertFalse(self.profiler.evaluate_probe_response(probe, "The result is 45."))

    def test_matrix_table_rendering(self):
        matrix = self.profiler.profile_catalog(self.catalog, apply_to_manifests=False)
        table_str = self.profiler.format_matrix_table(matrix)
        self.assertIn("| Model ID |", table_str)
        self.assertIn("mathematics-expert", table_str)
