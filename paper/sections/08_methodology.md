# 8. Experimental Methodology

Systems claims require empirical isolation. While the conceptual synthesis of semantic state virtualization and predictive residency is architecturally cohesive, its scientific validity rests entirely on whether these abstractions yield measurable advantages over conventional execution paradigms. This section details our experimental apparatus, model catalog, benchmark workloads, baseline spectrum, token-budget controls, and statistical verification protocols.

---

## 8.1 Research Questions

Our evaluation systematically targets four foundational research questions, mapped directly to the core hypotheses formulated in our system design:

* **RQ1 (State Virtualization):** Does mediating multi-model transitions through a typed Cognitive State Packet ($\mathcal{S}_t$) preserve domain facts, numerical precision, and procedural deliverables significantly better than raw conversational text handoffs under identical context limits, generation budgets, and memory constraints? (**H1**)
* **RQ2 (Predictive Residency):** Does stage-level working-set lookahead ($W(t, k)$) coupled with eviction shielding and opportunistic prefetching reduce cold-load I/O stalls and memory thrashing compared to classical recency-based eviction policies? (**H2**)
* **RQ3 (Resource-Aware Scheduling):** Does multi-objective scheduling grounded in empirical capability profiling outperform greedy capability-only selection and memory-aware greedy heuristics, approaching offline oracle bounds under constrained runtime memory? (**H3**)
* **RQ4 (Systemic Trade-Offs):** Does the integrated ModelVM runtime establish a superior Quality–Memory–Latency Pareto frontier relative to monolithic models, static specialist ensembles, and reactive paging frameworks? (**H4**)

---

## 8.2 Hardware Testbeds & Measurement Apparatus

To ensure our findings reflect physical runtime behavior rather than idealized simulation artifacts, all experiments are executed across physical commodity hardware configurations representative of constrained workstations and edge nodes (Table 1).

**Table 1: Physical Hardware Evaluation Testbeds**

| Component | Primary Testbed (Workstation) | Constrained Node (Edge) |
| :--- | :--- | :--- |
| **CPU** | AMD Ryzen 9 5900X (12c/24t @ 3.7–4.8 GHz) | Intel Core i7-11800H (8c/16t @ 2.3–4.6 GHz) |
| **Host System RAM** | 32 GB DDR4-3600 CL16 | 16 GB DDR4-3200 |
| **Runtime Memory Budget ($\mathcal{B}_{\text{RAM}}$)** | **8.0 GB Enforced Runtime Envelope** | **8.0 GB Enforced Runtime Envelope** |
| **Storage Subsystem** | 2 TB Samsung 980 Pro PCIe 4.0 NVMe SSD | 512 GB PCIe 3.0 NVMe SSD |
| **Storage Transfer Rate** | 6,900 MB/s Sequential Read | 2,400 MB/s Sequential Read |
| **Accelerator (GPU)** | NVIDIA GeForce RTX 3080 (10 GB GDDR6X) | NVIDIA GeForce RTX 3060 Mobile (6 GB GDDR6) |
| **CUDA / Driver Stack** | CUDA 12.4 / Driver 550.54 | CUDA 12.2 / Driver 535.104 |
| **Operating System** | Ubuntu 22.04 LTS (Linux Kernel 6.5) | Windows 11 / WSL2 Linux Subsystem |

### Hierarchical Memory Accounting
We explicitly distinguish between the host machine's total physical capacity (32 GB / 16 GB) and the **enforced runtime memory budget** ($\mathcal{B}_{\text{RAM}} = 8.0$ GB) imposed on model execution. Furthermore, we model a hierarchical three-tier memory architecture:

$$\text{Storage (NVMe)} \longrightarrow \text{Host RAM} \longrightarrow \text{Accelerator VRAM}$$

Telemetry tracks both tiers independently:
* **Host CPU Memory ($M_{\text{RAM}}(t)$):** Process Resident Set Size (RSS) sampled via `/proc/[pid]/statm` and OS counters at 10 ms intervals via `psutil`, capturing tokenizer buffers, Python runtime overhead, and CPU host weights.
* **Accelerator Memory ($M_{\text{VRAM}}(t)$):** Dedicated device memory tracked via NVML (`pynvml`) query hooks executed immediately before and after every paging transition:
  $$M_{\text{VRAM}}(t) = M_{\text{weights}}(t) + M_{\text{workspace}}(t) + M_{\text{KV}}(t)$$
* **Peak Memory Footprint ($M_{\text{peak}}$):** $\max_t \left( M_{\text{RAM}}(t), M_{\text{VRAM}}(t) \right)$, reported alongside tier-specific breakdowns.

Paging latency is recorded using monotonic nanosecond wall-clock timers (`time.perf_counter_ns`).

---

## 8.3 Heterogeneous Model Catalog

Our model library comprises ten open-weight models spanning six distinct architectural families, totaling 52.7 GB in aggregate configured RAM requirements and 64.0 GB of parameter data when serialized on disk (Table 2). Models were selected specifically for documented domain specialization rather than arbitrary scale.

**Table 2: The ModelVM Heterogeneous Open-Weight Model Library (52.7 GB Aggregate Configured RAM Requirement, 64.0 GB Serialized Disk Storage)**

| Model Identifier | Base Architecture | Quantization | Params | RAM Req. | Weights VRAM | Workspace | Cold Load | Inference Latency |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `research-expert` | MistralForCausalLM | Q4_K_M | 7.2B | 3.1 GB | 2.2 GB | 0.4 GB | 1.2s | 32 ms/tok |
| `mathematics-expert`| Qwen2ForCausalLM | Q4_K_S | 7.0B | 2.4 GB | 1.6 GB | 0.3 GB | 0.9s | 28 ms/tok |
| `coding-expert` | DeepSeekForCausalLM | Q4_K_M | 6.7B | 3.0 GB | 2.1 GB | 0.4 GB | 1.1s | 30 ms/tok |
| `physics-expert` | LlamaForCausalLM | Q4_K_M | 8.0B | 3.2 GB | 2.3 GB | 0.4 GB | 1.3s | 34 ms/tok |
| `general-reasoner` | LlamaForCausalLM | Q6_K | 8.0B | 7.1 GB | 6.2 GB | 0.5 GB | 2.1s | 42 ms/tok |
| `multimodal-vision` | Phi3VForCausalLM | FP16/Q4 | 4.2B | 5.6 GB | 4.8 GB | 0.4 GB | 1.7s | 38 ms/tok |
| `code-auditor` | StarCoder2ForCausalLM | Q4_K_M | 14.0B | 7.2 GB | 6.1 GB | 0.6 GB | 2.5s | 44 ms/tok |
| `biomedical-expert` | MistralForCausalLM | Q6_K | 7.2B | 6.8 GB | 5.9 GB | 0.5 GB | 2.2s | 40 ms/tok |
| `financial-analyst` | LlamaForCausalLM | Q6_K | 8.0B | 6.7 GB | 5.8 GB | 0.5 GB | 2.0s | 39 ms/tok |
| `synthesizer-master`| CohereForCausalLM | Q4_K_M | 14.0B | 7.6 GB | 6.5 GB | 0.6 GB | 2.7s | 46 ms/tok |

To ground capability terms in empirical measurement rather than subjective manual weights, each model in Table 2 was evaluated via `ModelProfiler`, benchmarking candidate models across held-out standardized probes in seven domains (formal mathematics, algorithmic coding, classical mechanics, paper synthesis, financial calculation, diagnostic reasoning, and general logic). The resultant empirical capability matrix $\mathbf{P} \in [0, 1]^{N \times M}$ grounds scheduler decisions directly in measured task performance.

---

## 8.4 Workloads & The Multi-Stage Pipeline

Evaluating cross-model virtualization demands tasks characterized by deep procedural dependency. A single-shot query provides no insight into state decay. The benchmark workload intentionally spans multiple specialized domains for which capability varies substantially across the model catalog, modeled as a directed acyclic graph $G = (S, E)$.

The canonical benchmark workload spans five consecutive cognitive stages:

$$s_0\,(\text{Research}) \longrightarrow s_1\,(\text{Math}) \longrightarrow s_2\,(\text{Coding}) \longrightarrow s_3\,(\text{Physics}) \longrightarrow s_4\,(\text{Synthesis})$$

Specifically, the workflow requires:
1. Extracting physical constants, hypotheses, and governing equations from archival publication text ($s_0$).
2. Deriving closed-form symbolic solutions and evaluating numerical boundary conditions ($s_1$).
3. Synthesizing an executable Python simulation implementing the mathematical derivation ($s_2$).
4. Verifying energy conservation laws, phase-space trajectories, and dimensional consistency ($s_3$).
5. Producing a structured publication-grade executive technical brief summarizing findings ($s_4$).

Every stage produces concrete domain deliverables that form strict prerequisite inputs for subsequent stages. State degradation is cumulative: an arithmetic error in $s_1$ causes simulation collapse in $s_2$ and boundary violations in $s_3$.

---

## 8.5 Token-Budget & Execution Controls

To prevent context-length discrepancies from acting as confounding variables in state virtualization experiments (EXP-H1), all model invocations adhere to strict token controls:
* **Maximum Context Window ($W_{\text{in}}$):** Fixed at 4,096 tokens across all models.
* **Maximum Generation Ceiling ($T_{\text{gen}}$):** Fixed at 1,024 tokens per stage.
* **Decoding Parameters:** Held constant at temperature $T = 0.0$ (greedy deterministic argmax), top-$p = 1.0$, and repetition penalty $1.0$.
* **Raw Text Handoff Protocol:** The unstructured conversational transcript of previous stage outputs is concatenated into the system prompt prefix of stage $s_t$. When cumulative text exceeds $W_{\text{in}} - T_{\text{gen}}$, a standard first-in, first-out (FIFO) sliding window truncates early tokens.
* **CSP Handoff Protocol:** The typed state packet $\mathcal{S}_{t-1}$ is serialized into schema text within the prompt prefix. Token consumption of the serialized CSP is logged independently to quantify representation overhead.

---

## 8.6 Baseline Spectrum

To systematically isolate individual systems mechanisms, ModelVM is evaluated against a structured baseline continuum:

* **$B_0$ (Static Monolith):** A single 8B instruction model (`general-reasoner`) retained permanently resident in memory. It executes all five stages sequentially without model switching or state serialization, representing the standard consumer deployment strategy.
* **$B_{\text{static}}$ (Static Specialist Ensemble):** A fixed subset of specialists fitting within the 8.0 GB runtime envelope simultaneously (`mathematics-expert` [2.4 GB] + `coding-expert` [3.0 GB] = 5.4 GB). The system routes strictly between these resident models; non-specialized stages fall back to the resident model with the highest capability match without paging.
* **$B_1$ (Unconstrained Specialist Router):** An upper-bound specialist router (analogous to RouteLLM or FrugalGPT). It selects the optimal specialist from the 10-model library for every stage under the presumption of infinite memory ($\mathcal{B}_{\text{RAM}} = \infty$). This baseline isolates model-selection quality from residency constraints and does not represent a deployable constrained system.
* **$B_2$ (Router + Raw Text + Reactive LRU):** Specialist routing with dynamic model loading constrained to $\mathcal{B}_{\text{RAM}} = 8.0$ GB. Eviction follows classical Least-Recently-Used (LRU) policy with no working-set lookahead or prefetching. State is transferred via raw conversational transcript concatenation.
* **$B_3$ (Router + CSP + Unconstrained):** Specialist routing with structured Semantic State Virtualization (CSP) evaluated under unconstrained memory ($\mathcal{B}_{\text{RAM}} = \infty$), isolating pure CSP efficacy from paging overhead.
* **$B_4$ (Router + CSP + Reactive LRU):** Combines structured CSP state virtualization with constrained dynamic paging under $\mathcal{B}_{\text{RAM}} = 8.0$ GB, but retains reactive LRU eviction without predictive working-set scheduling.
* **$B_5$ (Full ModelVM):** The integrated runtime incorporating Semantic State Virtualization (CSP), Predictive Working Set management ($W(t, k)$), eviction shielding, and multi-objective scheduling under the strict 8.0 GB runtime budget.
* **$B_{\text{oracle}}$ (Offline Oracle Scheduler):** A theoretical upper-bound scheduler with perfect advance knowledge of all pipeline stage requirements, selecting model residency sequences to minimize cold-load stalls under $\mathcal{B}_{\text{RAM}} = 8.0$ GB.

---

## 8.7 Factorial Ablation Design

Beyond baseline comparisons, we decompose ModelVM through an orthogonal $2^3$ factorial experimental design. Dynamic paging serves as the invariant physical substrate. We systematically toggle three binary factors across eight configurations ($C_0$ through $C_7$):

* **Factor A (CSP):** $\in \{\text{Disabled (Raw Text)}, \text{Enabled (Typed CSP)}\}$
* **Factor B (Working Set):** $\in \{\text{Disabled (Reactive LRU)}, \text{Enabled (Predictive } W(t, k))\}$
* **Factor C (Scheduler):** $\in \{\text{Disabled (Greedy Match)}, \text{Enabled (Multi-Objective)}\}$

This design permits systematic estimation of main effects ($\Delta_{\text{CSP}}, \Delta_{\text{WS}}, \Delta_{\text{Sched}}$) and all two-way and three-way interaction terms without confounding among the factorial factors. Replicated trial variance is preserved by computing effect estimates across independent experimental runs.

---

## 8.8 Evaluation Metrics Framework

We evaluate systems across four complementary evaluation dimensions:

### 1. Quality ($Q$)
* **Capability Coverage Score (CCS):** The fraction of required domain deliverables successfully synthesized across the workflow, normalized in $[0.0, 1.0]$.
* **Calculation Correctness Ratio ($R_{\text{calcs}}$):** The proportion of analytical expressions whose computed results match exact symbolic ground truth within numerical tolerance ($10^{-4}$):
  $$R_{\text{calcs}} = \frac{1}{|C|} \sum_{c \in C} \mathbf{1}\left( \text{ASTVerify}(c.\text{expr}, c.\text{result}) \right)$$

### 2. State Retention ($R$)
* **Factual Preservation Ratio ($R_{\text{facts}}$):** The fraction of ground-truth physical constants, hypotheses, and parameters originating in stage $s_0$ that remain present, uncorrupted, and accurately referenced in final deliverables at stage $s_4$:
  $$R_{\text{facts}} = \frac{|\mathcal{F}_{\text{retained}} \cap \mathcal{F}_{\text{ground\_truth}}|}{|\mathcal{F}_{\text{ground\_truth}}|}$$
* **Semantic Drift Index ($D_{\text{drift}}$):** Quantitative measurement of numerical value drift across consecutive model handoffs.

### 3. Resource Consumption ($E$)
* **Peak Memory Footprint ($M_{\text{peak}}$):** Maximum instantaneous physical RAM/VRAM consumed during execution (in gigabytes).
* **Memory Virtualization Ratio ($V_{\text{ratio}}$):** The ratio of total library parameter size to peak physical memory consumed: $V_{\text{ratio}} = T_{\text{library}} / M_{\text{peak}}$.
* **Budget Invariant Compliance:** Continuous verification that $\sum \text{RAM}(m_{\text{resident}}) \le \mathcal{B}_{\text{RAM}}$ is maintained at all timestamps without kernel OOM intervention.

### 4. Latency & Systems Efficiency ($L$)
* **Cold-Load Paging Overhead ($t_{\text{paging}}$):** Cumulative wall-clock seconds spent loading model weights from NVMe storage into memory.
* **Cache Hit Rate ($H_{\text{cache}}$):** Fraction of stage transitions where the selected model was already resident in memory:
  $$H_{\text{cache}} = \frac{N_{\text{hits}}}{N_{\text{transitions}}}$$
* **Model Reload Frequency ($N_{\text{reload}}$):** Count of redundant page-in operations where a previously evicted model is re-loaded due to cyclic demand or cache thrashing.

---

## 8.9 Statistical Rigor & Non-Circularity Harness

A pervasive weakness in multi-model literature is circular grading, where an orchestration system grades its own self-generated outputs using another language model instance. We strictly eliminate this circularity:

1. **Independent AST Verification:** Mathematical assertions and code outputs are never evaluated by prompting an LLM. Instead, our verification engine parses candidate calculation strings into Python Abstract Syntax Trees (`ast.parse`), extracting operators, constants, and variables into a sandboxed execution context to verify mathematical equivalence deterministically.
2. **Immutable Ground Truth:** Physical parameters, boundary values, and derivation targets are encapsulated in pre-registered `GroundTruthFact` objects. Tolerance checking is enforced mathematically ($|\hat{y} - y^*| < 10^{-4}$).
3. **Repetitions and Statistical Testing:** All configurations are evaluated on $n = 10$ identical seeded workload instances. We report paired differences alongside 95% empirical bootstrap percentile confidence intervals:
  $$\text{CI}_{95} = [q_{0.025}, q_{0.975}]$$
  derived from 2,000 bootstrap resamples. Statistical significance for pairwise baseline comparisons (EXP-H1, EXP-H2, EXP-H3) is assessed via two-sided paired permutation tests on matched workload trials, applying the Holm-Bonferroni step-down correction for multiple comparisons ($p < 0.05$). For the orthogonal $2^3$ factorial ablation study (EXP-FACT), parameter main effects and interaction estimates are computed via replicated Yates analysis, with inferential significance evaluated through a three-factor factorial ANOVA model containing all two-way and three-way interaction terms.
