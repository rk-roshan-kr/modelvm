"""Confidence Controller and Escalation Manager."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
from modelvm.core.manifest import ModelManifest
from modelvm.core.state_packet import CognitiveStatePacket
from modelvm.core.types import Capability


@dataclass
class ConfidenceAssessment:
    """Evaluation of the cognitive confidence of a stage result."""
    confidence_score: float
    is_acceptable: bool
    escalation_needed: bool
    reason: str
    suggested_model_id: Optional[str] = None


class ConfidenceController:
    """Monitors stage results and triggers cognitive escalation when needed."""

    def __init__(self, min_confidence_threshold: float = 0.70):
        self.min_confidence_threshold = min_confidence_threshold

    def evaluate_stage_result(
        self,
        csp: CognitiveStatePacket,
        executing_model: ModelManifest,
        target_capability: Capability,
    ) -> ConfidenceAssessment:
        """Evaluates whether the stage met quality and confidence thresholds."""
        base_confidence = executing_model.quality

        # Penalty for high uncertainty count
        unc_penalty = min(0.35, len(csp.uncertainties) * 0.08)
        
        # Bonus for verified calculations and facts
        verification_bonus = 0.0
        if csp.calculations and all(c.verified for c in csp.calculations):
            verification_bonus += 0.05
        if len(csp.facts) > 0:
            verification_bonus += 0.03

        effective_confidence = max(0.0, min(1.0, base_confidence - unc_penalty + verification_bonus))
        is_acceptable = effective_confidence >= self.min_confidence_threshold

        if not is_acceptable:
            # Need escalation: recommend either general reasoner or master synthesizer
            escalation_target = "general-reasoner" if target_capability != Capability.GENERAL else "synthesizer-master"
            return ConfidenceAssessment(
                confidence_score=round(effective_confidence, 3),
                is_acceptable=False,
                escalation_needed=True,
                reason=f"Confidence {effective_confidence:.2f} below threshold {self.min_confidence_threshold:.2f} due to {len(csp.uncertainties)} uncertainties",
                suggested_model_id=escalation_target,
            )

        return ConfidenceAssessment(
            confidence_score=round(effective_confidence, 3),
            is_acceptable=True,
            escalation_needed=False,
            reason="Stage completed with acceptable cognitive confidence",
        )
