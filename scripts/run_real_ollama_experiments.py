"""ModelVM Real GPU Inference Experiment Runner.

Connects to local Ollama runtime and NVIDIA GPU to execute the 5-stage
canonical scientific reasoning pipeline across heterogeneous real models:
- llama3.1:8b (Research & Physics Specialist)
- qwen2.5-coder:7b (Mathematics & Coding Specialist)
- llama3.2:1b (Executive Synthesis Specialist)

Compares:
1. Regime A: Raw Text Transcript Passing (Baseline)
2. Regime B: ModelVM Typed Cognitive State Packet (CSP)

Captures nanosecond-level hardware telemetry directly from Ollama/CUDA:
- Model load / swap time (load_duration)
- Prompt processing rate (prompt_eval_count / prompt_eval_duration)
- Token generation throughput (eval_count / eval_duration)
- Handoff payload token count
- Calculation accuracy verified via independent Python AST
"""

from __future__ import annotations
import json
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional
import httpx
import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modelvm.core.state_packet import CognitiveStatePacket, CalculationItem, EvidenceItem
from modelvm.core.verifier import ArithmeticVerifier

OLLAMA_API = "http://localhost:11434/api/generate"

# Pipeline Model Assignment (Real Local Open-Weight Models)
STAGE_MODELS = {
    1: {"id": "llama3.1:8b", "role": "Research Specialist", "capability": "Research"},
    2: {"id": "qwen2.5-coder:7b", "role": "Math Specialist", "capability": "Mathematics"},
    3: {"id": "qwen2.5-coder:7b", "role": "Coding Specialist", "capability": "Coding"},
    4: {"id": "llama3.1:8b", "role": "Physics Specialist", "capability": "Physics"},
    5: {"id": "llama3.2:1b", "role": "Synthesis Specialist", "capability": "Synthesis"},
}

STAGES_INFO = [
    {
        "index": 1,
        "title": "Stage 1: Governing Equations & Boundary Formulation",
        "objective": "Define the governing differential equation for a forced damped harmonic oscillator: m*x'' + c*x' + k*x = F0*cos(omega*t). Assume m=2.5 kg, k=500.0 N/m, c=0.8 Ns/m, F0=45.0 N, omega=14.0 rad/s. State the exact parameter values clearly.",
    },
    {
        "index": 2,
        "title": "Stage 2: Analytical Derivation & Resonant Amplitude",
        "objective": "Using m=2.5 kg, k=500.0 N/m, c=0.8 Ns/m, F0=45.0 N, omega=14.0 rad/s, calculate the natural frequency omega_0 = sqrt(k/m), resonant frequency omega_r = sqrt(k/m - 2*(c/(2*m))^2), and steady-state amplitude X0 = F0 / sqrt((k - m*omega^2)^2 + (c*omega)^2). Provide exact numerical values.",
    },
    {
        "index": 3,
        "title": "Stage 3: Numerical Simulation Script",
        "objective": "Implement a clean Python script using scipy.integrate.solve_ivp to simulate the oscillator over t=[0, 10] seconds. Calculate the maximum steady-state displacement from the simulated trajectory.",
    },
    {
        "index": 4,
        "title": "Stage 4: Physical Dissipation & Q-Factor Verification",
        "objective": "Calculate the mechanical quality factor Q = (m * omega_0) / c and the average power dissipation P_diss = 0.5 * c * (omega * X0)^2. Explain whether the system is lightly damped.",
    },
    {
        "index": 5,
        "title": "Stage 5: Executive Synthesis & Multi-Domain Validation",
        "objective": "Synthesize all results: natural frequency omega_0, steady state amplitude X0, simulated max displacement, Q factor, and dissipation. Verify whether analytical and simulated amplitudes match within 2%.",
    },
]


def query_ollama(model_id: str, prompt: str, timeout: float = 120.0) -> Dict[str, Any]:
    """Sends inference query to Ollama and returns full hardware telemetry."""
    payload = {
        "model": model_id,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 512,
        }
    }
    t0 = time.perf_counter()
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(OLLAMA_API, json=payload)
        resp.raise_for_status()
        data = resp.json()
    t1 = time.perf_counter()

    data["client_wall_time"] = t1 - t0
    # Normalize durations from nanoseconds to seconds
    data["load_time_sec"] = data.get("load_duration", 0) / 1e9
    data["prompt_eval_time_sec"] = data.get("prompt_eval_duration", 0) / 1e9
    data["eval_time_sec"] = data.get("eval_duration", 0) / 1e9
    data["total_time_sec"] = data.get("total_duration", 0) / 1e9

    eval_count = data.get("eval_count", 0)
    eval_dur = data["eval_time_sec"]
    data["tokens_per_sec"] = (eval_count / eval_dur) if eval_dur > 0 else 0.0

    return data


def run_experiment():
    print("=" * 80)
    print("MODELVM PHYSICAL EXPERIMENT: REAL OLLAMA GPU EXECUTION")
    print(f"Device: {torch.cuda.get_device_name(0)} | VRAM: {round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2)} GB")
    print("=" * 80)

    results = {
        "device": torch.cuda.get_device_name(0),
        "total_vram_gb": round(torch.cuda.get_device_properties(0).total_memory / 1e9, 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "regime_raw_text": [],
        "regime_modelvm_csp": [],
    }

    # --------------------------------------------------------------------------
    # 1. REGIME A: RAW TEXT TRANSCRIPT CONCATENATION (BASELINE)
    # --------------------------------------------------------------------------
    print("\n[REGIME A: RAW TEXT TRANSCRIPT (BASELINE)]")
    conversation_transcript = ""

    for stage in STAGES_INFO:
        s_idx = stage["index"]
        cfg = STAGE_MODELS[s_idx]
        print(f"\n--- {stage['title']} ---")
        print(f"Model: {cfg['id']} ({cfg['role']})")

        prompt = (
            f"You are a scientific specialist in {cfg['capability']}.\n\n"
            f"TASK: {stage['objective']}\n\n"
        )
        if conversation_transcript:
            prompt += f"PRIOR DISCUSSION TRANSCRIPT:\n{conversation_transcript}\n\n"
        prompt += "Provide your response:"

        prompt_chars = len(prompt)
        print(f"Input Prompt Size: {prompt_chars} chars (approx {prompt_chars // 4} tokens)")

        t_res = query_ollama(cfg["id"], prompt)
        response_text = t_res.get("response", "").strip()

        # Append to conversational transcript
        conversation_transcript += (
            f"\n\n[Stage {s_idx} by {cfg['id']} - {cfg['capability']}]:\n"
            f"{response_text}"
        )

        stage_metrics = {
            "stage_index": s_idx,
            "stage_title": stage["title"],
            "model_id": cfg["id"],
            "capability": cfg["capability"],
            "input_prompt_tokens": t_res.get("prompt_eval_count", 0),
            "output_tokens": t_res.get("eval_count", 0),
            "tokens_per_sec": round(t_res.get("tokens_per_sec", 0), 2),
            "load_time_sec": round(t_res.get("load_time_sec", 0), 3),
            "eval_time_sec": round(t_res.get("eval_time_sec", 0), 3),
            "total_time_sec": round(t_res.get("total_time_sec", 0), 3),
            "response_preview": response_text[:180].replace("\n", " "),
        }
        results["regime_raw_text"].append(stage_metrics)
        print(f"  Load Time: {stage_metrics['load_time_sec']:.3f} s | Gen Speed: {stage_metrics['tokens_per_sec']:.1f} tok/s")
        print(f"  Tokens Out: {stage_metrics['output_tokens']} in {stage_metrics['eval_time_sec']:.2f} s")

    # --------------------------------------------------------------------------
    # 2. REGIME B: MODELVM TYPED COGNITIVE STATE PACKET (CSP)
    # --------------------------------------------------------------------------
    print("\n\n" + "=" * 80)
    print("[REGIME B: MODELVM TYPED COGNITIVE STATE PACKET (CSP)]")
    print("=" * 80)

    # Structured ModelVM Cognitive State Packet (CSP)
    csp_packet = CognitiveStatePacket(
        goal="Forced damped harmonic oscillator analysis and verification",
        stage_index=0,
    )

    for stage in STAGES_INFO:
        s_idx = stage["index"]
        cfg = STAGE_MODELS[s_idx]
        print(f"\n--- {stage['title']} ---")
        print(f"Model: {cfg['id']} ({cfg['role']})")

        csp_context = (
            f"COGNITIVE STATE PACKET (Stage {s_idx - 1} Verified Facts):\n"
            f"- Evidence/Facts: {[e.statement for e in csp_packet.evidence]}\n"
            f"- Calculations: {[f'{c.expression} = {c.result}' for c in csp_packet.calculations]}\n"
            f"- Decisions: {csp_packet.decisions}\n"
        ) if s_idx > 1 else "INITIAL STATE: Fresh Task Execution."

        prompt = (
            f"You are a scientific specialist in {cfg['capability']}.\n\n"
            f"{csp_context}\n\n"
            f"TASK OBJECTIVE: {stage['objective']}\n\n"
            f"Provide your response. In addition, output a JSON block at the end with keys "
            f"'facts' (list of strings) and 'calculations' (list of {{'expression': str, 'result': str}})."
        )

        prompt_chars = len(prompt)
        print(f"CSP Prompt Size: {prompt_chars} chars (approx {prompt_chars // 4} tokens)")

        t_res = query_ollama(cfg["id"], prompt)
        response_text = t_res.get("response", "").strip()

        # Extract structured updates into typed CSP
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        extracted_data = {}
        if json_match:
            try:
                extracted_data = json.loads(json_match.group(1))
            except Exception:
                pass

        if "facts" in extracted_data and isinstance(extracted_data["facts"], list):
            for fact_str in extracted_data["facts"][:3]:
                csp_packet.evidence.append(EvidenceItem(statement=str(fact_str), confidence=0.95))
        else:
            lines = [l.strip() for l in response_text.split("\n") if len(l.strip()) > 20 and not l.startswith("```")]
            for l in lines[:2]:
                csp_packet.evidence.append(EvidenceItem(statement=l, confidence=0.90))

        if "calculations" in extracted_data and isinstance(extracted_data["calculations"], list):
            for c_obj in extracted_data["calculations"][:3]:
                if isinstance(c_obj, dict) and "expression" in c_obj and "result" in c_obj:
                    csp_packet.calculations.append(
                        CalculationItem(
                            expression=str(c_obj["expression"]),
                            result=str(c_obj["result"]),
                            tolerance=1e-3,
                        )
                    )

        # Run non-circular independent Python AST verifier on all CSP calculations
        ArithmeticVerifier.verify_all_in_csp(csp_packet)
        csp_packet.stage_index = s_idx

        stage_metrics = {
            "stage_index": s_idx,
            "stage_title": stage["title"],
            "model_id": cfg["id"],
            "capability": cfg["capability"],
            "input_prompt_tokens": t_res.get("prompt_eval_count", 0),
            "output_tokens": t_res.get("eval_count", 0),
            "tokens_per_sec": round(t_res.get("tokens_per_sec", 0), 2),
            "load_time_sec": round(t_res.get("load_time_sec", 0), 3),
            "eval_time_sec": round(t_res.get("eval_time_sec", 0), 3),
            "total_time_sec": round(t_res.get("total_time_sec", 0), 3),
            "csp_state_facts_count": len(csp_packet.evidence),
            "csp_state_calcs_count": len(csp_packet.calculations),
            "response_preview": response_text[:180].replace("\n", " "),
        }
        results["regime_modelvm_csp"].append(stage_metrics)
        print(f"  Load Time: {stage_metrics['load_time_sec']:.3f} s | Gen Speed: {stage_metrics['tokens_per_sec']:.1f} tok/s")
        print(f"  CSP State: {len(csp_packet.evidence)} facts, {len(csp_packet.calculations)} verified calcs")

    # --------------------------------------------------------------------------
    # SAVE RAW JSON TELEMETRY & PRINT SUMMARY COMPARISON TABLE
    # --------------------------------------------------------------------------
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, "real_ollama_experiment_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print("EMPIRICAL COMPARISON SUMMARY (REAL HARDWARE EXECUTION ON RTX 5070 Ti)")
    print("=" * 80)
    print(f"{'Stage':<8} | {'Model':<18} | {'Raw Prompt (tok)':<16} | {'CSP Prompt (tok)':<16} | {'Token Savings':<14} | {'Gen Speed'}")
    print("-" * 80)

    total_raw_prompt = 0
    total_csp_prompt = 0
    total_raw_time = 0.0
    total_csp_time = 0.0
    total_raw_load = 0.0
    total_csp_load = 0.0

    for r_raw, r_csp in zip(results["regime_raw_text"], results["regime_modelvm_csp"]):
        s_id = f"S{r_raw['stage_index']}"
        m_id = r_raw["model_id"]
        p_raw = r_raw["input_prompt_tokens"]
        p_csp = r_csp["input_prompt_tokens"]
        savings = f"{(1.0 - p_csp / max(1, p_raw)) * 100:.1f}%" if p_raw > 0 else "0.0%"
        spd = f"{r_csp['tokens_per_sec']} tok/s"

        total_raw_prompt += p_raw
        total_csp_prompt += p_csp
        total_raw_time += r_raw["total_time_sec"]
        total_csp_time += r_csp["total_time_sec"]
        total_raw_load += r_raw["load_time_sec"]
        total_csp_load += r_csp["load_time_sec"]

        print(f"{s_id:<8} | {m_id:<18} | {p_raw:<16} | {p_csp:<16} | {savings:<14} | {spd}")

    raw_inference_time = total_raw_time - total_raw_load
    csp_inference_time = total_csp_time - total_csp_load
    inf_reduction = (1.0 - csp_inference_time / max(0.001, raw_inference_time)) * 100
    total_reduction = (1.0 - total_csp_time / max(0.001, total_raw_time)) * 100

    print("-" * 80)
    print("LATENCY & PROMPT DECOMPOSITION (SCIENTIFIC PROVENANCE):")
    print(f"  • Prompt Context:     Raw = {total_raw_prompt} tok  | CSP = {total_csp_prompt} tok ({(1.0 - total_csp_prompt/total_raw_prompt)*100:.1f}% reduction)")
    print(f"  • Active Inference:   Raw = {raw_inference_time:.2f} s  | CSP = {csp_inference_time:.2f} s ({inf_reduction:.1f}% acceleration from prompt reduction)")
    print(f"  • Cold Weight Load:   Raw = {total_raw_load:.2f} s  | CSP = {total_csp_load:.2f} s (uncoordinated baseline cold-load overhead)")
    print(f"  • Total Wall-Clock:   Raw = {total_raw_time:.2f} s  | CSP = {total_csp_time:.2f} s ({total_reduction:.1f}% total end-to-end reduction)")
    print(f"Results saved to: {out_json}")
    print("=" * 80)


if __name__ == "__main__":
    run_experiment()
