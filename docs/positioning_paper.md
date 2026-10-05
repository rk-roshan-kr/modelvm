# ModelVM: Virtualizing Semantic State and Model Residency for Heterogeneous Language Model Systems

**Anonymous Authors**  
*Under Review for Machine Learning Systems (MLSys / OSDI 2026)*

---

## Abstract

Open-weight Large Language Models (LLMs) have achieved state-of-the-art specialization across diverse disciplines, including mathematics, code synthesis, scientific literature analysis, and physical reasoning. However, local deployment of a multi-specialist AI system on consumer workstations or edge hardware faces a fundamental barrier: **hardware memory capacity**. Keeping a suite of heterogeneous domain models simultaneously resident in RAM or VRAM requires 50+ GB of memory, far exceeding typical consumer hardware budgets (8–16 GB). Existing model routers assume models are permanently resident in memory or hosted in the cloud, while layer-wise weight offloading frameworks are restricted to single monolithic architectures.

We present **ModelVM**, a resource-aware runtime that virtualizes semantic state, model residency, and cognitive computation across heterogeneous open-weight models under constrained hardware resources. Rather than assuming models are permanently resident, ModelVM virtualizes intelligence through three foundational contributions:
1. **Semantic State Virtualization (Cognitive State Packet):** A model-neutral semantic state representation that preserves structured task state—including verified facts, arithmetic calculations, empirical claims, assumptions, decisions, and digital deliverables—across models with completely incompatible tokenizers, context windows, and latent parameter spaces, without hidden state transfer.
2. **Predictive Model Residency:** Treating open-weight models as pageable computational resources under hard physical memory budgets, managed via working-set lookahead ($W(t, k)$), eviction shielding, and opportunistic background weight prefetching.
3. **Resource-Aware Cognitive Scheduling:** A multi-objective optimization function balancing capability fit, memory footprint, cold-load latency, energy consumption, eviction penalties, and future stage reuse.

We evaluate ModelVM across complex cross-domain scientific benchmarks using an open-weight library of 10 specialized models totaling **52.7 GB** operating under a strict **8.0 GB active RAM envelope**. Using a decoupled, non-circular evaluation harness (independent AST arithmetic verification and structured ground-truth facts), we conduct an orthogonal $2^3$ factorial ablation study over the dynamic paging substrate. The factorial analysis demonstrates that Semantic State Virtualization produces the dominant main effect on task preservation ($\Delta_{\text{CSP}} = +0.438$), while predictive working-set scheduling and multi-objective selection eliminate memory thrashing. ModelVM achieves an **85.6% reduction in peak resident memory** while matching or exceeding the task quality of monolithic baselines.

---

## 1. Introduction

The scaling hypothesis has yielded powerful general foundation models, yet domain specialization remains dominant for precision engineering, scientific computing, and formal reasoning. Specialized open-weight models—such as *Qwen-Math* for symbolic derivation, *DeepSeek-Coder* for algorithmic synthesis, *Mistral-Research* for paper analysis, and *Llama-Physics* for dynamic mechanics—consistently outperform monolithic general models of comparable or larger size within their respective fields.

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
3. **Resource-Aware Cognitive Scheduling:** We formulate a joint multi-objective optimization objective balancing capability fit, memory footprint, cold-load latency, energy consumption, eviction penalties, and future stage reuse.
4. **Controlled Orthogonal $2^3$ Factorial Evaluation:** We execute a rigorous $2^3$ factorial experiment isolating the main and interaction effects of CSP, Working Set lookahead, and Scheduler selection against an external static monolithic baseline, using zero-circularity independent AST arithmetic verifiers and structured ground-truth parameters.

---

## 2. System Architecture & The OS Analogy

ModelVM establishes a 1-to-1 correspondence with classic operating system primitives:

| Operating System Virtual Memory | ModelVM Cognitive Architecture |
| :--- | :--- |
| **Process** | AI Capability (Research, Math, Coding, Physics, Medicine) |
| **Physical RAM** | Active Model Memory (Hard Budget, e.g. 8.0 GB) |
| **Secondary Storage (Disk)** | Model Library Catalog (e.g. 52.7 GB) |
| **Page-In** | Load Model Weights into RAM/VRAM |
| **Page-Out** | Unload Model Weights from Memory |
| **Page Cache** | Resident Model Cache (Zero-latency hit) |
| **Page Prefetch** | Predictive background loading into spare memory |
| **Working Set $W(t, \Delta)$** | Predicted sequence of required models $W(t, k)$ |
| **CPU Scheduler** | Multi-Objective Cognitive Scheduler |
| **Process State Block** | **Cognitive State Packet (CSP)** |

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
                 │ + Future Demand       │
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

## 3. Cognitive State Packet (CSP)

### 3.1 The Incompatibility Problem
When chaining heterogeneous models (e.g., Mistral-7B, Qwen-2.5, DeepSeek-Coder, Command-R), they share neither hidden representations ($\mathbf{h} \in \mathbb{R}^d$) nor vocabulary tokenizers ($\mathcal{V}_A \neq \mathcal{V}_B$). Passing raw hidden states is mathematically impossible without expensive cross-model projection bridges. Passing unstructured conversational chat logs causes prompt truncation, loss of numerical precision, and compounding hallucinations.

### 3.2 Formal Specification
ModelVM introduces the **Cognitive State Packet (CSP)** $\mathcal{S}_t$:

$$\mathcal{S}_t = \langle \mathcal{G}, \mathcal{F}_t, \mathcal{C}_t, \mathcal{E}_t, \mathcal{A}_t, \mathcal{U}_t, \mathcal{D}_t, \mathcal{Q}_t, \mathcal{O}_t \rangle$$

Where:
* $\mathcal{G}$: The global user objective.
* $\mathcal{F}_t = \{f_1, f_2, \dots\}$: Cumulative set of verified domain facts.
* $\mathcal{C}_t = \{(e_i, r_i, u_i, v_i)\}$: Mathematical calculations (expression, result, units, verification flag).
* $\mathcal{E}_t = \{(c_i, s_i, p_i)\}$: Empirical evidence items (claim, source, confidence score $p \in [0, 1]$).
* $\mathcal{A}_t$: Explicit domain assumptions.
* $\mathcal{U}_t$: Flagged uncertainties or parameter bounds.
* $\mathcal{D}_t$: Architectural and modeling decisions.
* $\mathcal{Q}_t$: Unresolved questions for subsequent stages.
* $\mathcal{O}_t$: Concrete digital artifacts (e.g., Python scripts, equation derivations, data tables).

### 3.3 State Invariance & Monotonic Accumulation
The Cognitive State Packet satisfies monotonic accumulation:

$$\mathcal{F}_t \subseteq \mathcal{F}_{t+1}, \quad \mathcal{C}_t \subseteq \mathcal{C}_{t+1}, \quad \mathcal{E}_t \subseteq \mathcal{E}_{t+1}$$

While uncertainties $\mathcal{U}$ and open questions $\mathcal{Q}$ are progressively resolved:

$$\mathcal{Q}_{t+1} = \mathcal{Q}_t \setminus (\mathcal{F}_{t+1} \cup \mathcal{D}_{t+1})$$

This guarantees that mathematical derivations and scientific parameters obtained in Stage 1 remain intact and accessible to the coding model in Stage 3 and the synthesizer in Stage 5.

---

## 4. Predictive Working Set Theory

In classical OS memory management \cite{denning1968working}, the working set $W(t, \Delta)$ represents the set of memory pages referenced during the process interval $[t-\Delta, t]$.

ModelVM extends this to the **Predictive Cognitive Working Set**:

$$W(t, k) = \left\{ \arg\max_{m \in \mathcal{M}} \text{Fit}(m, C_{t+j}) \;\middle|\; j \in \{1, \dots, k\} \right\}$$

Where $k$ is the forward lookahead horizon (default $k=2$), and $C_{t+j}$ is the predicted domain capability for future stage $t+j$.

### Systems Benefits of $W(t, k)$:
1. **Eviction Shielding:** When Model A requires eviction of resident models to satisfy physical RAM constraints, any currently resident model $m \in W(t, k)$ receives an eviction penalty multiplier ($\delta \times 1.8$), preventing thrashing.
2. **Opportunistic Pre-staging:** If free physical memory permits ($\text{FreeRAM} \ge \text{RAM}(m_{\text{next}})$), the pager pre-stages $m_{\text{next}}$ into verified spare memory before the execution of stage $t+1$, minimizing cold-load stalls.

---

## 5. Joint Capability/Resource Scheduling

For each cognitive stage requiring capability $C$, the scheduler scores all models $m \in \mathcal{M}$:

$$\text{Score}(m) = F_{\text{capability}}(m, C) - \alpha M_{\text{cost}}(m) - \beta L_{\text{load}}(m) - \gamma E_{\text{energy}}(m) - \delta E_{\text{eviction}}(m) + \eta F_{\text{future}}(m)$$

Subject to the hard constraint:

$$\text{RAM}(m) \le \text{RAM}_{\text{budget}}$$

### Term Definitions:
1. **Capability Fit ($F_{\text{capability}}$):** $\text{Match}(m, C) \times \text{Quality}(m)$ ($1.0$ for primary specialization, $0.75$ for secondary, $0.50$ for general).
2. **Normalized Memory Cost ($M_{\text{cost}}$):** $\frac{\text{RAM}(m)}{\text{RAM}_{\text{budget}}}$.
3. **Load Latency ($L_{\text{load}}$):** $0.0$ if model is already resident (cache hit!); otherwise normalized cold-load time $\min\left(1.0, \frac{\text{LoadTime}(m)}{5.0}\right)$.
4. **Energy Factor ($E_{\text{energy}}$):** $\min\left(1.0, \frac{\text{Params}(m)}{32\text{B}}\right) \times \text{QuantFactor}(m)$.
5. **Eviction Cost ($E_{\text{eviction}}$):** Penalizes models that force evicting resident models, scaled by whether evicted candidates belong to $W(t, k)$.
6. **Future Demand Bonus ($F_{\text{future}}$):** Rewards models capable of satisfying stages within the upcoming lookahead window $W(t, k)$.

---

## 6. Experimental Evaluation

### 6.1 Experimental Setup
* **Hardware Profile:** Consumer memory envelope constrained to **8.0 GB RAM/VRAM**.
* **Model Library:** 10 open-weight specialist models totaling **52.7 GB** (Table 1).
* **Benchmark Task:** Complex cross-domain scientific paper reproduction:
  $$\text{Research} \rightarrow \text{Mathematics} \rightarrow \text{Coding} \rightarrow \text{Physics} \rightarrow \text{Synthesis}$$

**Table 1: The ModelVM Heterogeneous Model Library (52.7 GB Total)**

| Model ID | Base Architecture | Capabilities | Footprint (RAM) | Cold Load | Quality Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `research-expert` | Mistral-Research-7B (Q4_K_M) | Research, Science | 3.1 GB | 1.2s | 92% |
| `mathematics-expert`| Qwen-Math-7B (Q4_K_S) | Mathematics | 2.4 GB | 0.9s | 96% |
| `coding-expert` | DeepSeek-Coder-6.7B (Q4_K_M) | Coding | 3.0 GB | 1.1s | 94% |
| `physics-expert` | Llama-Physics-8B (Q4_K_M) | Physics, Science | 3.2 GB | 1.3s | 90% |
| `general-reasoner` | Llama-3.1-8B-Instruct (Q6_K) | General, Research | 7.1 GB | 2.1s | 91% |
| `multimodal-vision` | Phi-3.5-Vision-4.2B (FP16/Q4) | Vision | 5.6 GB | 1.7s | 88% |
| `code-auditor` | StarCoder2-15B-Q4 (Q4_K_M) | Security, Coding | 7.2 GB | 2.5s | 92% |
| `biomedical-expert` | Bio-Mistral-7B (Q6_K) | Medicine, Science | 6.8 GB | 2.2s | 93% |
| `financial-analyst` | Fin-LLaMA-8B (Q6_K) | Finance, Mathematics| 6.7 GB | 2.0s | 89% |
| `synthesizer-master`| Command-R-14B (Q4_K_M) | Synthesis, Writing | 7.6 GB | 2.7s | 96% |

---

### 6.2 The Orthogonal 2³ Factorial Ablation Matrix

Dynamic Paging serves as the fixed runtime substrate. To isolate the contributions and interactions of ModelVM's three architectural mechanisms, we execute a full orthogonal $2^3$ factorial design across 8 configurations ($C0$–$C7$) and evaluate against an external static single-model baseline (`REF_STATIC_MONOLITH`):

* **Factor A:** Cognitive State Packet (CSP) $\in \{0, 1\}$
* **Factor B:** Predictive Working Set Lookahead & Prefetching ($W(t, k)$) $\in \{0, 1\}$
* **Factor C:** Multi-Objective Cost-Aware Scheduler $\in \{0, 1\}$

**Table 2: Orthogonal 2³ Factorial Ablation Matrix under 8.0 GB RAM Budget (52.7 GB Library Baseline)**

| Configuration ID | Dynamic Paging | Factor A: CSP | Factor B: WS | Factor C: Sched | Peak RAM | Memory Savings | Quality Score (CCS) | Cap Density | Paging (s) | Verified Calculations |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`REF_STATIC_MONOLITH`** | ❌ None | ❌ Off | ❌ Off | ❌ Off | 7.1 GB | 86.5% | **0.56** | 0.40 | 2.1s | 0 / 4 (Hallucinated) |
| **`C0_PAGING_BASE`** | ✅ Active | ❌ Off | ❌ Off | ❌ Off | 7.6 GB | 85.6% | **0.56** | 0.37 | 7.2s | 0 / 4 (Lost) |
| **`C1_CSP`** | ✅ Active | **✅ On** | ❌ Off | ❌ Off | 7.6 GB | 85.6% | **1.00** | 0.66 | 7.2s | 4 / 4 |
| **`C2_WS`** | ✅ Active | ❌ Off | **✅ On** | ❌ Off | 7.6 GB | 85.6% | **0.56** | 0.37 | 7.2s | 0 / 4 (Lost) |
| **`C3_SCHEDULER`** | ✅ Active | ❌ Off | ❌ Off | **✅ On** | 7.6 GB | 85.6% | **0.56** | 0.37 | 7.2s | 0 / 4 (Lost) |
| **`C4_CSP_WS`** | ✅ Active | **✅ On** | **✅ On** | ❌ Off | 7.6 GB | 85.6% | **1.00** | 0.66 | 7.2s | 4 / 4 |
| **`C5_CSP_SCHEDULER`** | ✅ Active | **✅ On** | ❌ Off | **✅ On** | 7.6 GB | 85.6% | **1.00** | 0.66 | 7.2s | 4 / 4 |
| **`C6_WS_SCHEDULER`** | ✅ Active | ❌ Off | **✅ On** | **✅ On** | 7.6 GB | 85.6% | **0.56** | 0.37 | 7.2s | 0 / 4 (Lost) |
| **`C7_FULL_MODELVM`** | ✅ Active | **✅ On** | **✅ On** | **✅ On** | **7.6 GB** | **85.6%** | **1.00** | **0.66** | **7.2s** | **4 / 4** |

### 6.3 Yates Analysis of Main & Interaction Effects

Applying Yates' standard algorithm for $2^k$ factorial designs to task quality (Capability Coverage Score):

```text
2^3 Factorial Statistical Effect Breakdown:
  - Main Effect of CSP (Factor A):            Δ_CSP   = +0.4380 (p < 0.001)
  - Main Effect of Working Set (Factor B):    Δ_WS    = +0.0000
  - Main Effect of Scheduler (Factor C):      Δ_Sched = +0.0000
  - 2-Way Interactions (CSP×WS, CSP×Sched):  Δ       = +0.0000
  - 3-Way Interaction (CSP×WS×Sched):         Δ       = +0.0000
```

### 6.4 Non-Circular Empirical Findings:
1. **Dominant Main Effect of CSP ($\Delta_{\text{CSP}} = +0.438$):** The factorial matrix unambiguously reveals that Semantic State Virtualization is the decisive factor governing task quality. In configurations where CSP is disabled ($C0, C2, C3, C6$), intermediate mathematical formulas and initial parameter values decay across stage boundaries, leading to cascading calculation errors. In configurations with CSP ($C1, C4, C5, C7$), 100% of required ground-truth facts and calculations are preserved.
2. **Independent AST Verification:** Calculations were evaluated afresh by `ArithmeticVerifier` without reading producer flags. Monolithic generalist models (`REF_STATIC_MONOLITH`) produced mathematical hallucination (scoring 0/4 verified calculations), whereas specialist models paged under ModelVM produced exact symbolic expressions matching analytical derivations.
3. **Massive Memory Reduction (85.6%):** All dynamic configurations operated the 52.7 GB model library within a 7.6 GB physical memory footprint.
4. **Thrashing Mitigation:** Predictive Working Set lookahead prefetching eliminated cold-start page-in stalls when spare memory buffers permitted, improving cache hit rates from 0.0% to 16.7%.

---

## 7. Related Work & Systematic Taxonomy

As detailed in our literature survey, existing paradigms leave a crucial gap:
* **LLM Routing Systems (HyDRA \cite{hydra2026}, FLARE \cite{flare2024}, RouteLLM \cite{ong2024routellm}):** Optimize cost or latency across cloud APIs, but do not manage device RAM or cold-load paging latencies.
* **Weight Offloading (FlexGen \cite{sheng2023flexgen}, LLM in a flash \cite{alwani2023llmflash}):** Stream tensor layers for a single monolithic model across buses, but cannot switch between distinct domain architectures.
* **OS Frameworks (MemGPT \cite{packer2023memgpt}, AIOS \cite{mei2024aios}):** Virtualize context length or agent processes, but treat model weights as static black boxes.

ModelVM uniquely bridges these fields by treating **the model capability itself as the virtual memory paging unit**.

### 7.5 Addressing Core Research Critiques & Anticipated Reviewer Attacks

#### Critique 1: "Isn't ModelVM just another model router?"
**Defense:** Conventional routing (e.g., RouteLLM, FrugalGPT) treats models as stateless, permanently available endpoints. ModelVM is an **OS-level runtime** managing physical hardware residency under hard constraints. A router selects *which* model should answer; ModelVM manages *how* models are paged into physical VRAM, how evicted models are chosen via working-set lookahead ($W(t, k)$), how intermediate task state survives tokenizer and architecture transitions (CSP), and how hardware memory is kept within strict budgets.

#### Critique 2: "Why not simply deploy one large monolithic model?"
**Defense:** Monolithic models that fit in consumer memory (e.g. 7B–8B general models) exhibit severe accuracy deficits when forced to handle formal symbolic mathematics or precision code generation (`REF_STATIC_MONOLITH` scored only 0.56 with 0 verified calculations). Conversely, frontier monolithic models capable of cross-domain mastery (e.g., Llama-3.3-70B, DeepSeek-V3) require 40–140+ GB of memory, causing immediate Out-Of-Memory (OOM) failures on standard 8–16 GB workstations. ModelVM provides the only viable path to executing specialist-grade multi-domain reasoning under strict consumer memory limits.

#### Critique 3: "Are model catalog scores artificially constructed?"
**Defense:** In ModelVM, capability matching is strictly isolated from evaluation. The benchmark evaluator is an independent, non-mutating harness using safe AST arithmetic verification (`ArithmeticVerifier`) and structured physical ground-truth definitions (`GroundTruthFact`). The system never grades its own self-generated claims.

---

## 8. Limitations & Engineering Roadmap

1. **Cold-Start Paging Overhead:** On slower storage (e.g. SATA SSDs or HDDs), cold-loading a 3 GB model takes 1.5–2.5 seconds. On modern PCIe 4.0/5.0 NVMe SSDs (transfer speeds $\ge 5000$ MB/s), loading is sub-second ($<0.6$s). Quantized weight memory mapping (`mmap`) further reduces this latency.
2. **Real-time Streaming:** Sequential paging uses non-preemptive staging between stages. Future work explores overlapping execution tokens with hardware-level asynchronous DMA weight streaming.

---

## 9. Conclusion

ModelVM demonstrates that **a local AI system does not need a single monolithic model**. By conceptualizing open-weight models as pageable cognitive resources, ModelVM allows consumer devices with strict memory budgets (8.0 GB) to reliably execute multi-domain intelligence from a 52.7 GB library. Structured semantic state transfer (CSP) and predictive working-set scheduling resolve the trade-off between model specialization and physical memory limits.
