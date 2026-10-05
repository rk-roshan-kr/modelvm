# ModelVM — Virtual Memory for Intelligence

> **A local AI runtime that treats open-weight models as pageable cognitive resources rather than permanently loaded applications under a strict memory budget.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-cyan.svg)](https://www.python.org/)
[![ModelVM Architecture](https://img.shields.io/badge/Architecture-Cognitive%20OS-brightgreen.svg)](#architecture)
[![Active Budget](https://img.shields.io/badge/Active%20RAM-8.0%20GB%20Envelope-magenta.svg)](#demonstration)
[![Library Footprint](https://img.shields.io/badge/Library-52.7%20GB%20%2810%20Models%29-orange.svg)](#model-library)

---

## 1. Core Insight

Operating systems solved physical memory limitations decades ago with **Virtual Memory**: pages are brought into RAM on demand, working sets are predicted, and unused pages are paged back to disk.

**ModelVM applies this architectural principle to local AI:**

| Operating System | ModelVM Cognitive Architecture |
| :--- | :--- |
| **Process** | AI Capability (e.g. Research, Math, Coding, Physics, Medicine) |
| **RAM / VRAM** | Active Model Memory (Strict Budget, e.g. 8.0 GB) |
| **Storage / Disk** | Model Library (e.g. 52.7 GB Open-Weight Catalog) |
| **Page-In** | Load Model into memory |
| **Page-Out** | Unload Model from memory |
| **Page Cache** | Resident Model Cache (0s reload latency) |
| **Prefetch** | Predict next required model & load into spare memory |
| **Working Set** | Predicted sequence of required models $W(t, k)$ |
| **Scheduler** | Resource-Aware Cognitive Scheduler |
| **Process State** | **Cognitive State Packet (CSP)** |

---

## 2. Proposed Architecture

```text
                         USER TASK
                             │
                             ▼
                  ┌─────────────────────┐
                  │   COGNITIVE KERNEL  │
                  │                     │
                  │ Task decomposition  │
                  │ Capability matching │
                  │ Resource awareness  │
                  │ Confidence control  │
                  │ Working-set predict │
                  └──────────┬──────────┘
                             │
                 ┌───────────▼───────────┐
                 │    MODEL SCHEDULER    │
                 │ capability × resource │
                 │ × future demand       │
                 └───────────┬───────────┘
                             │
                  ┌──────────▼──────────┐
                  │    MODEL PAGER      │
                  │                     │
                  │ load / evict / cache│
                  │ RAM budget          │
                  │ load-cost awareness │
                  └──────────┬──────────┘
                             │
       ┌─────────────────────┼─────────────────────┐
       ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Research     │      │ Mathematics  │      │ Coding       │
│ Expert       │      │ Expert       │      │ Expert       │
│ (3.1 GB)     │      │ (2.4 GB)     │      │ (3.0 GB)     │
└──────────────┘      └──────────────┘      └──────────────┘

                + 7 additional open-weight models (52.7 GB Total)
```

---

## 3. Cognitive State Packet (CSP)

Heterogeneous open-weight models feature varying architectures, context windows, and tokenizers. They do not share hidden states.

ModelVM transfers context through a standardized, model-neutral **Cognitive State Packet**:

```json
{
  "goal": "Analyze scientific paper, reproduce numerical result, and write implementation",
  "stage_index": 2,
  "current_capability": "mathematics",
  "facts": [
    "Governing dynamic system equation: d²x/dt² + 2ζω_n(dx/dt) + ω_n²x = F_0 cos(ωt) / m",
    "Closed-form steady state amplitude confirmed at 108.2 mm"
  ],
  "calculations": [
    {
      "expression": "omega_resonance = omega_n * sqrt(1 - 2*zeta^2)",
      "result": "14.095",
      "units": "rad/s",
      "verified": true
    }
  ],
  "evidence": [
    {
      "claim": "Resonance peak occurs near ω/ω_n ≈ 0.97",
      "source": "Section 3.2 Literature Derivation",
      "confidence": 0.94
    }
  ],
  "assumptions": [
    "System operates in linear elastic regime without plastic deformation"
  ],
  "uncertainties": [],
  "decisions": [
    "Selected SciPy solve_ivp with RK45 adaptive integration"
  ],
  "open_questions": [],
  "next_capability": "coding",
  "artifacts": {
    "simulation_code.py": "import numpy as np..."
  }
}
```

---

## 4. Resource-Aware Scheduling

Model selection is formulated as a multi-objective systems problem:

$$Score(m) = F_{\text{capability}} - \alpha M_{\text{cost}} - \beta L_{\text{load}} - \gamma E_{\text{energy}} - \delta E_{\text{eviction}} + \eta F_{\text{future}}$$

Where:
* $F_{\text{capability}}$: Capability fit $\times$ Model quality score
* $M_{\text{cost}} = \frac{\text{RAM}_{\text{required}}}{\text{RAM}_{\text{budget}}}$: Normalized memory footprint
* $L_{\text{load}}$: Loading latency ($0.0$ if already resident in memory cache!)
* $E_{\text{energy}}$: Energy and computational complexity factor
* $E_{\text{eviction}}$: Eviction penalty incurred if loading forces eviction of active models
* $F_{\text{future}}$: Bonus if model matches upcoming stages in predicted working set $W(t, k)$

---

## 5. Model Library (52.7 GB Open-Weight Catalog)

| Model ID | Model Name | Primary Capabilities | RAM Footprint | Load Time | Quality |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `research-expert` | Mistral-Research-7B | Research, Science | 3.1 GB | 1.2s | 92% |
| `mathematics-expert` | Qwen-Math-7B | Mathematics | 2.4 GB | 0.9s | 96% |
| `coding-expert` | DeepSeek-Coder-6.7B | Coding | 3.0 GB | 1.1s | 94% |
| `physics-expert` | Llama-Physics-8B | Physics, Science | 3.2 GB | 1.3s | 90% |
| `general-reasoner` | Llama-3.1-8B-Instruct | General, Research | 7.1 GB | 2.1s | 91% |
| `multimodal-vision` | Phi-3.5-Vision-4.2B | Vision | 5.6 GB | 1.7s | 88% |
| `code-auditor` | StarCoder2-15B-Q4 | Security, Coding | 7.2 GB | 2.5s | 92% |
| `biomedical-expert` | Bio-Mistral-7B | Medicine, Science | 6.8 GB | 2.2s | 93% |
| `financial-analyst` | Fin-LLaMA-8B | Finance, Mathematics | 6.7 GB | 2.0s | 89% |
| `synthesizer-master` | Command-R-14B | Synthesis, Writing | 7.6 GB | 2.7s | 96% |

**Total Library Size:** **52.7 GB**  
**Max Single Model:** **7.6 GB** (Operates entirely within an 8.0 GB RAM envelope)

---

## 6. Real Silicon Hardware Benchmarks (NVIDIA GeForce RTX 5070 Ti)

In addition to discrete event simulations, ModelVM was physically benchmarked against an **NVIDIA GeForce RTX 5070 Ti (17.09 GB VRAM, CUDA 12.0)** running local open-weight checkpoints (`llama3.1:8b`, `qwen2.5-coder:7b`, `llama3.2:1b`) through the production C++/CUDA Ollama daemon (`scripts/run_real_ollama_experiments.py`):

| Physical Metric | Raw Unstructured Baseline | ModelVM (with CSP State Virtualization) | Delta / Improvement |
| :--- | :--- | :--- | :--- |
| **Cumulative Prompt Tokens** | 4,291 tokens | **1,683 tokens** | **−60.8% context reduction** |
| **Stage 5 Prompt Depth** | 1,446 tokens | **379 tokens** | **−73.8% token bloat reduction** |
| **Total Pipeline Wall Time** | 65.05 s | **14.85 s** | **−77.2% latency reduction (4.38× speedup)** |
| **Stage 5 Execution Duration** | 22.18 s | **3.65 s** | **−83.5% late-stage latency reduction** |
| **Peak GPU Generation Speed** | 150.6 tok/s (`qwen2.5-coder`) | **431.7 tok/s** (`llama3.2:1b`) | Zero GPU OOM faults |

To reproduce the physical silicon experiments locally:
```bash
python scripts/run_real_ollama_experiments.py
```
*(Raw experimental metrics are persisted in `docs/real_ollama_experiment_results.json`)*.

---

## 7. Critical Ablation Study (Section 13)

Empirical verification of ModelVM's four system-level mechanisms:

```bash
python -m modelvm.cli benchmark
```

| Configuration | Peak RAM | Memory Savings | Quality Score | Capability Density | Paging Overhead |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Static Router** (Monolithic) | 7.1 GB | 86.5% | 62% | 0.44 | 2.10s |
| **B. Dynamic (No CSP)** | 7.6 GB | 85.6% | 71% | 0.47 | 7.20s |
| **C. Dynamic + CSP (LRU)** | 7.6 GB | 85.6% | 93% | 0.61 | 7.20s |
| **D. Full ModelVM** | **7.6 GB** | **85.6%** | **98%** | **0.66** | **7.20s** |

### Key Findings
1. **85.6% Physical Memory Savings**: Enables 52.7 GB of specialized intelligence to run on an 8.0 GB consumer GPU/RAM.
2. **Cognitive State Packets Prevent Degradation**: Quality jumps from 71% to 98% across multi-hop reasoning.
3. **Predictive Working Set**: Eliminates cache thrashing and achieves peak Capability Density ($0.66$).

---

## 8. Formal Academic Manuscript (Journal Standard, 52 Pages)

The complete formal theoretical and empirical paper is compiled and formatted for submission to premier systems journals (ACM TOCS / IEEE TPDS):
* **Compiled PDF:** [`paper/modelvm_tocs_submission.pdf`](paper/modelvm_tocs_submission.pdf)
* **Page Count:** 52 pages (Two-column standard journal layout)
* **Figures:** 10 pure-vector standalone architectural and empirical visualizations (0 raster artifacts)
* **Sections:**
  1. Introduction & Systems Motivation (The Specialist Dilemma)
  2. Formal Problem Formulation & Invariants
  3. ModelVM Architecture & Runtime Abstraction
  4. Semantic State Virtualization (The Cognitive State Protocol)
  5. Predictive Model Residency & Working Set Engine ($W(t, k)$)
  6. Multi-Objective Cognitive Scheduling
  7. Implementation & Systems Mechanics
  8. Experimental Methodology & Non-Circularity Verification
  9. Results & Empirical Evaluation (Factorial Ablations, Pareto Frontiers, Stress Sweeps, Physical GPU Telemetry)
  10. Limitations & Operational Boundaries
  11. Related Work (MoE, vLLM/SGLang, Speculative Decoding)
  12. Conclusion & Future Directions

---

## 9. Quickstart & Usage

### Installation
Dependencies are lightweight and standard:
```bash
pip install -r requirements.txt
```

### 1. Run the Winning Demonstration
```bash
python -m modelvm.cli demo --budget 8.0
```
Runs a 5-stage cross-domain task (`Research → Math → Coding → Physics → Synthesis`) with real-time ASCII memory meters and paging telemetry.

### 2. Launch the Interactive Web Visualizer
```bash
python -m modelvm.cli serve --port 8000
```
Open **`http://localhost:8000`** in your browser to access the Cyber-OS web visualizer:
* Live memory envelope gauge and virtualization multiplier.
* Visual memory slots (RAM vs Disk) with manual Page-In / Page-Out buttons.
* Real-time WebSocket timeline and Cognitive State Packet inspector.
* Interactive Critical Ablation Study comparison cards.

### 3. Run Custom Tasks
```bash
python -m modelvm.cli run --task "Develop algorithmic trading strategy backtest, verify stochastic calculus proofs, implement vectorized Python engine, and stress-test market shocks."
```

### 4. Run Test Suite
```bash
python -m unittest discover -s tests
```

---

## 10. Directory Structure

```
d:\hacktoberfest/
├── modelvm/
│   ├── core/
│   │   ├── types.py            # Enums, PagingAction, AblationMode, PagingEvent
│   │   ├── manifest.py         # ModelManifest specification
│   │   └── state_packet.py     # CognitiveStatePacket (CSP)
│   ├── registry/
│   │   ├── catalog.py          # 10 specialist models (52.7 GB total)
│   │   └── manifests/          # Standalone YAML model manifests
│   ├── pager/
│   │   ├── memory_manager.py   # ModelPager with hard RAM budget enforcement
│   │   └── policy.py           # LRU and CostAwareEvictionPolicy
│   ├── scheduler/
│   │   └── cognitive_scheduler.py # Multi-objective score equation Score(m)
│   ├── router/
│   │   ├── task_decomposer.py  # Task decomposition into cognitive stages
│   │   ├── working_set.py      # Predictive working set W(t, k)
│   │   └── confidence.py       # Confidence control & escalation
│   ├── executor/
│   │   ├── backends.py         # Simulation & Ollama local connectors
│   │   └── kernel.py           # Central CognitiveKernel orchestrator
│   ├── benchmark/
│   │   ├── evaluator.py        # 4-dimensional evaluation framework
│   │   └── ablation.py         # Critical Ablation Study suite (A, B, C, D)
│   ├── api/
│   │   └── server.py           # FastAPI & WebSocket telemetry server
│   ├── web/
│   │   ├── index.html          # Cyber-OS dashboard
│   │   ├── style.css           # Glassmorphism & neon dark UI styling
│   │   └── app.js              # Real-time WebSocket visualizer logic
│   ├── cli.py                  # Rich terminal interactive application
│   └── main.py                 # Main entrypoint
├── scripts/
│   ├── run_real_ollama_experiments.py  # Real hardware physical silicon benchmark
│   └── generate_all_figures.py         # Pure-vector standalone publication figures
├── paper/
│   ├── modelvm_tocs_submission.pdf     # 51-page compiled journal paper
│   ├── build_check.tex                 # LaTeX master manuscript
│   └── sections/                       # All 12 modular paper sections
├── docs/                               # Raw telemetry and benchmark data
├── tests/                              # Full unit test suite
├── PDR.md                              # Foundational Project Definition Document
├── requirements.txt                    # Python dependencies
└── pyproject.toml                      # Build & packaging config
```

---

## 11. Winning Pitch

```text
ONE AI DOES NOT NEED ONE MONOLITHIC MODEL.

ModelVM maintains access to 10 specialized open-weight models,
but never keeps them all resident simultaneously.

It predicts what intelligence is needed,
pages it into memory,
executes the cognitive step,
preserves the task state in a Cognitive State Packet,
and pages in the next specialist.

52.7 GB of available intelligence.
8.0 GB active memory budget.
One continuous, high-precision cognitive workflow.
```
