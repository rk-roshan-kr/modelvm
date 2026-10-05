# ModelVM: Research Paper Structure & Submission Blueprint

**Working Title:** ModelVM: Virtualizing Semantic State and Model Residency for Resource-Constrained Language Model Systems  
**Alternative Systems Title:** ModelVM: A Resource-Aware Runtime for Heterogeneous Open-Weight Language Models  
**Conceptual Tagline:** *Virtual Memory for Intelligence*  
**Conference Target:** MLSys 2026 / USENIX OSDI 2026 / EuroSys 2026 (12 pages double-column)  
**Journal Extension Trajectory:** ACM TOCS / IEEE TPAMI / JMLR (25–35 pages comprehensive)

---

## 1. The Intellectual Center of the Paper

The intellectual center of ModelVM is **not** the operating system metaphor. The OS analogy serves as an intuitive motivation, but the scientific core consists of two concrete, measurable systems principles:

> **1. Semantic state can be decoupled from model identity through a typed, model-independent representation.**  
> **2. Model residency can be dynamically managed as a pageable computational resource under hard physical hardware limits.**

Together, these principles naturally yield an **operating-system-inspired runtime abstraction**:

> **ModelVM is a resource-aware runtime that virtualizes semantic state and model residency while coordinating heterogeneous model execution under constrained hardware resources.**

---

## 2. Defeating the Central Reviewer Attack

### The Central Attack
> *"This is just model routing + model loading + a structured prompt."*

### Why the Architecture Alone Does Not Defeat It
Having three components (CSP, Pager, Scheduler) in an architectural diagram does not automatically prove they are non-trivial. A skeptical reviewer will claim:
* *CSP is just prompt engineering.*
* *The Pager is just calling `ollama run` or Python `del model`.*
* *The Scheduler is just an argmax score.*

### The Experimental Counter-Offensive
The paper defeats this attack through three dedicated, non-circular experimental questions that isolate each mechanism and demonstrate advantages impossible with routing or prompt engineering alone:

```text
                               THE THREE CORE EXPERIMENTS
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
   Experiment 1:                     Experiment 2:                     Experiment 3:
Does CSP Matter?                 Does Predictive Residency         The Quality–Resource
(Semantic State Virtualization)  Beat Ordinary Routing?            Pareto Frontier
Raw Text vs. Typed CSP           Monolith vs. Route vs.            Quality vs. Memory vs.
under identical token limits.    LRU vs. Predictive W(t,k).        Latency across all regimes.
```

---

## 3. Paper Section Outline & Page Budget (12-Page Conference Format)

```text
Section                                         Target Pages
─────────────────────────────────────────────────────────────
Abstract                                        ~0.3 page
1. Introduction                                 ~2.0 pages
2. Runtime Architecture & Systems Abstraction   ~1.5 pages
3. Semantic State Virtualization (CSP)          ~2.0 pages
4. Predictive Model Residency & Working Set     ~1.5 pages
5. Resource-Aware Cognitive Scheduling          ~1.2 pages
6. Experimental Evaluation                      ~2.5 pages
   6.1 Exp 1: State Virtualization (CSP vs Raw)
   6.2 Exp 2: Predictive Residency vs Routing/LRU
   6.3 Exp 3: Quality-Resource Pareto Frontiers
   6.4 The Signature 5-System Progression
7. Addressing Critical Reviewer Attacks         ~1.0 page
8. Related Work                                 ~1.0 page
9. Limitations & Discussion                     ~0.5 page
10. Conclusion                                  ~0.3 page
References & Appendix                           ~2.0 pages
─────────────────────────────────────────────────────────────
Total Body:                                     ~12.0 pages
```

---

## 4. Detailed Section-by-Section Blueprint

### Abstract
* **Motivation:** Specialized open-weight models consistently outperform general models in formal domains (math, code, physics), but keeping a library of specialists resident in memory requires 50+ GB RAM/VRAM, far exceeding consumer hardware (8–16 GB).
* **The Core Proposal:** ModelVM decouples semantic state from model identity and treats model weights as pageable resources governed by working-set lookahead.
* **The Three Systems Abstractions:**
  1. *Semantic State Virtualization (CSP):* Typed schema preserving verified facts, calculations, evidence, and artifacts across incompatible architectures without hidden-state projection bridges.
  2. *Predictive Model Residency ($W(t, k)$):* Lookahead forecasting, eviction shielding, and background prefetching under hard physical budgets.
  3. *Resource-Aware Cognitive Scheduling:* Multi-objective optimization balancing capability, memory footprint, cold-load latency, energy, and future stage reuse.
* **Evaluation Summary:** Evaluated across a 52.7 GB catalog under an 8.0 GB RAM envelope. Controlled factorial experiments demonstrate that CSP produces the primary main effect on task state preservation, while predictive working-set scheduling and multi-objective selection reduce memory thrashing and cold-load stalls.

---

### Section 1: Introduction (~2.0 pages)
* **1.1 The Domain Specialization Frontier:**
  - Empirical divergence of specialized weights (*Qwen-Math*, *DeepSeek-Coder*, *Llama-Physics*, *Mistral-Research*) vs general monoliths.
  - The Physical Memory Barrier: $\sum_{i=1}^N \text{RAM}(M_i) \gg \text{RAM}_{\text{budget}}$.
* **1.2 Tripartite Separation of Concerns:**
  - Conventional architectures conflate state, residency, and scheduling.
  - Separating Semantic State Virtualization (CSP) vs Model Residency (Pager) vs Execution Scheduling (Scheduler).
* **1.3 The Central Research Question:**
  - *Can heterogeneous open-weight language models be treated as pageable computational resources while preserving task state and improving quality–resource tradeoffs under constrained hardware?*
* **1.4 Summary of Contributions:**
  - Formulate CSP 9-tuple and diversity-discounted aggregation.
  - Formulate predictive working set $W(t, k)$ and time-consistent prefetch utility.
  - Formulate multi-objective hardware-aware scheduling.
  - Controlled factorial and Pareto empirical validation.

---

### Section 2: Runtime Architecture & Systems Abstraction (~1.5 pages)
* **2.1 Motivation via the OS Analogy:**
  - Process $\leftrightarrow$ Domain Capability
  - Physical RAM $\leftrightarrow$ Active Hardware Memory Budget (8.0 GB)
  - Secondary Storage $\leftrightarrow$ Model Catalog (52.7 GB)
  - Page-In / Page-Out $\leftrightarrow$ Model Weight Load / Eviction
  - Page Cache Hit $\leftrightarrow$ Resident Model Hit (zero load latency)
  - Working Set $W(t, \Delta)$ $\leftrightarrow$ Predictive Cognitive Working Set $W(t, k)$
  - Process Control Block $\leftrightarrow$ Cognitive State Packet (CSP)
* **2.2 Runtime Control Loop:**
  - Cognitive Kernel (Decomposition) $\rightarrow$ Scheduler (Score) $\rightarrow$ Pager (Residency) $\rightarrow$ Backend Execution $\rightarrow$ State Packet Update.
* **2.3 Physical Memory Invariant:**
  - Hard constraint: $\text{ActiveRAM}(M_{\text{resident}}) \le \mathcal{B}_{\text{RAM}}$ strictly enforced at all times.

---

### Section 3: Semantic State Virtualization (CSP) (~2.0 pages)
* **3.1 The Incompatibility Problem:**
  - Tokenizer incompatibility ($\mathcal{V}_A \neq \mathcal{V}_B$), parameter space incompatibility ($\mathbf{h} \in \mathbb{R}^d$).
  - Why raw conversational text concatenation fails (token budget exhaustion, precision decay, numerical hallucination).
* **3.2 Mathematical Formulation:**
  - The 9-tuple schema: $\mathcal{S}_t = \langle \mathcal{G}, \mathcal{F}_t, \mathcal{C}_t, \mathcal{E}_t, \mathcal{A}_t, \mathcal{U}_t, \mathcal{D}_t, \mathcal{Q}_t, \mathcal{O}_t \rangle$.
  - Explicit typing: facts, calculations, evidence, assumptions, uncertainties, decisions, questions, artifacts.
* **3.3 Epistemic Diversity-Discounted Evidence Aggregation:**
  - Declared heuristic formula with source correlation discount ($w_{\text{source}} = 0.65$):
    $$\text{MergeEvidence}(e_1, e_2) = \begin{cases} \max(p_1, p_2) & \text{if } s_1 = s_2 \\ 1.0 - (1.0 - p_1)(1.0 - p_2) \cdot w_{\text{source}} & \text{if } s_1 \neq s_2 \end{cases}$$
* **3.4 Monotonic State Invariance:**
  - Fact preservation $\mathcal{F}_t \subseteq \mathcal{F}_{t+1}$; progressive resolution of open questions $\mathcal{Q}$.
* **3.5 Non-Circular Verification:**
  - Independent AST verification (`ArithmeticVerifier`) ensuring calculation truth flags are never self-assigned.

---

### Section 4: Predictive Model Residency & Working Set Management (~1.5 pages)
* **4.1 Models as Pageable Computational Resources:**
  - Managing discrete weights on disk/NVMe and active VRAM/RAM.
* **4.2 Predictive Cognitive Working Set:**
  - $W(t, k) = \{ \arg\max_{m} \text{CapabilityMatch}(m, C_{t+j}) \mid j \in [1, k] \}$.
* **4.3 Eviction Shielding:**
  - Models $m \in W(t, k)$ receive an eviction cost multiplier ($\delta \times 1.8$), preventing thrashing.
* **4.4 Dimensionally Consistent Prefetch Utility:**
  - $U_{\text{prefetch}} = P(m) \cdot \Delta L_{\text{avoided}} - \lambda M_{\text{cost}} - \mu E_{\text{prefetch}}$ (in seconds of latency saved).

---

### Section 5: Resource-Aware Multi-Objective Cognitive Scheduling (~1.2 pages)
* **5.1 Multi-Objective Scoring Function:**
  - Joint trade-off: $\text{Score}(m) = F_{\text{cap}} - \alpha M_{\text{cost}} - \beta L_{\text{load}} - \gamma E_{\text{energy}} - \delta E_{\text{evict}} + \eta F_{\text{future}}$.
* **5.2 Term Normalization & Parameters:**
  - Explicit definition and sensitivity analysis of weights $\alpha, \beta, \gamma, \delta, \eta$.
* **5.3 Empirical Capability Profiling (`ModelProfiler`):**
  - Replacing manual catalog scores with empirical probe matrices across 7 domains (Math, Coding, Physics, Research, Finance, Medicine, General).

---

### Section 6: Controlled Experimental Evaluation (~2.5 pages)

#### 6.1 Experiment 1: Does CSP Actually Matter? (Semantic State Virtualization)
* **Hypothesis:** Under identical models, task, and token budget, model transitions mediated by CSP will maintain factual consistency and arithmetic precision, whereas raw conversational text handoffs will experience progressive error compounding.
* **Setup:** Compare `Model A -> raw text -> Model B` against `Model A -> CSP -> Model B`.
* **Metrics:** Factual retention ratio ($R_{\text{facts}}$), verified calculation survival ($R_{\text{calcs}}$), prompt token overhead, and error propagation rate.

#### 6.2 Experiment 2: Does Predictive Residency Beat Ordinary Routing & Naive Paging?
* **Hypothesis:** Stage-level working set forecasting $W(t, k)$ and cost-aware eviction reduce memory thrashing and cold-load stalls compared to reactive LRU or naive routing.
* **Baselines:**
  1. *Baseline A (Monolith):* Single static general model.
  2. *Baseline B (Stateless Routing):* Dynamic model selection assuming infinite RAM (unconstrained).
  3. *Baseline C (Plain LRU Paging):* Dynamic model loading with classical recency eviction (no lookahead).
  4. *Baseline D (Greedy Selection):* Capability-based model loading without hardware cost awareness.
  5. *ModelVM:* Predictive working set + multi-objective scheduler + dynamic pager.
* **Metrics:** Peak RAM/VRAM, cold-load latency, total execution time, number of evictions, number of reloads, cache hit rate.

#### 6.3 Experiment 3: The Multi-Dimensional Pareto Frontier
* **Visual Plots:**
  - **Quality vs. Memory:** Showing ModelVM operating in the high-quality, low-memory regime inaccessible to monoliths or static ensembles.
  - **Quality vs. Latency:** Showing prefetching closing the latency gap with resident models.
  - **Quality vs. Energy:** Normalized energy consumption per verified deliverable.

#### 6.4 The Signature 5-System Progression Table
The paper's centerpiece empirical table (same task, same models, same hardware):

| System Configuration | Quality ($Q$) | State Retention ($R$) | Peak VRAM / RAM | Cold-Load Latency | Evictions / Reloads | Cache Hit Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **A: Monolithic Generalist** | Low–Mod | Low | 7.1 GB | Minimal | 0 | 0% |
| **B: Specialist Routing + Raw Text** | Low | Low (Decayed) | 7.6 GB | High | High (Thrashing) | 0% |
| **C: Specialist Routing + CSP** | **High** | **High (100%)** | 7.6 GB | High | High (Thrashing) | 0% |
| **D: Specialist Routing + CSP + Plain LRU**| **High** | **High (100%)** | 7.6 GB | Moderate | Moderate | ~8% |
| **E: Full ModelVM (CSP + W(t,k) + Scheduler)**| **High** | **High (100%)** | **7.6 GB** | **Optimized** | **Minimal** | **16.7%+** |

---

### Section 7: Addressing Critical Reviewer Attacks (~1.0 page)
* **7.1 Attack 1: "Isn't this just model routing?"**
  - Refutation: Routing is stateless prompt dispatching. ModelVM manages hardware memory residency, state virtualization across disparate tokenizers, and predictive lookahead.
* **7.2 Attack 2: "Why not just use one good monolithic model?"**
  - Refutation: 8B monoliths fail specialist accuracy (0/4 verified calcs); 70B+ monoliths cause immediate OOM on consumer hardware. ModelVM achieves specialist accuracy within an 8.0 GB envelope.
* **7.3 Attack 3: "Are model catalog scores artificially chosen?"**
  - Refutation: Decoupled non-circular verification (`ArithmeticVerifier`) + held-out empirical capability profiling matrix (`ModelProfiler`).

---

### Section 8: Related Work (~1.0 page)
* **LLM Routing Frameworks:** RouteLLM, FrugalGPT, FLARE, HyDRA.
* **Parameter Offloading & Layer Paging:** FlexGen, LLM in a flash, PowerInfer.
* **Agent Operating Systems:** MemGPT, AIOS.
* **Adapter Serving:** S-LoRA, Punica.

---

### Section 9: Limitations & Practical Considerations (~0.5 page)
* Hardware bus bandwidth (PCIe 4.0 vs SATA) and cold-load impact.
* Asynchronous token streaming and overlapping computation with background weight transfers.

---

### Section 10: Conclusion (~0.3 page)
* Summary: Semantic state virtualization and predictive model residency together resolve the fundamental tension between model specialization and physical hardware limits.

---

## 5. Journal Extension Trajectory (25–35 Pages Roadmap)

For a top-tier journal extension (ACM TOCS / IEEE TPAMI / JMLR), the conference paper expands with:
1. **Workload Diversity:** 5 distinct cross-domain benchmarks (Scientific reproduction, Clinical medical diagnosis, Financial portfolio risk modeling, Full-stack software synthesis, Aerospace mechanics).
2. **Hardware Platform Diversity:** 3 distinct physical testbeds:
   - High-end consumer workstation (RTX 4090 24GB + PCIe 4.0 NVMe).
   - Constrained consumer laptop (RTX 4060 8GB + SATA/PCIe 3.0 SSD).
   - Edge embedded device (Apple Silicon M-series unified memory / Jetson AGX).
3. **Model Diversity:** Expanding from 10 models (52.7 GB) to 20 models (100+ GB library).
4. **Formal Scheduling Proofs:** Theoretical competitive ratio analysis of $W(t, k)$ prefetching under varying lookahead horizons $k$.
5. **Real-world Telemetry:** Profiling memory page fault intervals, PCIe bus bandwidth utilization, and kernel interrupt overheads.
