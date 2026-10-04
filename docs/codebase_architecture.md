# ModelVM Codebase Architecture & Technical Specification

This document provides a comprehensive technical breakdown of the implemented **ModelVM** codebase (`modelvm/`). It describes the system components, class hierarchies, mathematical execution pipelines, memory invariants, and data flows.

---

## 1. System Component Map

```text
                                  COGNITIVE KERNEL
                         (modelvm/executor/kernel.py)
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
 TASK DECOMPOSER             COGNITIVE SCHEDULER              MODEL PAGER
(router/task_decomposer)    (scheduler/cognitive_scheduler) (pager/memory_manager)
        │                              │                              │
        │ CognitiveStagePlan           │ Multi-Objective Score        │ Enforces RAM Budget
        ▼                              ▼                              ▼
WORKING SET PREDICTOR        MODEL CATALOG REGISTRY          EVICTION POLICY
(router/working_set.py)     (registry/catalog.py)           (pager/policy.py)
        │                              │                              │
        │ W(t, k) Lookahead            │ 10 Models (52.7 GB)          │ Cost-Aware & LRU
        ▼                              ▼                              ▼
CONFIDENCE CONTROLLER        EXECUTION BACKENDS             TELEMETRY & UI
(router/confidence.py)      (executor/backends.py)          (api/server.py & web/)
        │                              │                              │
        │ Escalation Logic             │ Simulation & Ollama          │ WebSocket Streaming
        └──────────────────────────────┼──────────────────────────────┘
                                       ▼
                            COGNITIVE STATE PACKET
                          (core/state_packet.py)
```

---

## 2. Directory & Module Organization

```text
modelvm/
├── core/                           # Foundational Types & Data Models
│   ├── types.py                    # Enums (Capability, PagingAction, AblationMode) & Telemetry
│   ├── manifest.py                 # ModelManifest specification & quality scoring
│   └── state_packet.py             # CognitiveStatePacket (CSP) & state merging
├── registry/                       # Model Library Catalog
│   ├── catalog.py                  # ModelCatalog registry (10 models, 52.7 GB)
│   └── manifests/                  # Standalone YAML model manifests
├── pager/                          # Virtual Memory Subsystem
│   ├── memory_manager.py           # ModelPager (RAM budget enforcement, residency tracking)
│   └── policy.py                   # LRUEvictionPolicy & CostAwareEvictionPolicy
├── scheduler/                      # Cognitive Resource Scheduling
│   └── cognitive_scheduler.py      # Multi-objective Score(m) optimization function
├── router/                         # Cognitive Routing & Planning
│   ├── task_decomposer.py          # Task graph decomposition into cognitive stages
│   ├── working_set.py              # CognitiveWorkingSetPredictor (W(t, k))
│   └── confidence.py               # ConfidenceController & model escalation
├── executor/                       # Execution Orchestration
│   ├── backends.py                 # ModelBackend, SimulationBackend, OllamaBackend
│   └── kernel.py                   # CognitiveKernel runtime coordinator
├── benchmark/                      # Evaluation & Empirical Verification
│   ├── evaluator.py                # 4-dimensional evaluation framework
│   └── ablation.py                 # Critical Ablation Study suite (Modes A, B, C, D)
├── api/                            # REST & WebSocket Interface
│   └── server.py                   # FastAPI backend with real-time telemetry streaming
├── web/                            # Cyber-OS Web Visualizer
│   ├── index.html                  # Glassmorphic cyber dashboard
│   ├── style.css                   # Dynamic CSS theme & animations
│   └── app.js                      # WebSocket client & interactive visualizer logic
├── cli.py                          # Rich terminal application
└── main.py                         # CLI entrypoint
```

---

## 3. Core Subsystems & Implementation Details

### 3.1 Core Data Models (`modelvm/core/`)

#### 1. Enums and Telemetry (`modelvm/core/types.py`)
* `Capability`: Supported cognitive domains (`GENERAL`, `RESEARCH`, `SCIENCE`, `MATHEMATICS`, `CODING`, `PHYSICS`, `VISION`, `SECURITY`, `MEDICINE`, `FINANCE`, `WRITING`, `DATA_ANALYSIS`, `SYNTHESIS`).
* `PagingAction`: Memory manager events (`PAGE_IN`, `PAGE_OUT`, `EVICT`, `CACHE_HIT`, `PREFETCH`, `PIN`, `UNPIN`).
* `ModelStatus`: Residency state of model weights (`DISK`, `LOADING`, `RESIDENT`, `EXECUTING`, `EVICTING`).
* `AblationMode`: Architectural benchmark configurations (`A_STATIC_ROUTER`, `B_DYNAMIC_NO_CSP`, `C_DYNAMIC_WITH_CSP`, `D_FULL_MODELVM`).
* `PagingEvent`: Structured telemetry record capturing timestamp, model ID, action, RAM footprint, active memory, budget, latency duration, and operational reason.

#### 2. Model Manifest (`modelvm/core/manifest.py`)
Defines the schema for all registered models:
* `id: str`: Unique slug (e.g., `qwen-math-7b`).
* `name: str`: Human-readable identifier.
* `capabilities: List[Capability]`: Ranked cognitive specializations.
* `ram_required: float`: Memory footprint in gigabytes.
* `load_time: float`: Typical cold-load latency in seconds from storage.
* `latency: float`: Inference token latency in seconds per token.
* `quality: float`: Normalized domain benchmark score ($0.0 - 1.0$).
* `offline: bool`: Indicates fully offline execution.
* `parameters_billion`, `quantization`, `architecture`, `energy_cost_factor`.
* `capability_score(target: Capability) -> float`: Returns $1.0$ for primary specialization, $0.75$ for secondary, $0.50$ for general reasoners, and $0.05$ baseline.

#### 3. Cognitive State Packet (`modelvm/core/state_packet.py`)
Implements the model-neutral semantic state transfer interface:
* `CalculationItem`: Numerical or symbolic computation with formula, evaluated result, units, and verification flag.
* `EvidenceItem`: Structured claim, cited source, and calibrated confidence score ($p \in [0, 1]$).
* `StageTrace`: Audit trail of completed cognitive stages.
* `CognitiveStatePacket`:
  * Monotonic accumulation: `merge_update(update_csp)` merges facts, calculations, and evidence while deduplicating strings and updating decisions.
  * Prompt context generation: `to_prompt_context() -> str` serializes the structured state into markdown prompt context suitable for injection into any LLM.
  * Structured extraction: `extract_from_text(goal, text)` parses LLM outputs (JSON blocks or formatted markdown bullet points) into structured state fields.

---

### 3.2 Model Library Registry (`modelvm/registry/`)

#### `ModelCatalog` (`modelvm/registry/catalog.py`)
Maintains the catalog of 10 open-weight specialist models totaling **52.7 GB**:
1. `research-expert` (Mistral-Research-7B, 3.1 GB)
2. `mathematics-expert` (Qwen-Math-7B, 2.4 GB)
3. `coding-expert` (DeepSeek-Coder-6.7B, 3.0 GB)
4. `physics-expert` (Llama-Physics-8B, 3.2 GB)
5. `general-reasoner` (Llama-3.1-8B-Instruct, 7.1 GB)
6. `multimodal-vision` (Phi-3.5-Vision-4.2B, 5.6 GB)
7. `code-auditor` (StarCoder2-15B-Q4, 7.2 GB)
8. `biomedical-expert` (Bio-Mistral-7B, 6.8 GB)
9. `financial-analyst` (Fin-LLaMA-8B, 6.7 GB)
10. `synthesizer-master` (Command-R-14B, 7.6 GB)

* **Key Invariant:** No individual model exceeds 7.6 GB, ensuring that any individual specialist model fits within an **8.0 GB RAM envelope**.
* Supports dynamic loading and saving of YAML manifests via `load_from_directory()` and `save_to_directory()`.

---

### 3.3 Virtual Memory Manager & Pager (`modelvm/pager/`)

#### 1. Eviction Policies (`modelvm/pager/policy.py`)
* `EvictionPolicy`: Abstract base interface defining `select_eviction_candidates()`.
* `LRUEvictionPolicy`: Selects models with the oldest `last_accessed` timestamps.
* `CostAwareEvictionPolicy`: Evaluates an eviction priority score for each resident model:
  $$\text{Priority}(m) = 0.5 \cdot \text{Age}(m) + 1.5 \cdot \text{RAM}(m) - 2.0 \cdot \text{LoadTime}(m) - \text{FuturePenalty}(m)$$
  Where $\text{FuturePenalty} = 1000$ if $m \in W(t, k)$. Models needed in upcoming stages or expensive to reload are protected.

#### 2. Model Pager (`modelvm/pager/memory_manager.py`)
Enforces the hard memory envelope:
* `active_memory_gb`: Sum of RAM required by all currently resident models ($\le \text{budget}$).
* `free_memory_gb`: Remaining RAM before reaching the hard limit.
* `page_in(model_id, protected_ids, future_demanded_ids) -> PagingEvent`:
  * **Cache Hit:** If model is resident, registers zero load duration and returns immediately.
  * **Cache Miss:** Checks available free RAM. If $\text{free\_ram} < \text{model.ram}$, invokes `_evict_for()` to free the exact deficit.
* `page_out(model_id)`: Explicitly unloads weights from active memory back to storage.
* `prefetch(model_id)`: Loads upcoming weights into spare memory if free RAM permits without forcing eviction.
* `add_listener(callback)`: Observer pattern mechanism broadcasting paging telemetry to the web dashboard and CLI live feed.

---

### 3.4 Multi-Objective Cognitive Scheduler (`modelvm/scheduler/`)

#### `CognitiveScheduler` (`modelvm/scheduler/cognitive_scheduler.py`)
Computes the multi-objective score for all candidate models fitting within the memory budget:

$$\text{Score}(m) = F_{\text{capability}} - \alpha M_{\text{cost}} - \beta L_{\text{load}} - \gamma E_{\text{energy}} - \delta E_{\text{eviction}} + \eta F_{\text{future}}$$

Default Weights:
* $\alpha = 0.20$ (RAM footprint penalty)
* $\beta = 0.25$ (Cold-load latency penalty; $0.0$ on cache hit)
* $\gamma = 0.10$ (Energy/parameter factor)
* $\delta = 0.30$ (Eviction penalty on active models; scaled by $1.8\times$ if evicted models clash with future working set)
* $\eta = 0.35$ (Future stage demand bonus)

Outputs a `SchedulingScoreBreakdown` providing an explainable, transparent decomposition of each term.

---

### 3.5 Cognitive Routing & Planning (`modelvm/router/`)

#### 1. Task Decomposer (`modelvm/router/task_decomposer.py`)
* Deconstructs multi-domain prompts into ordered `CognitiveStagePlan` objects.
* Built-in support for standard pipelines:
  * Scientific Paper Reproduction: $\text{Research} \rightarrow \text{Math} \rightarrow \text{Coding} \rightarrow \text{Physics} \rightarrow \text{Synthesis}$
  * Quantitative Trading: $\text{Finance} \rightarrow \text{Math} \rightarrow \text{Coding} \rightarrow \text{Synthesis}$
  * Clinical Trial Pipeline: $\text{Medicine} \rightarrow \text{Math} \rightarrow \text{Coding} \rightarrow \text{Synthesis}$
* Robust regex-based semantic fallback for arbitrary user inputs.

#### 2. Working Set Predictor (`modelvm/router/working_set.py`)
* `predict_future_capabilities(stages, current_idx)`: Extracts upcoming capabilities within lookahead window $k$.
* `predict_future_model_ids(stages, current_idx)`: Resolves best-fit model IDs for future stages.
* `recommend_prefetch_model()`: Identifies candidate models for background prefetching when spare physical memory is available.

#### 3. Confidence Controller (`modelvm/router/confidence.py`)
* Evaluates stage outputs against a minimum confidence threshold (default $0.70$).
* Penalizes outputs with high uncertainty counts ($\mathcal{U}$) or missing calculations.
* Triggers model escalation to larger specialist or general models when necessary.

---

### 3.6 Execution Engine (`modelvm/executor/`)

#### 1. Backends (`modelvm/executor/backends.py`)
* `ModelBackend`: Abstract inference interface.
* `SimulationBackend`: Deterministic, high-fidelity cognitive simulation engine generating domain-accurate equations, Python simulation scripts (SciPy RK45), empirical evidence, and physical parameters matching model latency profiles.
* `OllamaBackend`: Connects to local Ollama daemon (`http://localhost:11434/api/generate`) with automatic fallback to `SimulationBackend` if offline.

#### 2. Cognitive Kernel (`modelvm/executor/kernel.py`)
The central coordinator:
1. Decomposes user goal into ordered stages.
2. For each stage:
   * Predicts working set $W(t, k)$.
   * Scores candidate models via `CognitiveScheduler`.
   * Pages in selected model via `ModelPager` (evicting if necessary).
   * Executes stage using `ModelBackend`, passing the current CSP.
   * Merges output into CSP.
   * Evaluates confidence and handles escalation if needed.
   * Prefetches next model if spare memory permits.
3. Computes summary metrics (`TaskExecutionSummary`).

---

### 3.7 Benchmark & Critical Ablation Suite (`modelvm/benchmark/`)

#### 1. Evaluator (`modelvm/benchmark/evaluator.py`)
Computes the four evaluation dimensions from PDR Section 12:
1. **Memory Savings Ratio:** $1 - \frac{\text{PeakMemory}_{\text{ModelVM}}}{\text{PeakMemory}_{\text{AllResident}}}$
2. **Capability Coverage Score:** Quality score based on preserved facts, calculations, and domain accuracy.
3. **Capability Density:** $\frac{\text{Quality} \times \text{Total Stages}}{\text{Peak Resident Memory}}$
4. **Latency Breakdown:** Paging overhead vs. execution time.

#### 2. Ablation Study Runner (`modelvm/benchmark/ablation.py`)
Automates comparative benchmarking across all four configurations:
* **Mode A (Static Router):** Single monolithic general model.
* **Mode B (Dynamic Loading without CSP):** Paging models with lossy string state transfer.
* **Mode C (Dynamic Loading with CSP):** Paging with structured state, LRU policy.
* **Mode D (Full ModelVM):** Paging + CSP + Predictive Working Set + Resource-Aware Scheduling.

---

### 3.8 User Interfaces & API

#### 1. FastAPI Telemetry Server (`modelvm/api/server.py`)
* `GET /api/status`: Active memory, resident models, disk models, cache hit rate.
* `GET /api/models`: Catalog manifests.
* `POST /api/run`: Executes task and streams updates.
* `POST /api/budget`: Dynamically adjusts the active RAM budget.
* `POST /api/page_in` & `POST /api/page_out`: Manual paging testing.
* `POST /api/ablation`: Runs 4-mode benchmark.
* `WebSocket /ws`: Real-time streaming of `PAGING_EVENT`, `STAGE_COMPLETED`, and `TASK_FINISHED`.

#### 2. Cyber-OS Web Visualizer (`modelvm/web/`)
* **Live Memory Envelope:** Gauge showing current active RAM vs. 52.7 GB library with $6.6\times$ virtualization multiplier.
* **Memory Residency Slots:** Visual representation of models in RAM vs. Storage with interactive Page-In / Page-Out controls.
* **Live Paging Timeline:** Displays real-time `[PAGE_IN]`, `[CACHE_HIT]`, `[EVICT]`, and `[PREFETCH]` events.
* **Cognitive State Packet Inspector:** Tabbed viewer for Facts, Calculations, Evidence, Decisions, and Artifacts.
* **Ablation Comparison Grid:** Side-by-side benchmark comparison cards.

#### 3. Rich CLI Terminal Application (`modelvm/cli.py`)
* `python -m modelvm.cli demo --budget 8.0`: Runs the winning PDR demonstration with ASCII memory allocation bars.
* `python -m modelvm.cli benchmark`: Executes the 4-mode Critical Ablation Study.
* `python -m modelvm.cli library`: Displays formatted model catalog table.
* `python -m modelvm.cli serve --port 8000`: Launches the web dashboard.
