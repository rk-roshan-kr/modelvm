"""Cognitive State Packet (CSP): Model-neutral semantic task representation.

Allows heterogeneous open-weight models with completely different architectures,
tokenizers, and contexts to cooperate sequentially without hidden state transfer.
"""

from __future__ import annotations
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CalculationItem(BaseModel):
    """Structured mathematical or numerical calculation record."""
    expression: str = Field(description="Mathematical expression or formula")
    result: str = Field(description="Computed numerical or symbolic result")
    units: Optional[str] = Field(default=None, description="Physical or logical units")
    verified: bool = Field(default=False, description="Whether calculation was verified by an independent verifier")
    verification_method: Optional[str] = Field(
        default=None,
        description="Method used for verification: 'arithmetic', 'symbolic', 'external_tool', 'human', or None"
    )


class EvidenceItem(BaseModel):
    """Empirical or theoretical evidence supporting task claims."""
    claim: str = Field(description="The claim or finding")
    source: str = Field(default="Inference", description="Source reference or derivation")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Confidence score")
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat(), description="Generation timestamp")
    model_id: Optional[str] = Field(default=None, description="Which model generated this")


def diversity_weighted_confidence_aggregation(
    c1: float,
    c2: float,
    source1: str,
    source2: str,
    w_diversity: float = 0.65,
) -> float:
    """Diversity-weighted confidence aggregation heuristic.
    
    NOTE: This is a conservative engineering heuristic, NOT Bayesian inference.
    - Repeated claims from identical or overlapping sources apply no amplification (max rule).
    - Cross-model claims apply a diversity discount exponent (w_diversity) to penalize
      correlated priors across language models.
    """
    s1_clean = (source1 or "").strip().lower()
    s2_clean = (source2 or "").strip().lower()
    if s1_clean == s2_clean or s1_clean in s2_clean or s2_clean in s1_clean:
        return round(max(c1, c2), 4)
    p_combined = 1.0 - (1.0 - c1) * ((1.0 - c2) ** w_diversity)
    return round(min(0.99, max(c1, c2, p_combined)), 4)


class StageTrace(BaseModel):
    """Audit log of a completed cognitive stage."""
    stage_index: int
    capability: str
    model_id: str
    model_name: str
    action_taken: str
    duration_sec: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class CognitiveStatePacket(BaseModel):
    """The standardized semantic state exchanged between paged models.
    
    See PDR Section 5: Cognitive State Packet.
    """
    goal: str = Field(description="Primary user objective")
    stage_index: int = Field(default=0, description="Zero-indexed stage counter")
    current_capability: Optional[str] = Field(default=None, description="Currently executing capability")
    next_capability: Optional[str] = Field(default=None, description="Predicted or recommended next capability")
    
    facts: List[str] = Field(default_factory=list, description="Verified facts accumulated across stages")
    calculations: List[CalculationItem] = Field(default_factory=list, description="Numerical & symbolic results")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Structured claims and evidence")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made by specialist models")
    uncertainties: List[str] = Field(default_factory=list, description="Uncertainties or low-confidence points")
    decisions: List[str] = Field(default_factory=list, description="Decisions and architectural choices made")
    open_questions: List[str] = Field(default_factory=list, description="Remaining questions to resolve")
    
    artifacts: Dict[str, Any] = Field(default_factory=dict, description="Concrete outputs e.g. code, plots, summaries")
    history_trace: List[StageTrace] = Field(default_factory=list, description="Chronological stage trace")

    def to_dict(self) -> Dict[str, Any]:
        """Serializes CSP to standard dictionary."""
        return self.model_dump()

    def to_json(self, indent: int = 2) -> str:
        """Serializes CSP to formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_prompt_context(self) -> str:
        """Formats the CSP into a structured markdown prompt context for any LLM."""
        sections = [
            f"### [COGNITIVE STATE PACKET - STAGE {self.stage_index}]",
            f"**Overarching Goal**: {self.goal}",
        ]
        
        if self.current_capability:
            sections.append(f"**Current Domain Role**: {self.current_capability.upper()}")
            
        if self.facts:
            facts_str = "\n".join(f"- {f}" for f in self.facts)
            sections.append(f"#### Established Facts:\n{facts_str}")
            
        if self.calculations:
            calc_lines = []
            for c in self.calculations:
                status = f"[VERIFIED: {c.verification_method}]" if (c.verified and c.verification_method) else "[UNVERIFIED]"
                calc_lines.append(
                    f"- {status} `{c.expression}` = **{c.result}**" + (f" ({c.units})" if c.units else "")
                )
            sections.append("#### Calculations:\n" + "\n".join(calc_lines))
            
        if self.evidence:
            ev_str = "\n".join(f"- [{e.confidence * 100:.0f}% confidence] {e.claim} (Source: {e.source})" for e in self.evidence)
            sections.append(f"#### Supporting Evidence:\n{ev_str}")
            
        if self.assumptions:
            assump_str = "\n".join(f"- {a}" for a in self.assumptions)
            sections.append(f"#### Working Assumptions:\n{assump_str}")
            
        if self.uncertainties:
            unc_str = "\n".join(f"- {u}" for u in self.uncertainties)
            sections.append(f"#### Known Uncertainties:\n{unc_str}")
            
        if self.decisions:
            dec_str = "\n".join(f"- {d}" for d in self.decisions)
            sections.append(f"#### Prior Decisions:\n{dec_str}")
            
        if self.open_questions:
            oq_str = "\n".join(f"- {q}" for q in self.open_questions)
            sections.append(f"#### Open Questions:\n{oq_str}")

        if self.artifacts:
            sections.append("#### Artifacts Generated So Far:")
            for name, val in self.artifacts.items():
                if isinstance(val, str) and "\n" in val:
                    sections.append(f"**{name}**:\n```\n{val}\n```")
                else:
                    sections.append(f"- **{name}**: {val}")

        return "\n\n".join(sections)

    def merge_artifacts(self, update_artifacts: Dict[str, Any]) -> None:
        """Merges artifacts with version tracking for conflicts."""
        for key, val in update_artifacts.items():
            if key in self.artifacts and self.artifacts[key] != val:
                version = 1
                versioned_key = f"{key}_v{version}"
                while versioned_key in self.artifacts:
                    version += 1
                    versioned_key = f"{key}_v{version}"
                self.artifacts[versioned_key] = val
                self.artifacts[f"{key}_CONFLICT"] = True
            else:
                self.artifacts[key] = val

    def merge_update(self, update: "CognitiveStatePacket") -> "CognitiveStatePacket":
        """Accumulates newly discovered knowledge into the state packet without losing prior context."""
        # Add new facts preserving uniqueness
        for fact in update.facts:
            if fact not in self.facts:
                self.facts.append(fact)
                
        # Add or update calculations
        for calc in update.calculations:
            existing = next((c for c in self.calculations if c.expression == calc.expression), None)
            if existing:
                # If newly presented calculation is verified, upgrade existing entry
                if calc.verified and not existing.verified:
                    existing.verified = True
                    existing.verification_method = calc.verification_method
                    existing.result = calc.result
            else:
                self.calculations.append(calc)
                
        # Add evidence with diversity-weighted confidence aggregation & source diversity tracking
        for ev in update.evidence:
            existing = next((e for e in self.evidence if e.claim == ev.claim), None)
            if existing:
                existing.confidence = diversity_weighted_confidence_aggregation(
                    existing.confidence,
                    ev.confidence,
                    existing.source,
                    ev.source,
                )
                # Track source diversity
                if ev.source and ev.source not in existing.source:
                    existing.source = f"{existing.source} + {ev.source}"
                if ev.model_id and existing.model_id and ev.model_id not in existing.model_id:
                    existing.model_id = f"{existing.model_id}, {ev.model_id}"
                elif ev.model_id and not existing.model_id:
                    existing.model_id = ev.model_id
            else:
                self.evidence.append(ev)
                
        # Update assumptions, uncertainties, decisions, questions
        for a in update.assumptions:
            if a not in self.assumptions:
                self.assumptions.append(a)
                
        for u in update.uncertainties:
            if u not in self.uncertainties:
                self.uncertainties.append(u)
                
        for d in update.decisions:
            if d not in self.decisions:
                self.decisions.append(d)
                
        # Accumulate open questions, resolving any answered in facts or decisions
        combined_questions = []
        for q in self.open_questions + update.open_questions:
            if q not in combined_questions and q not in self.facts and q not in self.decisions:
                combined_questions.append(q)
        self.open_questions = combined_questions
        
        # Merge artifacts with conflict handling
        self.merge_artifacts(update.artifacts)
        
        # Update stage and capability
        self.stage_index = update.stage_index
        self.current_capability = update.current_capability
        self.next_capability = update.next_capability
        
        # Append history
        for h in update.history_trace:
            self.history_trace.append(h)
            
        return self

    @classmethod
    def extract_from_text(cls, goal: str, text: str, stage_index: int = 0) -> "CognitiveStatePacket":
        """Robustly parses an LLM response or structured block into a CognitiveStatePacket."""
        packet_data: Dict[str, Any] = {
            "goal": goal,
            "stage_index": stage_index,
            "facts": [],
            "calculations": [],
            "evidence": [],
            "assumptions": [],
            "uncertainties": [],
            "decisions": [],
            "open_questions": [],
            "artifacts": {},
        }
        
        # Check for embedded JSON block ```json ... ```
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                if isinstance(parsed, dict):
                    for k in packet_data:
                        if k in parsed:
                            packet_data[k] = parsed[k]
                    return cls.model_validate(packet_data)
            except Exception:
                pass
                
        # Fallback heuristic parsing from markdown bullet points
        curr_section = None
        for line in text.splitlines():
            line_str = line.strip()
            lower_line = line_str.lower()
            if "fact" in lower_line and (":" in line_str or "#" in line_str):
                curr_section = "facts"
                continue
            elif "calculation" in lower_line and (":" in line_str or "#" in line_str):
                curr_section = "calculations"
                continue
            elif "evidence" in lower_line and (":" in line_str or "#" in line_str):
                curr_section = "evidence"
                continue
            elif "assumption" in lower_line and (":" in line_str or "#" in line_str):
                curr_section = "assumptions"
                continue
            elif "uncertaint" in lower_line and (":" in line_str or "#" in line_str):
                curr_section = "uncertainties"
                continue
            elif "decision" in lower_line and (":" in line_str or "#" in line_str):
                curr_section = "decisions"
                continue
            elif "open question" in lower_line and (":" in line_str or "#" in line_str):
                curr_section = "open_questions"
                continue
                
            if curr_section and (line_str.startswith("- ") or line_str.startswith("* ")):
                bullet = line_str[2:].strip()
                if curr_section == "calculations":
                    if "=" in bullet:
                        parts = bullet.split("=")
                        packet_data["calculations"].append(
                            CalculationItem(expression=parts[0].strip(), result=parts[1].strip()).model_dump()
                        )
                elif curr_section == "evidence":
                    packet_data["evidence"].append(
                        EvidenceItem(claim=bullet, source="Model Output", confidence=0.85).model_dump()
                    )
                elif curr_section in packet_data and isinstance(packet_data[curr_section], list):
                    packet_data[curr_section].append(bullet)
                    
        return cls.model_validate(packet_data)
