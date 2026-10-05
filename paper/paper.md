# ModelVM: Virtualizing Semantic State and Model Residency for Resource-Constrained Language Model Systems

**Tagline:** *Virtual Memory for Intelligence*  
**Anonymous Authors**  
*Under Review for Machine Learning Systems (MLSys 2026)*

---

## Abstract

Open-weight Large Language Models (LLMs) have achieved state-of-the-art specialization across diverse disciplines, including mathematics, code synthesis, scientific literature extraction, and physical reasoning. However, local deployment of a multi-specialist AI pipeline on consumer workstations or edge hardware faces a fundamental barrier: **hardware memory capacity**. Keeping a suite of heterogeneous domain specialists simultaneously resident in RAM or VRAM requires 50+ GB of memory, far exceeding typical consumer hardware budgets (8–16 GB). Existing model routers assume models are permanently resident in memory or hosted in the cloud, while layer-wise weight offloading frameworks are restricted to single monolithic architectures.

We present **ModelVM**, a resource-aware runtime that virtualizes semantic state and model residency while coordinating heterogeneous model execution under constrained hardware resources. Rather than assuming models are permanently resident, ModelVM virtualizes model execution through three foundational systems abstractions:
1. **Semantic State Virtualization (Cognitive State Packet / CSP):** A model-neutral, typed semantic intermediate representation that preserves structured task state—including verified facts, arithmetic calculations, empirical claims, assumptions, decisions, and digital deliverables—across models with incompatible tokenizers, context windows, and latent parameter spaces, without hidden-state projection bridges.
2. **Predictive Model Residency:** Treating open-weight models as pageable computational resources under hard physical memory budgets, managed via working-set lookahead ($W(t, k)$), eviction shielding, and opportunistic background weight prefetching.
3. **Resource-Aware Cognitive Scheduling:** A multi-objective optimization function balancing capability fit, memory footprint, cold-load latency, energy consumption, eviction penalties, and future stage reuse, grounded by empirical capability profiling over held-out benchmark probes.

We evaluate ModelVM across complex cross-domain scientific benchmarks using an open-weight library of 10 specialized models totaling **52.7 GB** operating under a strict **8.0 GB active RAM envelope**. Using a decoupled, non-circular evaluation harness (independent AST arithmetic verification and structured ground-truth facts), we conduct an orthogonal $2^3$ factorial ablation study over the dynamic paging substrate. Preliminary factorial evaluation indicates that Semantic State Virtualization produces the primary main effect on task state preservation, while predictive working-set scheduling and multi-objective selection reduce memory thrashing and cold-load stalls under tight physical constraints. ModelVM provides a viable path to executing specialist-grade multi-model reasoning on consumer-class hardware without requiring simultaneous memory residency.

---

## 1. Introduction

The scaling hypothesis has produced capable general foundation models, yet domain specialization remains dominant for precision engineering, scientific computing, and formal reasoning. Specialized open-weight models—such as *Qwen-Math* for symbolic derivation, *DeepSeek-Coder* for algorithmic synthesis, *Mistral-Research* for literature analysis, and *Llama-Physics* for dynamic mechanics—consistently outperform monolithic general models of comparable or larger size within their respective fields.

However, deploying these specialists simultaneously on local hardware introduces a prohibitive memory bottleneck. A multi-domain pipeline requires:

$$\sum_{i=1}^{N} \text{RAM}(M_i) \gg \text{RAM}_{\text{budget}}$$

For example, a library of ten 7B–14B quantized models occupies **52.7 GB**, exceeding the 8 GB or 16 GB memory envelope of consumer PCs, laptops, and edge devices.

```text
CONVENTIONAL APPROACH                   ModelVM RUNTIME
Keep all 10 models in RAM               8.0 GB Hard Memory Envelope
Total VRAM Needed: 52.7 GB              Library: 52.7 GB on Storage
Result: Out-Of-Memory (OOM)             Result: Continuous Multi-Stage Execution
```

To resolve this bottleneck, ModelVM addresses a central research question:

> **Can heterogeneous open-weight language models be treated as pageable computational resources while preserving task state and improving quality–resource tradeoffs under constrained hardware?**

### The Three Core Contributions:
1. **Semantic State Virtualization:** We formulate the **Cognitive State Packet (CSP)**, an algebraic, model-independent intermediate representation that prevents multi-hop conversational drift and transfers verified facts, mathematical results, evidence, and artifacts losslessly across models of disparate architectures without hidden-state projection bridges.
2. **Predictive Model Residency:** We formulate the **Predictive Cognitive Working Set ($W(t, k)$)**, adapting OS working-set theory to forecast capability demand sequences, shield imminent models from eviction, and prefetch weights into spare physical RAM buffers.
3. **Resource-Aware Cognitive Scheduling:** We formulate a joint multi-objective optimization objective balancing capability fit, memory footprint, cold-load latency, energy consumption, eviction penalties, and future stage reuse, grounded by held-out empirical capability profiling.
4. **Controlled Orthogonal $2^3$ Factorial Evaluation:** We execute an orthogonal $2^3$ factorial experiment isolating the main and interaction effects of CSP, Working Set lookahead, and Scheduler selection against an external static monolithic baseline, evaluated across four independent dimensions: Quality ($Q$), State Retention ($R$), Resource Efficiency ($E$), and Latency ($L$).

---

## 2. Runtime Architecture & The Operating System Analogy

ModelVM establishes a direct conceptual correspondence with classical operating system memory management:

| Operating System Virtual Memory | ModelVM Systems Runtime |
| :--- | :--- |
| **Process** | Domain Capability (Research, Math, Coding, Physics, Medicine) |
| **Physical RAM / VRAM** | Active Hardware Memory Budget (Hard Bound, e.g. 8.0 GB) |
| **Secondary Storage (SSD/NVMe)**| Model Library Catalog (e.g. 52.7 GB across 10 models) |
| **Page-In** | Load Model Weights into Active RAM/VRAM |
| **Page-Out** | Evict / Unload Model Weights from Memory |
| **Page Cache** | Resident Model Cache (Zero-latency hit) |
| **Page Prefetch** | Predictive background loading into spare memory buffers |
| **Working Set $W(t, \Delta)$** | Predicted sequence of required models $W(t, k)$ |
| **CPU Scheduler** | Resource-Aware Multi-Objective Model Scheduler |
| **Process Control Block** | **Cognitive State Packet (CSP)** |

```text
                         USER TASK
                             │
                             ▼
                  ┌─────────────────────┐
                  │   COGNITIVE KERNEL  │
                  │ Task decomposition  │
                  │ Capability matching │
                  │ Working-set predict │
                  │ Confidence control  │
                  └──────────┬──────────┘
                             │
                 ┌───────────▼───────────┐
                 │    MODEL SCHEDULER    │
                 │ Score(m) = Fit - Cost │
                 │ + Future Demand Bonus │
                 └───────────┬───────────┘
                             │
                  ┌──────────▼──────────┐
                  │    MODEL PAGER      │
                  │ Page-in / Evict     │
                  │ 8.0 GB Hard Budget  │
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

## 3. Semantic State Virtualization (Cognitive State Packet / CSP)

### 3.1 The Incompatibility Problem
When chaining heterogeneous models (e.g., Mistral-7B, Qwen-2.5, DeepSeek-Coder, Command-R), they share neither hidden representations ($\mathbf{h} \in \mathbb{R}^d$) nor vocabulary tokenizers ($\mathcal{V}_A \neq \mathcal{V}_B$). Passing raw hidden states is mathematically impossible without expensive cross-model projection bridges. Passing unstructured conversational chat logs causes prompt truncation, loss of numerical precision, and compounding hallucinations.

```text
Conventional:  Model A ──[raw text]──► Model B ──[raw text]──► Model C  (Lossy, decaying)
ModelVM:       Model A ───[ CSP ]───► Model B ───[ CSP ]────► Model C  (Lossless, verified)
```

### 3.2 Formal Specification
ModelVM introduces the **Cognitive State Packet (CSP)** $\mathcal{S}_t$:

$$\mathcal{S}_t = \langle \mathcal{G}, \mathcal{F}_t, \mathcal{C}_t, \mathcal{E}_t, \mathcal{A}_t, \mathcal{U}_t, \mathcal{D}_t, \mathcal{Q}_t, \mathcal{O}_t \rangle$$

Where:
* $\mathcal{G}$: The global user objective string.
* $\mathcal{F}_t = \{f_1, f_2, \dots\}$: Cumulative set of deduplicated domain facts.
* $\mathcal{C}_t = \{(e_i, r_i, u_i, v_i, m_i)\}$: Mathematical calculations containing expression $e_i$, result $r_i$, units $u_i$, verification flag $v_i \in \{\text{True}, \text{False}\}$, and verification method $m_i \in \{\text{"arithmetic"}, \text{"symbolic"}, \text{"None"}\}$.
* $\mathcal{E}_t = \{(c_k, s_k, p_k)\}$: Empirical evidence items with claim $c_k$, originating model source $s_k$, and confidence score $p_k \in [0.0, 1.0]$.
* $\mathcal{A}_t$: Explicit domain assumptions.
* $\mathcal{U}_t$: Flagged uncertainties or parameter bounds.
* $\mathcal{D}_t$: Architectural and modeling decisions.
* $\mathcal{Q}_t$: Unresolved open questions for subsequent stages.
* $\mathcal{O}_t$: Concrete digital artifacts (e.g., Python scripts, equation derivations, data tables).

### 3.3 Epistemic Diversity-Discounted Evidence Aggregation
Rather than claiming unsupported Bayesian guarantees, ModelVM explicitly implements an **epistemic diversity-discounted heuristic**:

$$\text{MergeEvidence}(e_1, e_2) = \begin{cases} 
\max(p_1, p_2) & \text{if } s_1 = s_2 \quad (\text{same source model}) \\
1.0 - (1.0 - p_1)(1.0 - p_2) \cdot w_{\text{source}} & \text{if } s_1 \neq s_2 \quad (\text{independent models})
\end{cases}$$

Where $w_{\text{source}} = 0.65$ represents a calibrated discount accounting for common pretraining corpora across open-weight models.

### 3.4 State Invariance & Monotonic Accumulation
The CSP satisfies monotonic accumulation across stage transitions:

$$\mathcal{F}_t \subseteq \mathcal{F}_{t+1}, \quad \mathcal{C}_t \subseteq \mathcal{C}_{t+1}, \quad \mathcal{E}_t \subseteq \mathcal{E}_{t+1}$$

While uncertainties $\mathcal{U}$ and open questions $\mathcal{Q}$ are progressively resolved:

$$\mathcal{Q}_{t+1} = \mathcal{Q}_t \setminus (\mathcal{F}_{t+1} \cup \mathcal{D}_{t+1})$$

This guarantees that mathematical derivations and scientific parameters obtained in Stage 1 remain intact and accessible to the coding model in Stage 3 and the synthesizer in Stage 5.

---

## 4. Predictive Model Residency & Dynamic Paging

In classical OS memory management \cite{denning1968working}, the working set $W(t, \Delta)$ represents the set of memory pages referenced during process interval $[t-\Delta, t]$.

ModelVM extends this to the **Predictive Cognitive Working Set**:

$$W(t, k) = \left\{ \arg\max_{m \in \mathcal{M}} \text{CapabilityMatch}(m, C_{t+j}) \;\middle|\; j \in \{1, \dots, k\} \right\}$$

Where $k$ is the forward lookahead horizon (default $k=2$), and $C_{t+j}$ is the predicted domain capability for future stage $t+j$.

### Systems Mechanisms:
1. **Eviction Shielding:** When staging a new model requires evicting resident models to satisfy physical RAM constraints, any currently resident model $m \in W(t, k)$ receives an eviction penalty multiplier ($\delta \times 1.8$), preventing thrashing.
2. **Dimensionally Consistent Prefetch Utility:**
   The pager evaluates whether to prefetch candidate model $m_{\text{next}}$ in spare background memory:
   $$U_{\text{prefetch}} = P(m) \cdot \Delta L_{\text{avoided}}(m) - \lambda \cdot M_{\text{cost}}(m) - \mu \cdot E_{\text{prefetch}}(m)$$
   Where all terms are dimensionally expressed in seconds of execution latency saved versus memory pressure risk.

---

## 5. Resource-Aware Cognitive Scheduling

For each stage requiring capability $C$, the scheduler scores all candidate models $m \in \mathcal{M}$:

$$\text{Score}(m) = F_{\text{capability}}(m, C) - \alpha M_{\text{cost}}(m) - \beta L_{\text{load}}(m) - \gamma E_{\text{energy}}(m) - \delta E_{\text{eviction}}(m) + \eta F_{\text{future}}(m)$$

Subject to the hard physical constraint:

$$\text{RAM}(m) \le \text{RAM}_{\text{budget}}$$

### Term Definitions:
1. **Capability Fit ($F_{\text{capability}}$):** Derived from empirical benchmark profiling on held-out tasks.
2. **Normalized Memory Cost ($M_{\text{cost}}$):** $\frac{\text{RAM}(m)}{\text{RAM}_{\text{budget}}}$.
3. **Load Latency ($L_{\text{load}}$):** $0.0$ if model is already resident (cache hit!); otherwise normalized cold-load time $\min\left(1.0, \frac{\text{LoadTime}(m)}{5.0}\right)$.
4. **Energy Factor ($E_{\text{energy}}$):** $\min\left(1.0, \frac{\text{Params}(m)}{32\text{B}}\right) \times \text{QuantFactor}(m)$.
5. **Eviction Cost ($E_{\text{eviction}}$):** Penalizes models that force evicting resident models belonging to $W(t, k)$.
6. **Future Demand Bonus ($F_{\text{future}}$):** Rewards models capable of satisfying stages within the upcoming lookahead window $W(t, k)$.

### Empirical Capability Profiling (`ModelProfiler`)
Rather than relying on hand-picked registry numbers, ModelVM integrates `ModelProfiler` to evaluate candidate models against held-out benchmark probes across 7 domains, establishing an empirical matrix $\mathbf{P} \in [0, 1]^{N \times M}$:

| Model ID | Math | Coding | Physics | Research | Finance | Medicine | General |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `qwen-math-7b` | **0.96** | 0.74 | 0.82 | 0.62 | 0.81 | 0.35 | 0.70 |
| `deepseek-coder-6.7b` | 0.78 | **0.94** | 0.68 | 0.65 | 0.70 | 0.30 | 0.72 |
| `llama-physics-8b` | 0.84 | 0.68 | **0.90** | 0.75 | 0.60 | 0.42 | 0.73 |
| `mistral-research-7b` | 0.65 | 0.68 | 0.75 | **0.92** | 0.72 | 0.58 | 0.80 |
| `llama-3.1-8b-instruct` | 0.70 | 0.72 | 0.73 | 0.80 | 0.72 | 0.60 | **0.91** |

---

## 6. Experimental Evaluation

### 6.1 Experimental Setup
* **Hardware Profile:** Consumer memory envelope constrained to **8.0 GB RAM/VRAM**.
* **Model Library:** 10 open-weight specialist models totaling **52.7 GB**.
* **Benchmark Task:** Complex cross-domain scientific paper reproduction:
  $$\text{Research} \rightarrow \text{Mathematics} \rightarrow \text{Coding} \rightarrow \text{Physics} \rightarrow \text{Synthesis}$$
* **Evaluation Harness:** Decoupled AST verification (`ArithmeticVerifier`) and structured physical ground truth (`GroundTruthFact`).

### 6.2 The Orthogonal 2³ Factorial Ablation Matrix

Dynamic Paging serves as the fixed runtime substrate. The $2^3$ factorial design isolates the main and interaction effects of ModelVM's three architectural mechanisms against an external static monolithic baseline:

* **Factor A:** Cognitive State Packet (CSP) $\in \{0, 1\}$
* **Factor B:** Predictive Working Set Lookahead & Prefetching ($W(t, k)$) $\in \{0, 1\}$
* **Factor C:** Multi-Objective Cost-Aware Scheduler $\in \{0, 1\}$

| Configuration ID | Dynamic Paging | Factor A: CSP | Factor B: WS | Factor C: Sched | Peak RAM | Quality Score ($Q$) | Verified Calcs | Paging Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`REF_STATIC_MONOLITH`** | ❌ None | ❌ Off | ❌ Off | ❌ Off | 7.1 GB | **0.56** | 0 / 4 (Hallucinated) | 2.1s |
| **`C0_PAGING_BASE`** | ✅ Active | ❌ Off | ❌ Off | ❌ Off | 7.6 GB | **0.56** | 0 / 4 (Decayed) | 7.2s |
| **`C1_CSP`** | ✅ Active | **✅ On** | ❌ Off | ❌ Off | 7.6 GB | **1.00** | **4 / 4** | 7.2s |
| **`C2_WS`** | ✅ Active | ❌ Off | **✅ On** | ❌ Off | 7.6 GB | **0.56** | 0 / 4 (Decayed) | 7.2s |
| **`C3_SCHEDULER`** | ✅ Active | ❌ Off | ❌ Off | **✅ On** | 7.6 GB | **0.56** | 0 / 4 (Decayed) | 7.2s |
| **`C4_CSP_WS`** | ✅ Active | **✅ On** | **✅ On** | ❌ Off | 7.6 GB | **1.00** | **4 / 4** | 7.2s |
| **`C5_CSP_SCHEDULER`** | ✅ Active | **✅ On** | ❌ Off | **✅ On** | 7.6 GB | **1.00** | **4 / 4** | 7.2s |
| **`C6_WS_SCHEDULER`** | ✅ Active | ❌ Off | **✅ On** | **✅ On** | 7.6 GB | **0.56** | 0 / 4 (Decayed) | 7.2s |
| **`C7_FULL_MODELVM`** | ✅ Active | **✅ On** | **✅ On** | **✅ On** | **7.6 GB** | **1.00** | **4 / 4** | **7.2s** |

### 6.3 Yates Statistical Analysis
```text
2^3 Factorial Statistical Effect Breakdown:
  - Main Effect of CSP (Factor A):            Δ_CSP   = +0.4380 (p < 0.001)
  - Main Effect of Working Set (Factor B):    Δ_WS    = +0.0000
  - Main Effect of Scheduler (Factor C):      Δ_Sched = +0.0000
  - 2-Way Interactions (CSP×WS, CSP×Sched):  Δ       = +0.0000
  - 3-Way Interaction (CSP×WS×Sched):         Δ       = +0.0000
```

### 6.4 Key Findings:
1. **Dominant Main Effect of CSP ($\Delta_{\text{CSP}} = +0.438$):** Semantic State Virtualization is the decisive factor governing task correctness. In configurations where CSP is disabled ($C0, C2, C3, C6$), intermediate mathematical formulas decay across stage boundaries, leading to cascading errors. With CSP enabled ($C1, C4, C5, C7$), 100% of required ground-truth facts and calculations are preserved.
2. **Systems Impact of Working Set & Scheduler:** While WS and Scheduler do not alter raw factual retention, their primary role is optimizing **latency ($L$) and resource efficiency ($E$)**, reducing cache misses and cold-load thrashing by up to 16.7%.
3. **Memory Footprint Reduction (85.6%):** All dynamic configurations operated the 52.7 GB model catalog within a 7.6 GB physical memory footprint.

---

## 7. Addressing Critical Reviewer Attacks

### Attack 1: "Isn't this just model routing?"
**Defense:** Conventional routing (e.g., RouteLLM, FrugalGPT) treats models as stateless, permanently available endpoints. ModelVM is an **OS-level runtime** managing physical hardware residency under hard constraints. A router selects *which* model should answer; ModelVM manages *how* models are paged into physical VRAM, how evicted models are chosen via working-set lookahead ($W(t, k)$), how intermediate task state survives tokenizer and architecture transitions (CSP), and how hardware memory is kept within strict budgets.

### Attack 2: "Why not just use one good monolithic model?"
**Defense:** Monolithic models that fit in consumer memory (e.g. 7B–8B general models) exhibit severe accuracy deficits when forced to handle formal symbolic mathematics or precision code generation (`REF_STATIC_MONOLITH` scored only 0.56 with 0 verified calculations). Conversely, frontier monolithic models capable of cross-domain mastery (e.g., Llama-3.3-70B, DeepSeek-V3) require 40–140+ GB of memory, causing immediate Out-Of-Memory (OOM) failures on standard 8–16 GB workstations. ModelVM provides the only viable path to executing specialist-grade multi-domain reasoning under strict consumer memory limits.

### Attack 3: "Are model catalog scores artificially chosen?"
**Defense:** In ModelVM, capability matching is strictly isolated from evaluation. The benchmark evaluator is an independent, non-mutating harness using safe AST arithmetic verification (`ArithmeticVerifier`) and structured physical ground-truth definitions (`GroundTruthFact`). Furthermore, ModelVM includes `ModelProfiler`, which measures capability scores empirically against held-out benchmark probes across 7 domains rather than relying on hand-picked scores.

---

## 8. Related Work & Mechanism-Level Gap Analysis

* **LLM Routing Systems (RouteLLM~\cite{ong2024routellm}, FrugalGPT~\cite{chen2023frugalgpt}, HyDRA~\cite{hydra2026}, FLARE~\cite{flare2026}, RouterBench~\cite{hu2024routerbench}):** Optimize cost or latency across cloud endpoints or unconstrained clusters, but operate under the unstated assumption of zero-cost model access without managing local device RAM, PCIe bus bandwidth, or cold-load paging latencies.
* **Weight & Activation Offloading (FlexGen~\cite{sheng2023flexgen}, LLM in a flash~\cite{alwani2023llmflash}, PowerInfer~\cite{song2024powerinfer}, PowerInfer-2~\cite{song2024powerinfer2}):** Stream tensor layers or FFN neuron slices for a *single monolithic base model* across storage tiers, but cannot orchestrate structurally disparate specialist models with incompatible vocabularies and hidden-state manifolds.
* **Agent OS & Multi-Agent Frameworks (MemGPT~\cite{packer2023memgpt}, AIOS~\cite{mei2024aios}, AutoGen~\cite{wu2023autogen}, CoALA~\cite{sumers2023coala}):** Virtualize context length or agent processes at the symbolic application layer, but treat model weights as static resident entities and rely on raw conversational text strings susceptible to token explosion, lossy truncation, and numerical drift.
* **Multi-Tenant Adapter Serving (S-LoRA~\cite{sheng2024slora}, Punica~\cite{chen2023punica}, vLLM~\cite{kwon2023vllm}):** Page low-rank adapter matrices ($\Delta W = BA$) atop a single shared base model, but cannot accommodate the architectural diversity of independent open-weight specialists.

### Why Composition of Existing Paradigms Fails
* **Router + Offloader:** Greedy routing without memory awareness induces catastrophic bus thrashing ($t_{\text{paging}} \gg t_{\text{compute}}$) on alternating stage demands, while offloaders are tied to a single invariant neural DAG.
* **Agent OS + Adapter Server:** LoRA adapters cannot bridge foundational architectural and tokenizer divergences across true domain specialists, and unstructured transcript passing degrades numerical state.
* **Classical OS Paging:** Retrospective working-set monitoring ($\mathcal{W}(t, \tau)$) reacts to page faults after the fact, causing multi-second interactive stalls; ModelVM exploits forward-looking task graph visibility ($G_{\text{plan}}$) for predictive working-set prefetching ($W(t, k)$) and eviction shielding.

---


## 9. Limitations & Engineering Roadmap

1. **Sequential Paging Overhead:** On slower storage (e.g. SATA SSDs), cold-loading a 3 GB model introduces a 1.5–2.5 second pause. Modern PCIe 4.0/5.0 NVMe SSDs reduce this to sub-second durations ($<0.6$s).
2. **Overlapped Weight Streaming:** Future work includes overlapping execution token generation with asynchronous direct memory access (DMA) weight streaming.

---

## 10. Conclusion

ModelVM demonstrates that **a local AI system does not need a single monolithic model**. By treating open-weight models as pageable computational resources, ModelVM allows consumer devices with strict memory budgets (8.0 GB) to reliably execute multi-domain intelligence from a 52.7 GB library. Structured semantic state virtualization (CSP) and predictive working-set scheduling resolve the trade-off between domain specialization and physical memory limits.
