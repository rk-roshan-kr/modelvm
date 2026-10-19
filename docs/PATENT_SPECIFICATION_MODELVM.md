# UNITED STATES PATENT APPLICATION SPECIFICATION

**TITLE OF THE INVENTION:**  
**SYSTEMS AND METHODS FOR VIRTUALIZING MODEL RESIDENCY AND SEMANTIC TASK STATE IN MEMORY-CONSTRAINED MACHINE LEARNING RUNTIMES**

**INVENTOR(S):**  
Roshan Kumar Gupta

---

## CROSS-REFERENCE TO RELATED APPLICATIONS
[0001] This application is a Non-Provisional Patent Application. The complete technical implementation, empirical benchmarks, and architectural designs disclosed herein were developed in connection with the ModelVM cognitive runtime architecture.

---

## STATEMENT REGARDING FEDERALLY SPONSORED RESEARCH OR DEVELOPMENT
[0002] Not Applicable.

---

## FIELD OF THE INVENTION
[0003] The present invention relates generally to computer systems, operating system architectures, and deep learning execution runtimes. More particularly, the present invention relates to systems, methods, and non-transitory computer-readable media for managing memory residency of heterogeneous machine learning models, scheduling modular specialist execution over physical interconnect buses under strict physical memory budgets, and structurally virtualizing semantic task state across disparate neural network architectures having incompatible tokenizers and hidden-state dimensions.

---

## BACKGROUND OF THE INVENTION
[0004] **1. The Memory Capacity Wall in Multi-Specialist Inference:**
Modern open-weight Large Language Models (LLMs) have demonstrated pronounced domain specialization. Specialized neural networksâ€”such as dedicated mathematical derivation models, algorithmic program synthesis models, scientific literature extraction models, and physical dynamics modelsâ€”consistently surpass dense, monolithic generalist models within their respective domains. For multi-step, multi-disciplinary computational tasks (e.g., extracting equations from scientific text, deriving closed-form solutions, implementing numerical solvers, and verifying physical boundaries), deploying an ensemble of specialized models produces reasoning deliverables that substantially outperform any single compact generalist.

[0005] However, deploying a catalog of specialized models on local consumer workstations, developer laptops, and edge devices is physically constrained by memory hardware. A catalog of ten specialized 7-billion (7B) to 14-billion (14B) parameter models requires between 50 to 65 Gigabytes (GB) of physical memory across quantized and floating-point formats. In contrast, commodity client computing systems are constrained by physical memory budgets of 8.0 to 16.0 GB of Random Access Memory (RAM) or Video RAM (VRAM). When a runtime attempts to load multiple specialists into memory concurrently without global coordination, memory allocations immediately breach physical capacity, causing operating system Out-Of-Memory (OOM) fatal process termination.

[0006] **2. Deficiencies of Retrospective Memory Management (LRU Caching):**
Conventional caching systems and virtual memory managers rely on retrospective, backward-looking eviction heuristics, such as Least Recently Used (LRU) or Least Frequently Used (LFU) replacement. When applied to multi-gigabyte neural network parameter weights operating over cyclic workflows (e.g., alternating between mathematical derivation, code generation, and numerical verification), retrospective heuristics trigger severe input/output (I/O) bus thrashing. The memory manager evicts mathematical specialist weights over the PCIe bus to make room for coding specialist weights, only to be forced to immediately reload the mathematical specialist weights from secondary storage on the subsequent step. This results in idle bus stalls that overwhelm actual compute throughput ($t_{\text{paging}} \gg t_{\text{compute}}$).

[0007] **3. Deficiencies of Unstructured Conversational State Handoffs:**
When transitioning task execution across disparate specialist models, conventional multi-agent frameworks concatenate natural language chat histories into prompt prefixes. This mechanism suffers from three acute failure modes:
- **Accumulating Context Bloat:** Prompt token length expands monotonically ($L_{\text{ctx}} = \mathcal{O}(t \cdot \bar{L}_{\text{gen}})$). When forced into bounded model context windows, first-in, first-out (FIFO) truncation discards foundational domain constraints.
- **Compounding Arithmetic Drift:** Conversational text lacks structural typing. Numerical constants and mathematical equations repeatedly paraphrased through narrative prose degrade across model boundaries, culminating in floating-point hallucinations.
- **Latent Incommensurability:** Because independently trained models utilize incompatible tokenizer vocabularies, rotary position embeddings, and internal hidden-state activation dimensions, internal Key-Value (KV) cache tensors or activation vectors cannot be transferred across model boundaries without prohibitive quadratic calibration bridges.

[0008] **4. Deficiencies of Prior Serving Paradigms:**
High-throughput serving systems (such as vLLM or SGLang) optimize KV-cache allocation for a *single permanently resident model* serving concurrent user queries, but do not manage physical weight residency across multi-model catalogs. Conversely, weight-offloading engines (such as FlexGen or PowerInfer) stream layer-by-layer tensor blocks for a *single static model DAG*, incurring severe per-token PCIe streaming latency without enabling multi-model capability switching.

[0009] Consequently, there exists a critical technological need for systems and methods that treat heterogeneous neural networks as pageable computational resources under hard hardware memory budgets, orchestrating predictive weight residency over physical interconnect buses while preserving semantic task state across model boundaries through a typed, verified intermediate representation.

---

## SUMMARY OF THE INVENTION
[0010] To overcome the aforementioned deficiencies in the art, the present disclosure provides systems, methods, and non-transitory computer-readable media embodying a user-space **Cognitive Systems Runtime** (designated herein as "ModelVM"). ModelVM virtualizes semantic task state and model parameter weight residency, enabling a constrained physical memory envelope (e.g., nominal 8.0 GB) to orchestrate an expansive catalog (e.g., 50+ GB) of heterogeneous open-weight specialists without Out-Of-Memory (OOM) aborts, bus thrashing, or conversational arithmetic degradation.

[0011] In a first principal aspect of the invention, there is provided a **Predictive Cognitive Working Set ($W(t, k)$)** management system. Rather than relying on retrospective eviction history, the system inspects an explicit multi-stage procedural task execution Directed Acyclic Graph (DAG) produced by a task decomposer. For a current stage $t$, the system computes an upcoming demand window over a lookahead horizon $k \in \mathbb{N}^+$. Models identified within the future working set receive an **Eviction Shielding Multiplier**, increasing their displacement cost and preferentially protecting them from premature removal from memory. Furthermore, whenever verified memory headroom exists satisfying a safety margin invariant ($\text{RAM}_{\text{free}} - \text{RAM}_{\text{req}}(m_{\text{next}}) \ge \Delta_{\text{margin}}$), the system proactively pre-stages or pre-fetches upcoming model weights across a physical interconnect bus (e.g., PCIe 4.0/5.0) into spare memory buffers, hiding cold-load stalls.

[0012] In a second principal aspect of the invention, there is provided a **Cognitive State Protocol (CSP)** intermediate representation. CSP virtualizes task state across disparate model architectures using a strongly typed 9-tuple state carrier:
$$\mathcal{S}_t = \langle \mathcal{G}, \mathcal{F}_t, \mathcal{C}_t, \mathcal{E}_t, \mathcal{A}_t, \mathcal{U}_t, \mathcal{D}_t, \mathcal{Q}_t, \mathcal{O}_t \rangle$$
comprising explicit fields for global task goal ($\mathcal{G}$), cumulative verified facts ($\mathcal{F}_t$), mathematical calculations ($\mathcal{C}_t$), empirical evidence citations ($\mathcal{E}_t$), explicit modeling assumptions ($\mathcal{A}_t$), active epistemic uncertainties ($\mathcal{U}_t$), committed architectural decisions ($\mathcal{D}_t$), unresolved open questions ($\mathcal{Q}_t$), and concrete deliverables or artifacts ($\mathcal{O}_t$), supported by an auxiliary execution history trace ($\mathcal{H}_t$). All mathematical calculations are passed through a deterministic Abstract Syntax Tree (AST) arithmetic verifier prior to state absorption, mitigating numerical drift and eliminating conversational token bloat.

[0013] In a third principal aspect of the invention, there is provided a **Multi-Objective Cognitive Scheduler**. For each execution stage, candidate models are evaluated via an explainable, joint utility scoring function balancing empirical capability fitness ($F_{\text{cap}}$), active memory footprint ($M_{\text{cost}}$), bus load latency ($L_{\text{load}}$), energy consumption ($E_{\text{energy}}$), eviction displacement costs of resident models ($E_{\text{evict}}$), and downstream stage reuse distance ($F_{\text{future}}$):
$$\text{Score}(m, C) = F_{\text{cap}}(m, C) - \alpha M_{\text{cost}}(m) - \beta L_{\text{load}}(m) - \gamma E_{\text{energy}}(m) - \delta E_{\text{evict}}(m) + \eta F_{\text{future}}(m)$$
Candidate models are objectively scored using pre-registered capability profiles established across held-out standardized probes, eliminating subjective manual scoring and achieving bounded regret ($\le 0.3\%$) relative to an exact finite-state Dynamic Programming offline oracle.

---

## BRIEF DESCRIPTION OF THE DRAWINGS
[0014] **FIG. 1** is a high-level architectural block diagram illustrating the ModelVM runtime subsystems, including the Cognitive Kernel, Working Set Predictor, Cognitive Scheduler, Model Pager, and the two-tier memory hierarchy.

[0015] **FIG. 2** is a schematic diagram illustrating the Cognitive State Protocol (CSP) 9-tuple schema, the state merge model with conflict resolution, and the AST arithmetic verification engine.

[0016] **FIG. 3** is a control-flow diagram illustrating the Multi-Objective Scheduler selection pipeline, eviction shielding, and opportunistic prefetching / pre-staging.

[0017] **FIG. 4** is a hardware interconnect diagram showing dataflow pathways between NVMe secondary storage, Host CPU DDR5 RAM, and GPU Accelerator GDDR7 VRAM across a physical PCIe bus.

[0018] **FIG. 5** is an empirical performance chart illustrating the Pareto optimization frontier and orthogonal factorial ablation decomposition of the runtime.

---

## DETAILED DESCRIPTION OF THE PREFERRED EMBODIMENTS
[0019] Referring now to the drawings in detail, exemplary embodiments of the present invention are described. While specific configurations, parameters, and algorithms are disclosed, it will be understood that these are provided for illustrative purposes and do not limit the scope of the claimed invention.

### 1. System Architecture & Two-Tier Memory Accounting
[0020] As shown in **FIG. 1**, the runtime comprises a **Cognitive Kernel (102)** running in user space on a host operating system. In an exemplary embodiment, the host computing system includes a host central processing unit (CPU), a physical primary host memory (RAM, e.g., 64 GB DDR5), a secondary non-volatile storage (e.g., NVMe SSD, 1 TB), and an accelerator device (GPU, e.g., NVIDIA GeForce RTX 5070 Ti with 16 GB GDDR7 VRAM) connected via a physical high-speed serial bus (e.g., PCIe 4.0/5.0 x16).

[0021] **Decoupled Two-Tier Memory Accounting:** The runtime explicitly decouples host memory allocations from accelerator memory allocations, establishing distinct capacity envelopes:
- $\mathcal{B}_{\text{host}}$: Enforced budget for host CPU RAM (nominally 8.0 GB for model weight caching, tokenizer buffers, runtime context, and secondary staging buffers).
- $\mathcal{B}_{\text{device}}$: Enforced budget for accelerator device VRAM.
- $M_{\text{active}}(t)$: Instantaneous active memory allocation, computed as:
  $$M_{\text{active}}(t) = M_{\text{weights}}(t) + M_{\text{workspace}}(t) + M_{\text{KV}}(t) + M_{\text{runtime}}(t)$$
where $M_{\text{weights}}(t)$ represents pinned model parameters, $M_{\text{workspace}}(t)$ denotes scratchpad execution buffers, $M_{\text{KV}}(t)$ denotes dynamic key-value attention cache, and $M_{\text{runtime}}(t)$ accounts for OS/driver allocator overhead.

[0022] At any instant $t$, the set of models resident in active memory $\mathcal{R}_t \subset \mathcal{M}$ satisfies the strict admission invariants:
$$\sum_{m \in \mathcal{R}_{\text{device}}(t)} M_{\text{weights}}(m) + M_{\text{workspace}}(t) + M_{\text{KV}}(t) \le \mathcal{B}_{\text{device}}$$
$$\sum_{m \in \mathcal{R}_{\text{host}}(t)} M_{\text{host}}(m) + M_{\text{context}}(t) + M_{\text{runtime}}(t) \le \mathcal{B}_{\text{host}}$$
Memory residency is actively managed through user-space admission control and memory reservation tokens, preventing runtime memory requests from exceeding physical capacity.

### 2. Predictive Working-Set Memory Management ($W(s_t, k)$)
[0023] When a computational task goal is received, the Kernel invokes a Task Decomposer to parse the task into an execution Directed Acyclic Graph (DAG) of $N$ dependent capability stages $G = (V, E)$, where vertices $V = \{s_0, s_1, \dots, s_{N-1}\}$ represent capability stages and edges $E$ represent data and dependency handoffs. For linear workflows, $G$ is a topological sequence; for non-linear workflows, $G$ contains branching and join nodes.

[0024] **Working Set Formulation:** For a currently executing stage $s_t$, the **Working Set Predictor (104)** defines the forward lookahead working set $W(s_t, k)$ over horizon $k \in \mathbb{N}^+$ (nominally $k=3$) as the set of capabilities demanded by all reachable nodes within topological path distance $k$:
$$W(s_t, k) = \{ C(s_j) \mid s_j \in \text{Reachable}(s_t), \; 1 \le \text{dist}(s_t, s_j) \le k \}$$
For each candidate future stage $s_j$, the demand probability is modeled via an execution probability function:
$$P(\text{demand}, s_j) = P_{\text{branch}}(s_t \to s_j) \cdot \max\left(P_{\text{floor}}, \; 1.0 - \zeta \cdot \text{dist}(s_t, s_j)\right)$$
where $P_{\text{branch}}$ represents branch execution probability (1.0 for deterministic sequences), $\zeta$ is a distance decay parameter (nominally 0.20), and $P_{\text{floor}}$ is a minimum demand floor (nominally 0.10).

[0025] **Displacement Cost & Eviction Policy:** When an incoming model $m_{\text{in}}$ requires memory allocation exceeding available free capacity $\text{RAM}_{\text{free}}$, the **Model Pager (106)** identifies one or more victim models from the resident set $\mathcal{R}_t$. The eviction displacement cost $\text{Cost}_{\text{disp}}(m)$ for resident model $m \in \mathcal{R}_t$ quantifies the penalty incurred by evicting model $m$:
$$\text{Cost}_{\text{disp}}(m) = \left[ L_{\text{reload}}(m) \cdot P(\text{reuse}, m) + \text{Cost}_{\text{recompute}}(m) \right] \cdot \sigma_{\text{shield}}(m)$$
where $L_{\text{reload}}(m)$ is the estimated PCIe reload latency for model $m$, $P(\text{reuse}, m) = \max_{s_j \in W(s_t, k)} P(\text{demand}, s_j) \cdot F_{\text{cap}}(m, C(s_j))$ represents future reuse probability, and $\sigma_{\text{shield}}(m)$ is an eviction shielding multiplier defined as:
$$\sigma_{\text{shield}}(m) = \begin{cases} 
\mu_{\text{shield}} & \text{if } m \text{ satisfies a capability in } W(s_t, k) \\ 
1.0 & \text{otherwise} 
\end{cases}$$
wherein $\mu_{\text{shield}} \ge 1.5$ (nominally $\mu_{\text{shield}} = 1.80$).

[0026] **Victim Selection Algorithm:** The Model Pager selects a minimal subset of candidate victim models $\mathcal{V} \subset \mathcal{R}_t \setminus \{m_{\text{active}}\}$ that satisfies the memory reclamation requirement:
$$\sum_{v \in \mathcal{V}} \text{RAM}_{\text{reclaim}}(v) \ge \text{RAM}_{\text{req}}(m_{\text{in}}) - \text{RAM}_{\text{free}}$$
while minimizing the total displacement cost $\sum_{v \in \mathcal{V}} \text{Cost}_{\text{disp}}(v)$. If all resident models are shielded, the victim with the lowest displacement cost is evicted, ensuring that execution never deadlocks.

[0027] **Prefetch and Pre-Staging Execution Embodiments:** The Model Pager continually evaluates upcoming models in $W(s_t, k)$ against two admission invariants:
1. **Safety Headroom Invariant:**
   $$\text{RAM}_{\text{free}} - \text{RAM}_{\text{req}}(m_{\text{next}}) \ge \Delta_{\text{margin}}$$
   where $\Delta_{\text{margin}}$ is an immutable safety buffer (nominally $1.0\,\text{GB}$) reserved for activation spikes and runtime overhead.
2. **Positive Prefetch Utility:**
   $$U_{\text{prefetch}}(m) = P(\text{demand}, m) \cdot L_{\text{load}}(m) - \lambda \cdot M_{\text{cost}}(m) - \mu \cdot E_{\text{cost}}(m) > 0$$
   where $\lambda$ and $\mu$ represent dimensional scaling weights.

The runtime supports two pre-loading execution modes:
- **Synchronous Pre-Staging:** When stage $t$ completes and headroom condition (1) is satisfied, model $m_{\text{next}}$ is paged into available memory prior to dispatching stage $t+1$, eliminating cold-load latency on stage $t+1$ without concurrent I/O interference.
- **Concurrent Double-Buffered Prefetching:** In an asynchronous embodiment, a dedicated background I/O thread pool initiates direct memory access (DMA) streaming of $m_{\text{next}}$ parameter weights across the physical interconnect bus while stage $t$ executes on accelerator tensor cores. An atomic reservation token is allocated in memory prior to initiation. If active inference memory consumption breaches a dynamic headroom threshold during the transfer, an abort signal terminates background streaming and rolls back the reservation token, preventing memory contention.

### 3. Cognitive State Protocol (CSP) & Verification Engine
[0028] State transitions across heterogeneous models are mediated through the strongly typed 9-tuple $\mathcal{S}_t$:
$$\mathcal{S}_t = \langle \mathcal{G}, \mathcal{F}_t, \mathcal{C}_t, \mathcal{E}_t, \mathcal{A}_t, \mathcal{U}_t, \mathcal{D}_t, \mathcal{Q}_t, \mathcal{O}_t \rangle$$
accompanied by auxiliary execution history $\mathcal{H}_t = [h_0, h_1, \dots, h_{t-1}]$. Table 1 specifies the semantic role of each constituent.

| Symbol | Field Name | Type | Semantic Definition & Systems Role |
| :--- | :--- | :--- | :--- |
| $\mathcal{G}$ | `goal` | `str` | Immutable top-level user objective; anchors all stage prompts. |
| $\mathcal{F}_t$ | `facts` | `List[str]` | Deduplicated set of verified factual assertions accumulated over stages. |
| $\mathcal{C}_t$ | `calculations` | `List[CalcRecord]` | Structured arithmetic and symbolic records with independent AST verification status. |
| $\mathcal{E}_t$ | `evidence` | `List[EvidRecord]` | Empirical claims paired with provenance source and diversity-discounted confidence. |
| $\mathcal{A}_t$ | `assumptions` | `List[str]` | Explicit modeling assumptions introduced by specialist models. |
| $\mathcal{U}_t$ | `uncertainties` | `List[str]` | Active epistemic risks, low-confidence derivations, or boundary ambiguities. |
| $\mathcal{D}_t$ | `decisions` | `List[str]` | Architectural and design decisions committed during execution. |
| $\mathcal{Q}_t$ | `open_questions` | `List[str]` | Unresolved domain questions targeted for subsequent stages. |
| $\mathcal{O}_t$ | `artifacts` | `Dict[str, Any]` | Versioned store of concrete deliverables (scripts, datasets, plots). |
| $\mathcal{H}_t$ | `history_trace` | `List[StageTrace]` | Immutable chronological audit trail of stage durations, models, and actions. |

[0029] **AST Arithmetic Verification Grammar:** To mitigate mathematical hallucinations without unbounded execution risk, any mathematical calculation item $c \in \mathcal{C}$ declaring an expression $E$ and claimed result $R$ is parsed into an Abstract Syntax Tree (AST) governed by a restricted formal grammar. The grammar restricts allowable operations to:
- Binary operators: Addition ($+$), Subtraction ($-$), Multiplication ($*$), Division ($/$), Floor Division ($//$), Modulo ($\%$), Exponentiation ($**$).
- Unary operators: Positive ($+$), Negation ($-$).
- Mathematical functions: $\text{sqrt}(\cdot)$, $\exp(\cdot)$, $\log(\cdot)$, $\log_{10}(\cdot)$, $\sin(\cdot)$, $\cos(\cdot)$, $\tan(\cdot)$, $\text{abs}(\cdot)$.
- Mathematical constants: $\pi$, $e$.
Arbitrary code execution, dynamic imports, operating system calls, and external variable references are strictly blocked by the AST parser.

[0030] The AST evaluator computes exact numerical evaluation $V = \text{eval}(E)$ and validates arithmetic consistency with claimed result $R$ using an adaptive absolute/relative error tolerance rule:
$$|V - R| \le \max\left(\epsilon_{\text{abs}}, \; |R| \cdot \epsilon_{\text{rel}}\right)$$
wherein nominal values are $\epsilon_{\text{abs}} = 10^{-4}$ (preventing division-by-zero anomalies near the origin) and $\epsilon_{\text{rel}} = 10^{-3}$ (0.1% relative tolerance). If verification succeeds, the item is stamped `verified=True` and assigned verification provenance (`verification_method = 'arithmetic'`). If verification fails, the item is marked `verified=False` and routed to the uncertainty set $\mathcal{U}_t$. The verification establishes deterministic syntactic arithmetic correctness of declared expressions, while domain scientific validity remains governed by model capability.

[0031] **Deterministic State Conflict Resolution & Provenance:** Rather than lossy conversational concatenation, state updates follow an explicit conflict resolution model:
- **Fact and Evidence Updates:** Each evidence item $e \in \mathcal{E}$ contains $\langle \text{claim}, \text{source}, \text{confidence}, \text{model\_id}, \text{timestamp} \rangle$. When an incoming claim matches an existing claim from an identical or overlapping model source, no confidence amplification is applied ($c_{\text{new}} = \max(c_1, c_2)$) to prevent circular self-reinforcement. When corroborated across distinct, heterogeneous model architectures, confidence is aggregated via a diversity-discounted combination rule:
  $$c_{\text{new}} = \min\left(0.99, \; \max\left(c_1, c_2, \; 1.0 - (1.0 - c_1)(1.0 - c_2)^{w_{\text{diversity}}}\right)\right)$$
  wherein $w_{\text{diversity}} \in (0, 1)$ (nominally $w_{\text{diversity}} = 0.65$) penalizes correlated priors across foundational language models while rewarding verified multi-model cross-validation.
- **Calculation Updates:** Calculations with identical mathematical expressions are evaluated via AST. If an incoming calculation is verified while an existing record is unverified, the existing entry is upgraded to verified status and its result updated.
- **Artifact Versioning & Conflict Isolation:** If an incoming artifact declares a key matching an existing artifact with divergent content, the runtime creates a versioned key ($\text{key\_v}N$) and flags an explicit conflict marker ($\text{key\_CONFLICT}$), preserving both deliverables for downstream resolution rather than overwriting prior deliverables.
- **Immutable Audit Trail:** The history field $\mathcal{H}_t$ is strictly append-only, storing the complete provenance log of all accepted, upgraded, and versioned state updates.

### 4. Multi-Objective Cognitive Scheduling
[0032] Candidate models are scored for capability $C$ at stage $t$ via the multi-objective utility formula:
$$\text{Score}(m, C) = F_{\text{cap}}(m, C) - \alpha M_{\text{cost}}(m) - \beta L_{\text{load}}(m) - \gamma E_{\text{energy}}(m) - \delta E_{\text{evict}}(m) + \eta F_{\text{future}}(m)$$
where:
- $F_{\text{cap}}(m, C) \in [0, 1]$ is obtained from an empirical capability matrix $\mathbf{P}$ established via offline benchmark probes;
- $M_{\text{cost}}(m) = \text{RAM}_{\text{req}}(m) / \mathcal{B}_{\text{RAM}}$ is normalized memory cost;
- $L_{\text{load}}(m) = 0.0$ if model $m$ is resident, else normalized cold transfer time over the physical bus;
- $E_{\text{energy}}(m) = (\min(1.0, \text{params}/32.0)) \cdot \text{factor}$ is normalized energy consumption;
- $E_{\text{evict}}(m) = \sum_{v \in \mathcal{V}} \text{Cost}_{\text{disp}}(v)$ is the normalized displacement penalty of models required to be evicted to admit model $m$, including shielding multiplier $\mu_{\text{shield}} = 1.8$;
- $F_{\text{future}}(m) = \sum_{s_j \in W(s_t, k)} P(\text{demand}, s_j) \cdot F_{\text{cap}}(m, C(s_j))$ rewards models with downstream stage utility.
Nominal parameter weights are $\alpha = 0.20, \beta = 0.25, \gamma = 0.10, \delta = 0.30, \eta = 0.35$.

---
