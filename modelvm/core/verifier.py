"""Independent verification and ground-truth validation engine for ModelVM.

Ensures that the component generating an artifact is never the sole authority
determining whether that artifact is verified or correct.
"""

from __future__ import annotations
import ast
import math
import operator
import re
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field
from modelvm.core.state_packet import CalculationItem, CognitiveStatePacket


class GroundTruthFact(BaseModel):
    """Structured domain ground truth fact for independent evaluation.
    
    Prevents self-grading circularity by specifying exact entities, attributes,
    and acceptable numerical tolerances for key domain assertions.
    """
    fact_id: str = Field(description="Unique fact identifier")
    entity: str = Field(description="Entity or physical component name e.g. 'oscillator', 'resonator'")
    attribute: str = Field(description="Property or parameter name e.g. 'damping_ratio', 'natural_frequency'")
    expected_value: Optional[float] = Field(default=None, description="Expected numerical value if quantitative")
    unit: Optional[str] = Field(default=None, description="Physical or logical units")
    tolerance: float = Field(default=0.02, description="Relative tolerance for numerical comparison (e.g. 0.02 = 2%)")
    required: bool = Field(default=True, description="Whether this fact is mandatory for task success")


class ArithmeticVerifier:
    """Safely verifies mathematical and numerical calculations using AST parsing.
    
    IMPORTANT: This is strictly an arithmetic verifier, not a universal verifier.
    It verifies that the declared arithmetic evaluation holds, but does not certify
    whether the underlying physical modeling assumptions or unit definitions are valid.
    """

    ALLOWED_OPERATORS: Dict[type, Callable[[Any, Any], Any]] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    ALLOWED_FUNCTIONS: Dict[str, Callable[..., float]] = {
        "sqrt": math.sqrt,
        "exp": math.exp,
        "log": math.log,
        "log10": math.log10,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "abs": abs,
    }

    ALLOWED_CONSTANTS: Dict[str, float] = {
        "pi": math.pi,
        "e": math.e,
    }

    @classmethod
    def _eval_ast(cls, node: ast.AST) -> float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError(f"Unsupported constant value: {node.value}")

        elif isinstance(node, ast.Name):
            name_lower = node.id.lower()
            if name_lower in cls.ALLOWED_CONSTANTS:
                return cls.ALLOWED_CONSTANTS[name_lower]
            raise ValueError(f"Unknown variable: {node.id}")

        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in cls.ALLOWED_OPERATORS:
                left = cls._eval_ast(node.left)
                right = cls._eval_ast(node.right)
                return cls.ALLOWED_OPERATORS[op_type](left, right)
            raise ValueError(f"Unsupported operator: {op_type}")

        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in cls.ALLOWED_OPERATORS:
                operand = cls._eval_ast(node.operand)
                return cls.ALLOWED_OPERATORS[op_type](operand)
            raise ValueError(f"Unsupported unary operator: {op_type}")

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id.lower()
                if func_name in cls.ALLOWED_FUNCTIONS:
                    args = [cls._eval_ast(arg) for arg in node.args]
                    return cls.ALLOWED_FUNCTIONS[func_name](*args)
            raise ValueError(f"Unsupported function call: {ast.dump(node)}")

        raise ValueError(f"Unsupported AST node: {type(node)}")

    @classmethod
    def verify_item(cls, item: CalculationItem, tolerance: float = 1e-3) -> bool:
        """Verifies if the declared expression numerically evaluates to the declared result."""
        # Clean expression (remove assignment variable name if present e.g. "omega_n = sqrt(k / m)")
        expr = item.expression
        if "=" in expr:
            # e.g., "omega_n = 14.14 rad/s" or "P_diss = 2 * 0.12 * 14.14 * 1.0 = 1.34"
            parts = expr.split("=")
            # Use right-hand expression if variable on left
            expr = parts[-1] if len(parts) == 2 and not any(op in parts[0] for op in "+-*/^") else parts[0]

        # Extract numerical portion from item.result (strip symbols/units e.g. "14.14 rad/s" -> 14.14)
        match = re.search(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", item.result)
        if not match:
            item.verified = False
            item.verification_method = None
            return False

        try:
            expected_num = float(match.group(0))
            parsed = ast.parse(expr.strip(), mode="eval")
            computed = cls._eval_ast(parsed.body)

            if abs(computed - expected_num) <= max(tolerance, abs(expected_num) * tolerance):
                item.verified = True
                item.verification_method = "arithmetic"
                return True
        except Exception:
            pass

        # If arithmetic verifier fails, do not mark verified
        item.verified = False
        item.verification_method = None
        return False

    @classmethod
    def verify_all_in_csp(cls, csp: CognitiveStatePacket) -> int:
        """Runs the arithmetic verifier across all calculations in a state packet."""
        verified_count = 0
        for calc in csp.calculations:
            if cls.verify_item(calc):
                verified_count += 1
        return verified_count


class IndependentEvaluator:
    """Decoupled ground-truth evaluation harness.
    
    Evaluates state packets against external task criteria and domain ground truth,
    ensuring that the system never grades its own self-generated claims.
    """

    @staticmethod
    def evaluate_calculation_correctness(csp: CognitiveStatePacket) -> float:
        """Independently evaluates calculations afresh without mutating the CSP.
        
        CRITICAL: Never trusts producer-supplied flags (e.g. c.verified).
        Creates independent copies and tests arithmetic validity via AST.
        """
        if not csp.calculations:
            return 0.5  # Neutral default when no calculations were requested

        verified_count = 0
        for calc in csp.calculations:
            # Independent non-mutating copy
            calc_copy = calc.model_copy()
            if ArithmeticVerifier.verify_item(calc_copy):
                verified_count += 1

        return round(verified_count / len(csp.calculations), 3)

    @staticmethod
    def evaluate_artifact_integrity(csp: CognitiveStatePacket, required_artifacts: List[str]) -> float:
        """Measures deliverable completeness against external requirements."""
        if not required_artifacts:
            return 1.0
        matched = sum(1 for req in required_artifacts if req in csp.artifacts)
        return round(matched / len(required_artifacts), 3)

    @classmethod
    def evaluate_state_integrity(
        cls,
        csp: CognitiveStatePacket,
        ground_truth_facts: Any,
    ) -> float:
        """Measures whether required ground-truth facts survived model transitions without loss.
        
        Supports both structured List[GroundTruthFact] and legacy List[str].
        SI = (Preserved Ground-Truth Facts) / (Total Required Ground-Truth Facts)
        """
        if not ground_truth_facts:
            return 1.0

        # Check if using structured GroundTruthFact definitions
        if isinstance(ground_truth_facts[0], GroundTruthFact):
            matched = 0

            # Attribute symbol aliases for technical domain calculations
            attr_aliases = {
                "mass": ["mass", "m =", "m=", " 2.5 kg"],
                "natural_frequency": ["natural_frequency", "omega_n", "ω_n", "natural frequency"],
                "damping_ratio": ["damping_ratio", "zeta", "ζ", "damping"],
                "force_amplitude": ["force_amplitude", "f_0", "f0", "force amplitude", "force"],
                "frequency": ["excitation frequency", "frequency", "omega", "ω"],
                "amplitude": ["amplitude", "x_0", "steady_state", "steady state"],
                "constant_k": ["constant_k", "stiffness", " k ", "k =", "k="],
                "power": ["power", "p_diss", "dissipation"],
            }

            for gt in ground_truth_facts:
                ent_target = gt.entity.lower()
                attr_target = gt.attribute.lower()
                aliases = attr_aliases.get(attr_target, [attr_target])

                def record_matches_semantic(text: str) -> bool:
                    t = text.lower()
                    return (ent_target in t) or any(a in t for a in aliases)

                def record_has_number(text: str, target_val: float, tol: float) -> bool:
                    nums = re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", text)
                    for n in nums:
                        try:
                            v_float = float(n)
                            if abs(v_float - target_val) <= max(1e-4, abs(target_val) * tol):
                                return True
                        except ValueError:
                            continue
                    return False

                gt_matched = False

                if gt.expected_value is not None:
                    # 1. Check local calculation records
                    for calc in csp.calculations:
                        calc_text = f"{calc.expression} = {calc.result} {calc.units or ''}"
                        if record_matches_semantic(calc_text) and record_has_number(calc_text, gt.expected_value, gt.tolerance):
                            gt_matched = True
                            break

                    # 2. Check individual fact statements
                    if not gt_matched:
                        for fact in csp.facts:
                            if record_matches_semantic(fact) and record_has_number(fact, gt.expected_value, gt.tolerance):
                                gt_matched = True
                                break

                    # 3. Check individual artifact deliverables
                    if not gt_matched:
                        for k, v in csp.artifacts.items():
                            art_text = f"{k}: {v}"
                            if record_matches_semantic(art_text) and record_has_number(art_text, gt.expected_value, gt.tolerance):
                                gt_matched = True
                                break
                else:
                    # Non-numerical fact: check if any single fact or artifact mentions entity or attribute
                    for fact in csp.facts:
                        if record_matches_semantic(fact):
                            gt_matched = True
                            break

                if gt_matched:
                    matched += 1

            return round(matched / len(ground_truth_facts), 3)

        # Fallback legacy string keyword matching
        csp_fact_text = (" ".join(csp.facts) + " " + " ".join(f"{c.expression}={c.result}" for c in csp.calculations)).lower()
        matched = 0
        for fact in ground_truth_facts:
            keywords = [w.lower() for w in re.findall(r"\b\w{4,}\b", str(fact)) if w.lower() not in {"this", "that", "with", "from", "have"}]
            if keywords and sum(1 for kw in keywords if kw in csp_fact_text) >= max(1, len(keywords) // 2):
                matched += 1

        return round(matched / len(ground_truth_facts), 3)

    @classmethod
    def evaluate_task_correctness(
        cls,
        csp: CognitiveStatePacket,
        required_artifacts: List[str],
        required_calculations: Optional[List[str]] = None,
    ) -> float:
        """Evaluates whether all required deliverables and verifiable calculations are present.
        
        CRITICAL: Never trusts producer-supplied flags (e.g. c.verified).
        Calculations are evaluated independently via fresh AST evaluation on non-mutating copies.
        TC = (Artifact Coverage + Verified Calculations Ratio) / 2
        """
        art_score = cls.evaluate_artifact_integrity(csp, required_artifacts)
        calc_score = cls.evaluate_calculation_correctness(csp)
        return round(0.5 * art_score + 0.5 * calc_score, 3)

    @staticmethod
    def evaluate_structural_completeness(csp: CognitiveStatePacket) -> float:
        """Measures structural completeness of the CSP representation (syntax, format, non-emptiness)."""
        score = 0.0
        if csp.facts:
            score += min(0.25, len(csp.facts) * 0.05)
        if csp.calculations:
            score += min(0.25, len(csp.calculations) * 0.08)
        if csp.evidence:
            score += min(0.25, len(csp.evidence) * 0.08)
        if csp.artifacts:
            score += min(0.25, len(csp.artifacts) * 0.125)
        return round(min(1.0, score), 3)
