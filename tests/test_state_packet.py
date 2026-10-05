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

    def test_evidence_confidence_merging(self):
        # Test distinct sources with diversity discount
        csp1 = CognitiveStatePacket(
            goal="test",
            evidence=[EvidenceItem(claim="Hypothesis X", source="Model A", confidence=0.80)]
        )
        csp2 = CognitiveStatePacket(
            goal="test",
            evidence=[EvidenceItem(claim="Hypothesis X", source="Model B", confidence=0.90)]
        )
        merged = csp1.merge_update(csp2)
        self.assertEqual(len(merged.evidence), 1)
        # Expected: 1 - (1 - 0.8) * (1 - 0.9)^0.65 = 1 - 0.2 * 0.22387 = 0.9552
        self.assertAlmostEqual(merged.evidence[0].confidence, 0.9552, places=3)
        self.assertIn("Model A", merged.evidence[0].source)
        self.assertIn("Model B", merged.evidence[0].source)

        # Test duplicate/same source (max rule)
        csp3 = CognitiveStatePacket(
            goal="test",
            evidence=[EvidenceItem(claim="Hypothesis Y", source="Model A", confidence=0.70)]
        )
        csp4 = CognitiveStatePacket(
            goal="test",
            evidence=[EvidenceItem(claim="Hypothesis Y", source="Model A", confidence=0.85)]
        )
        merged_same = csp3.merge_update(csp4)
        self.assertEqual(merged_same.evidence[0].confidence, 0.85)

    def test_merge_is_associative(self):
        """Verify (A ⊕ B) ⊕ C = A ⊕ (B ⊕ C) for facts, calculations, and evidence claims."""
        csp_a = CognitiveStatePacket(goal="test", facts=["Fact 1"], calculations=[CalculationItem(expression="1+1", result="2")])
        csp_b = CognitiveStatePacket(goal="test", facts=["Fact 2"], evidence=[EvidenceItem(claim="Claim B", confidence=0.9)])
        csp_c = CognitiveStatePacket(goal="test", facts=["Fact 3"], calculations=[CalculationItem(expression="2+2", result="4")])

        # Left side: (A ⊕ B) ⊕ C
        left = csp_a.model_copy(deep=True)
        left.merge_update(csp_b.model_copy(deep=True))
        left.merge_update(csp_c.model_copy(deep=True))

        # Right side: A ⊕ (B ⊕ C)
        bc = csp_b.model_copy(deep=True)
        bc.merge_update(csp_c.model_copy(deep=True))
        right = csp_a.model_copy(deep=True)
        right.merge_update(bc)

        self.assertEqual(set(left.facts), set(right.facts))
        self.assertEqual({c.expression for c in left.calculations}, {c.expression for c in right.calculations})
        self.assertEqual({e.claim for e in left.evidence}, {e.claim for e in right.evidence})

    def test_merge_is_commutative(self):
        """Verify A ⊕ B = B ⊕ A for set-based facts and evidence claims."""
        csp_a = CognitiveStatePacket(
            goal="test",
            facts=["Fact A"],
            evidence=[EvidenceItem(claim="Claim 1", confidence=0.9)]
        )
        csp_b = CognitiveStatePacket(
            goal="test",
            facts=["Fact B"],
            evidence=[EvidenceItem(claim="Claim 2", confidence=0.8)]
        )

        ab = csp_a.model_copy(deep=True)
        ab.merge_update(csp_b)

        ba = csp_b.model_copy(deep=True)
        ba.merge_update(csp_a)

        self.assertEqual(set(ab.facts), set(ba.facts))
        self.assertEqual({e.claim for e in ab.evidence}, {e.claim for e in ba.evidence})

    def test_merge_is_idempotent(self):
        """Verify A ⊕ A = A."""
        csp = CognitiveStatePacket(
            goal="test",
            facts=["Fact Unique"],
            evidence=[EvidenceItem(claim="Claim Unique", confidence=0.95)],
            calculations=[CalculationItem(expression="E=mc^2", result="energy")]
        )
        merged = csp.model_copy(deep=True)
        merged.merge_update(csp)

        self.assertEqual(len(merged.facts), 1)
        self.assertEqual(len(merged.evidence), 1)
        self.assertEqual(len(merged.calculations), 1)

    def test_artifact_conflict_versioning(self):
        csp = CognitiveStatePacket(goal="test", artifacts={"code.py": "print('v1')"})
        update = CognitiveStatePacket(goal="test", artifacts={"code.py": "print('v2')"})
        csp.merge_update(update)

        self.assertIn("code.py", csp.artifacts)
        self.assertIn("code.py_v1", csp.artifacts)
        self.assertTrue(csp.artifacts.get("code.py_CONFLICT"))


if __name__ == "__main__":
    unittest.main()
