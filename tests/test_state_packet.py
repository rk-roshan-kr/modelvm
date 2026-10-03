"""Tests for Cognitive State Packet (CSP)."""

import unittest
from modelvm.core.state_packet import CognitiveStatePacket, CalculationItem, EvidenceItem


class TestCognitiveStatePacket(unittest.TestCase):
    def setUp(self):
        self.csp = CognitiveStatePacket(
            goal="Analyze harmonic resonance",
            stage_index=1,
            current_capability="research",
        )

    def test_serialization_and_deserialization(self):
        self.csp.facts.append("Natural frequency omega_n = 14.2 rad/s")
        self.csp.calculations.append(
            CalculationItem(expression="f = omega_n / (2*pi)", result="2.26", units="Hz", verified=True)
        )
        json_str = self.csp.to_json()
        self.assertIn("14.2", json_str)
        self.assertIn("2.26", json_str)

        restored = CognitiveStatePacket.model_validate_json(json_str)
        self.assertEqual(restored.goal, "Analyze harmonic resonance")
        self.assertEqual(len(restored.facts), 1)
        self.assertEqual(len(restored.calculations), 1)
        self.assertEqual(restored.calculations[0].expression, "f = omega_n / (2*pi)")

    def test_merge_update(self):
        self.csp.facts.append("Fact A")
        self.csp.decisions.append("Decision 1")

        update = CognitiveStatePacket(
            goal="Analyze harmonic resonance",
            stage_index=2,
            current_capability="mathematics",
            facts=["Fact A", "Fact B"],
            calculations=[CalculationItem(expression="x = 2+2", result="4")],
            decisions=["Decision 2"],
        )

        self.csp.merge_update(update)
        # Should not duplicate Fact A
        self.assertEqual(self.csp.facts, ["Fact A", "Fact B"])
        self.assertEqual(len(self.csp.calculations), 1)
        self.assertEqual(self.csp.decisions, ["Decision 1", "Decision 2"])
        self.assertEqual(self.csp.stage_index, 2)
        self.assertEqual(self.csp.current_capability, "mathematics")

    def test_to_prompt_context(self):
        self.csp.facts.append("Damping ratio is 0.12")
        self.csp.calculations.append(CalculationItem(expression="Q = 1 / (2*zeta)", result="4.17"))
        prompt = self.csp.to_prompt_context()

        self.assertIn("### [COGNITIVE STATE PACKET - STAGE 1]", prompt)
        self.assertIn("Damping ratio is 0.12", prompt)
        self.assertIn("Q = 1 / (2*zeta)", prompt)
        self.assertIn("4.17", prompt)


if __name__ == "__main__":
    unittest.main()
