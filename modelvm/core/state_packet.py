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
    verified: bool = Field(default=True, description="Whether calculation was verified")


class EvidenceItem(BaseModel):
    """Empirical or theoretical evidence supporting task claims."""
    claim: str = Field(description="The claim or finding")
    source: str = Field(default="Inference", description="Source reference or derivation")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Confidence score")


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
            calc_str = "\n".join(
                f"- `{c.expression}` = **{c.result}**" + (f" ({c.units})" if c.units else "")
                for c in self.calculations
            )
            sections.append(f"#### Verified Calculations:\n{calc_str}")
            
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

    def merge_update(self, update: "CognitiveStatePacket") -> "CognitiveStatePacket":
        """Accumulates newly discovered knowledge into the state packet without losing prior context."""
        # Add new facts preserving uniqueness
        for fact in update.facts:
            if fact not in self.facts:
                self.facts.append(fact)
                
        # Add new calculations
        existing_exprs = {c.expression for c in self.calculations}
        for calc in update.calculations:
            if calc.expression not in existing_exprs:
                self.calculations.append(calc)
                existing_exprs.add(calc.expression)
                
        # Add evidence
        existing_claims = {e.claim for e in self.evidence}
        for ev in update.evidence:
            if ev.claim not in existing_claims:
                self.evidence.append(ev)
                existing_claims.add(ev.claim)
                
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
                
        # If an open question was answered in facts or decisions, it can be resolved
        self.open_questions = [
            q for q in update.open_questions 
            if q not in self.facts and q not in self.decisions
        ]
        
        # Merge artifacts
        self.artifacts.update(update.artifacts)
        
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
