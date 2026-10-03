"""Task Decomposer: Breaks down user goals into ordered cognitive subtasks."""

from __future__ import annotations
import re
from typing import List, Optional
from pydantic import BaseModel, Field
from modelvm.core.types import Capability


class CognitiveStagePlan(BaseModel):
    """A planned stage in the cognitive task graph."""
    stage_index: int
    title: str
    capability: Capability
    description: str
    expected_artifact: Optional[str] = None


class TaskDecomposer:
    """Decomposes multi-domain user goals into a sequence of capability-specific stages."""

    PRESET_TASKS = {
        "pdr_example": {
            "query": "Analyze this scientific paper, reproduce its numerical result, write the implementation, and explain the physical meaning.",
            "stages": [
                ("Extract scientific assumptions & equations", Capability.RESEARCH, "Identify theoretical principles, parameters, and governing equations"),
                ("Formal mathematical derivation & numerical solving", Capability.MATHEMATICS, "Verify boundary conditions, solve equations, and compute numerical values"),
                ("Algorithm implementation & simulation code", Capability.CODING, "Write clean, reproducible Python simulation code and unit tests"),
                ("Physical interpretation & thermodynamic analysis", Capability.PHYSICS, "Analyze physical implications, phase space behavior, and domain limits"),
                ("Comprehensive synthesis & executive report", Capability.SYNTHESIS, "Combine research, calculations, code, and interpretation into final report"),
            ],
        },
        "financial_quant": {
            "query": "Develop algorithmic trading strategy backtest, verify stochastic calculus proofs, implement vectorized Python engine, and stress-test market shocks.",
            "stages": [
                ("Quantitative market theory & risk hypotheses", Capability.FINANCE, "Define alpha factor, transaction cost model, and risk constraints"),
                ("Stochastic calculus proof & variance reduction", Capability.MATHEMATICS, "Derive martingale properties and calculate closed-form option bounds"),
                ("Vectorized backtesting engine implementation", Capability.CODING, "Write high-performance vectorized NumPy/Pandas simulation with slippage"),
                ("Final risk report & capital allocation", Capability.SYNTHESIS, "Synthesize Sharpe ratio, drawdown profile, and portfolio mandate"),
            ],
        },
        "clinical_trial": {
            "query": "Evaluate clinical trial dataset, verify statistical significance, write reproducibility pipeline, and summarize biological mechanism.",
            "stages": [
                ("Biomedical pathway & pharmacological mechanism", Capability.MEDICINE, "Inspect receptor binding affinity and biological drug mechanism"),
                ("Biostatistical hypothesis testing & p-values", Capability.MATHEMATICS, "Compute hazard ratios, Kaplan-Meier curves, and confidence intervals"),
                ("Data pipeline & statistical verification script", Capability.CODING, "Implement reproducible Python analysis script and data validation"),
                ("Clinical trial executive summary & submission", Capability.SYNTHESIS, "Synthesize findings into clinical review document"),
            ],
        },
    }

    def decompose(self, goal: str) -> List[CognitiveStagePlan]:
        """Decomposes a user goal into an ordered cognitive execution sequence."""
        # 1. Check presets
        lower_goal = goal.lower()
        for preset in self.PRESET_TASKS.values():
            if preset["query"].lower() in lower_goal or lower_goal in preset["query"].lower():
                return [
                    CognitiveStagePlan(
                        stage_index=i,
                        title=title,
                        capability=cap,
                        description=desc,
                    )
                    for i, (title, cap, desc) in enumerate(preset["stages"])
                ]

        # 2. Semantic heuristic decomposition
        stages: List[CognitiveStagePlan] = []
        step_idx = 0

        # Heuristic detection of sub-domains in query
        has_research = bool(re.search(r"paper|research|study|literature|hypothes|analy|survey", lower_goal))
        has_math = bool(re.search(r"math|equation|calculate|numerical|deriv|proof|formula|matrix|solve", lower_goal))
        has_coding = bool(re.search(r"code|implement|python|script|program|algorithm|software|test", lower_goal))
        has_physics = bool(re.search(r"physic|thermodynamic|quantum|mechanic|gravity|energy|force", lower_goal))
        has_finance = bool(re.search(r"finance|stock|trading|portfolio|risk|option|market|alpha", lower_goal))
        has_medicine = bool(re.search(r"medic|clinic|bio|drug|patient|genom|health|disease", lower_goal))
        has_vision = bool(re.search(r"image|vision|chart|diagram|photo|plot|ocr", lower_goal))

        if has_vision:
            stages.append(CognitiveStagePlan(
                stage_index=step_idx,
                title="Visual & Diagram Extraction",
                capability=Capability.VISION,
                description="Extract features, tables, charts, or images from input context",
            ))
            step_idx += 1

        if has_research or (not any([has_physics, has_finance, has_medicine, has_math, has_coding])):
            stages.append(CognitiveStagePlan(
                stage_index=step_idx,
                title="Literature & Conceptual Analysis",
                capability=Capability.RESEARCH,
                description="Deconstruct foundational principles, theoretical claims, and facts",
            ))
            step_idx += 1

        if has_medicine:
            stages.append(CognitiveStagePlan(
                stage_index=step_idx,
                title="Biomedical Pathway & Clinical Evaluation",
                capability=Capability.MEDICINE,
                description="Analyze pharmacological mechanisms and clinical evidence",
            ))
            step_idx += 1

        if has_finance:
            stages.append(CognitiveStagePlan(
                stage_index=step_idx,
                title="Financial Modeling & Quantitative Strategy",
                capability=Capability.FINANCE,
                description="Formulate econometric framework, asset dynamics, and risk parameters",
            ))
            step_idx += 1

        if has_math:
            stages.append(CognitiveStagePlan(
                stage_index=step_idx,
                title="Mathematical Proof & Numerical Solving",
                capability=Capability.MATHEMATICS,
                description="Derive equations, solve boundary problems, and compute precise values",
            ))
            step_idx += 1

        if has_physics:
            stages.append(CognitiveStagePlan(
                stage_index=step_idx,
                title="Physical Interpretation & Laws Verification",
                capability=Capability.PHYSICS,
                description="Assess conservation laws, dynamic equilibrium, and experimental bounds",
            ))
            step_idx += 1

        if has_coding:
            stages.append(CognitiveStagePlan(
                stage_index=step_idx,
                title="Algorithmic Implementation & Verification",
                capability=Capability.CODING,
                description="Write executable implementation, test cases, and simulation logic",
            ))
            step_idx += 1

        # Always end with a synthesis / final reconciliation stage
        stages.append(CognitiveStagePlan(
            stage_index=step_idx,
            title="Final Cognitive Synthesis & Delivery",
            capability=Capability.SYNTHESIS,
            description="Reconcile all specialist findings into a cohesive, structured deliverable",
        ))

        return stages
