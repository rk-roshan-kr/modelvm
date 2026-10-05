"""Execution backends: Simulation engine and real local inference connectors."""

from __future__ import annotations
import json
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import httpx

from modelvm.core.manifest import ModelManifest
from modelvm.core.state_packet import (
    CalculationItem,
    CognitiveStatePacket,
    EvidenceItem,
    StageTrace,
)
from modelvm.core.types import Capability, ExecutionMode
from modelvm.core.verifier import ArithmeticVerifier


class ModelBackend(ABC):
    """Abstract interface for executing inference on a paged model."""

    @abstractmethod
    def execute_stage(
        self,
        model: ModelManifest,
        stage_title: str,
        stage_description: str,
        capability: Capability,
        input_csp: CognitiveStatePacket,
    ) -> CognitiveStatePacket:
        """Executes a cognitive reasoning stage with the given model and state packet."""
        pass


class SimulationBackend(ModelBackend):
    """Deterministic, high-fidelity cognitive simulation backend.
    
    Generates rich, domain-specific scientific and engineering outputs,
    emulates inference token latency, and produces valid Cognitive State Packets.
    """

    def execute_stage(
        self,
        model: ModelManifest,
        stage_title: str,
        stage_description: str,
        capability: Capability,
        input_csp: CognitiveStatePacket,
    ) -> CognitiveStatePacket:
        start_time = time.time()
        
        # Emulate token generation delay based on model latency
        emulated_delay = min(0.6, model.latency * 15.0)
        time.sleep(emulated_delay)

        new_csp = CognitiveStatePacket(
            goal=input_csp.goal,
            stage_index=input_csp.stage_index + 1,
            current_capability=capability.value,
        )

        # Domain-specific cognitive generation
        if capability == Capability.RESEARCH:
            new_csp.facts = [
                "Governing dynamic system equation: d²x/dt² + 2ζω_n(dx/dt) + ω_n²x = F_0 cos(ωt) / m",
                "Assumed parameter values: m = 2.5 kg, natural frequency ω_n = 14.2 rad/s, damping ratio ζ = 0.12",
                "Driving force amplitude F_0 = 45.0 N at excitation frequency ω = 13.8 rad/s",
            ]
            new_csp.assumptions = [
                "System operates in linear elastic regime without plastic deformation",
                "Viscous air damping is constant across thermodynamic temperature bounds",
            ]
            new_csp.evidence = [
                EvidenceItem(claim="Resonance peak occurs near ω/ω_n ≈ 0.97", source="Section 3.2 Literature Derivation", confidence=0.94),
                EvidenceItem(claim="Magnification factor Q ≈ 1 / (2ζ) = 4.167", source="Equation (14) Benchmark", confidence=0.96),
            ]
            new_csp.next_capability = Capability.MATHEMATICS.value

        elif capability == Capability.MATHEMATICS:
            new_csp.calculations = [
                CalculationItem(expression="omega_resonance = 14.2 * sqrt(1 - 2 * 0.12**2)", result="13.993", units="rad/s"),
                CalculationItem(expression="k = 2.5 * 14.2**2", result="504.1", units="N/m"),
                CalculationItem(expression="steady_state_amplitude = 45.0 / 504.1", result="0.0893", units="m"),
                CalculationItem(expression="peak_kinetic_energy = 0.5 * 2.5 * (13.8 * 0.0893)**2", result="1.898", units="Joules"),
            ]
            new_csp.facts = [
                "Closed-form steady state amplitude confirmed at 89.3 mm",
                "Natural frequency stiffness constant k calculated at 504.1 N/m",
            ]
            new_csp.next_capability = Capability.CODING.value

        elif capability == Capability.CODING:
            sim_code = (
                "import numpy as np\n"
                "from scipy.integrate import solve_ivp\n\n"
                "# Parameters\n"
                "m, omega_n, zeta, F0, omega = 2.5, 14.2, 0.12, 45.0, 13.8\n"
                "k = m * omega_n**2\n\n"
                "def harmonic_oscillator(t, y):\n"
                "    x, v = y\n"
                "    dxdt = v\n"
                "    dvdt = (F0*np.cos(omega*t) - 2*zeta*omega_n*m*v - k*x) / m\n"
                "    return [dxdt, dvdt]\n\n"
                "sol = solve_ivp(harmonic_oscillator, [0, 10], [0.0, 0.0], t_eval=np.linspace(0, 10, 1000))\n"
                "print(f'Max simulated displacement: {np.max(np.abs(sol.y[0][-200:])):.4f} m')\n"
            )
            new_csp.artifacts["simulation_code.py"] = sim_code
            new_csp.decisions = [
                "Selected SciPy solve_ivp with RK45 adaptive integration for high numerical stability",
                "Sampled 1000 trajectory points over 10 second steady-state horizon",
            ]
            new_csp.facts = [
                "Numerical simulation converged with residual error < 1e-6 relative to analytical formula",
            ]
            new_csp.next_capability = Capability.PHYSICS.value

        elif capability == Capability.PHYSICS:
            new_csp.facts = [
                "Energy dissipation rate P_diss = 2 * zeta * omega_n * m * (omega * X_0)^2 / 2 = 1.34 Watts",
                "Mechanical Q-factor is high enough to induce transient ring-down time of tau = 1 / (zeta * omega_n) = 0.587 s",
            ]
            new_csp.evidence = [
                EvidenceItem(claim="System is sub-critically damped (zeta=0.12 < 1.0), exhibiting pronounced resonance amplification", source="Dynamical Stability Theorem", confidence=0.98),
            ]
            new_csp.next_capability = Capability.SYNTHESIS.value

        elif capability == Capability.FINANCE:
            new_csp.calculations = [
                CalculationItem(expression="annualized_sharpe_ratio = (mean_excess_return / std_return) * sqrt(252)", result="2.34", verified=True),
                CalculationItem(expression="max_drawdown = min(cumulative_wealth / peak_wealth - 1.0)", result="-6.8", units="%", verified=True),
                CalculationItem(expression="var_99_1day = portfolio_value * (mu - 2.33 * sigma)", result="$42,850", verified=True),
            ]
            new_csp.facts = [
                "Strategy shows high risk-adjusted performance with constrained 99% 1-day Value-at-Risk under $50k",
            ]
            new_csp.next_capability = Capability.SYNTHESIS.value

        elif capability == Capability.MEDICINE:
            new_csp.facts = [
                "Target receptor affinity Kd = 2.4 nM indicates high selectivity against off-target homologues",
                "Adverse event incidence in treatment arm (4.1%) vs control (3.9%), p = 0.62 (not statistically significant)",
            ]
            new_csp.calculations = [
                CalculationItem(expression="hazard_ratio = exp(beta_treatment)", result="0.58", units="95% CI [0.44 - 0.76]", verified=True),
                CalculationItem(expression="p_value_log_rank", result="0.00018", verified=True),
            ]
            new_csp.next_capability = Capability.SYNTHESIS.value

        else:  # SYNTHESIS / GENERAL
            new_csp.facts = [
                "All cross-domain hypotheses and derivations verified end-to-end",
                "Analytical, numerical, and software artifacts synthesized into executive report",
            ]
            new_csp.decisions = [
                "Final deliverable validated across all constraint boundaries",
            ]
            new_csp.artifacts["executive_summary.md"] = (
                f"# ModelVM Cognitive Execution Report\n\n"
                f"**Task Objective**: {input_csp.goal}\n\n"
                f"### Consolidated Findings\n"
                f"- Successfully routed through specialist models in a dynamic memory envelope.\n"
                f"- Preserved cross-domain calculations, assumptions, and artifacts via Cognitive State Packets.\n"
                f"- Verified analytical, numerical, and physical boundaries with zero state degradation."
            )

        # Reflect domain competence & capability fit
        fit = model.capability_score(capability) * model.quality
        if fit < 0.70:
            new_csp.uncertainties.append(
                f"Model {model.name} domain fit is limited ({fit:.2f}) for {capability.value}"
            )
            # Models with poor domain fit generate calculation inaccuracies that fail arithmetic verification
            for c in new_csp.calculations:
                match = re.search(r"[-+]?(?:\d*\.\d+|\d+)", c.result)
                if match:
                    try:
                        v = float(match.group(0))
                        c.result = c.result.replace(match.group(0), f"{v * 1.18:.2f}")
                    except ValueError:
                        pass
            for e in new_csp.evidence:
                e.confidence = round(e.confidence * 0.70, 3)

        # Reflect state degradation if prior facts were lost (e.g. configurations without CSP)
        if capability in (Capability.MATHEMATICS, Capability.CODING, Capability.PHYSICS) and len(input_csp.facts) < 2:
            new_csp.uncertainties.append(
                f"State degradation: missing prior foundational facts at stage {input_csp.stage_index}"
            )
            if new_csp.calculations:
                c0 = new_csp.calculations[0]
                match0 = re.search(r"[-+]?(?:\d*\.\d+|\d+)", c0.result)
                if match0:
                    try:
                        v0 = float(match0.group(0))
                        c0.result = c0.result.replace(match0.group(0), f"{v0 * 1.25:.2f}")
                    except ValueError:
                        pass
            if new_csp.evidence:
                new_csp.evidence[0].confidence = round(new_csp.evidence[0].confidence * 0.80, 3)

        # Run independent arithmetic verification on all generated calculations
        ArithmeticVerifier.verify_all_in_csp(new_csp)

        duration = time.time() - start_time
        new_csp.history_trace.append(
            StageTrace(
                stage_index=input_csp.stage_index,
                capability=capability.value,
                model_id=model.id,
                model_name=model.name,
                action_taken=stage_title,
                duration_sec=duration,
            )
        )

        return new_csp


class OllamaBackend(ModelBackend):
    """Connects to a running local Ollama daemon with strict execution enforcement."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        mode: ExecutionMode = ExecutionMode.REAL,
    ):
        self.base_url = base_url
        self.mode = mode
        self.fallback = SimulationBackend()

    def execute_stage(
        self,
        model: ModelManifest,
        stage_title: str,
        stage_description: str,
        capability: Capability,
        input_csp: CognitiveStatePacket,
    ) -> CognitiveStatePacket:
        # If in explicit simulation mode, route directly to the simulation engine
        if self.mode == ExecutionMode.SIMULATION:
            return self.fallback.execute_stage(model, stage_title, stage_description, capability, input_csp)

        prompt = (
            f"You are {model.name}, a specialist in {capability.value.upper()}.\n\n"
            f"TASK STAGE: {stage_title}\n"
            f"OBJECTIVE: {stage_description}\n\n"
            f"{input_csp.to_prompt_context()}\n\n"
            f"Emit your reasoning and updated facts, calculations, and decisions. "
            f"Format structured updates in a ```json code block."
        )

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    f"{self.base_url}/api/generate",
                    json={"model": model.id, "prompt": prompt, "stream": False},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    response_text = data.get("response", "")
                    extracted_csp = CognitiveStatePacket.extract_from_text(
                        goal=input_csp.goal,
                        text=response_text,
                        stage_index=input_csp.stage_index + 1,
                    )
                    # Run independent arithmetic verification on extracted calculations
                    ArithmeticVerifier.verify_all_in_csp(extracted_csp)
                    return extracted_csp
                else:
                    error_msg = f"HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            error_msg = str(e)

        # STRICT_REAL mode strictly forbids silent fallback to simulation
        if self.mode == ExecutionMode.STRICT_REAL:
            raise RuntimeError(
                f"[STRICT_REAL Violation] Ollama daemon inference failed for model '{model.id}' "
                f"at {self.base_url}: {error_msg}. Silent simulation fallback is disabled."
            )

        # In standard REAL mode, warn transparently before fallback
        print(
            f"[OllamaBackend] WARNING: Real inference failed ({error_msg}). "
            f"Falling back to high-fidelity simulation engine."
        )
        return self.fallback.execute_stage(model, stage_title, stage_description, capability, input_csp)
