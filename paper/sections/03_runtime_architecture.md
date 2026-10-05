# Section 3: ModelVM Architecture & Runtime Abstraction

Executing complex multi-disciplinary language model workloads on resource-constrained consumer hardware requires resolving a core contradiction: domain-specialized open-weight models deliver superior accuracy on targeted technical tasks compared to monolithic generalists, but their collective memory footprint ($M_{\text{active,total}} = 52.7\,\text{GB}$) far exceeds commodity memory envelopes ($\mathcal{B}_{\text{RAM}} = 8.0\,\text{GB}$). To resolve this bottleneck without sacrificing specialization or state integrity, ModelVM introduces an operating-system-inspired runtime architecture.

In this section, we present the structural foundations of ModelVM. We first de-center the operating system metaphor, establishing the precise theoretical and practical boundaries between classical virtual memory and cognitive runtime virtualization. We then detail the architectural flow and subsystem coordination governing the Cognitive Kernel, Model Pager, and Cognitive Scheduler. Finally, we formulate the residency state and provide an inductive proof of the runtime memory invariant, characterizing its relationship to physical host and accelerator memory headroom.

---

## 3.1 De-centering the OS Metaphor

The conceptual lineage of ModelVM traces directly to Peter Denning's foundational work on virtual memory and working-set dynamics. In early mainframe computing, programmers encountered a physical constraint analogous to today's LLM deployment barrier: individual software systems required more primary magnetic core memory than was physically installed. Classical virtual memory resolved this disparity by decoupling the logical address space referenced by software processes from the physical page frames provided by hardware, transparently swapping unreferenced pages to secondary disk storage.

While this paradigm inspires our design, we explicitly decouple ModelVM from literal kernel-level mechanisms to avoid false equivalence. Table 1 formalizes the conceptual correspondence while delineating critical systems differences.

### Table 1: System Mapping: Classical Operating System Virtual Memory vs. ModelVM Runtime Abstraction

| Systems Dimension | Classical OS Virtual Memory | ModelVM Runtime Abstraction | Architectural Distinction |
| :--- | :--- | :--- | :--- |
| **Execution Unit** | Operating System Process | Domain Capability Stage ($s_t$) | Coarse procedural step vs. machine instruction stream |
| **Execution Engine** | Physical Hardware CPU / Core | Heterogeneous Specialist Model ($M_t$) | Neural network parameter logic executing on host/device |
| **State Abstraction** | Process Control Block (PCB) & Virtual Address Space | Cognitive State Packet ($\mathcal{S}_t$) | Structured typed 9-tuple semantic carrier vs. raw uninterpreted bytes |
| **Memory Allocation** | Fixed-size Page Frames (4 KB / 2 MB) | Model Weight Parameter Allocations ($\text{RAM}_{\text{req}}(m)$) | Multi-gigabyte tensor buffers vs. uniform hardware page frames |
| **Primary Memory** | Physical Host RAM | Active Execution Budget ($\mathcal{B}_{\text{RAM}} = 8.0\,\text{GB}$) | User-space configured quota vs. physical silicon capacity |
| **Backing Store** | Secondary Disk / Swap Partition | Serialized Model Catalog on NVMe ($\mathcal{B}_{\text{disk}} = 64.0\,\text{GB}$) | Structured parameter safetensors / GGUF vs. raw swap blocks |
| **Fault Mechanism** | Hardware Page Fault (MMU Interrupt) | Model Cache Miss (Runtime Interception) | Software-level stage routing vs. ring-0 exception handler |
| **Residency Tracking** | Inverted Page Table / TLB | Resident Model Tracking Table ($\mathcal{R}_t$) | Object registry with access timestamps vs. hardware translation tables |
| **Working Set** | Past-window Page Frequency $W(t, \Delta)$ | Predictive Working Set $W(t, k)$ | Forward-looking task DAG lookahead vs. backward-looking sliding window |
| **Context Switch** | Register save/restore + address space swap | Typed CSP Handoff across Model Boundaries | Architecture-agnostic state merge vs. hardware thread context dump |

### Scope Boundaries and What ModelVM Is Not
To ensure scientific clarity, we define three explicit boundaries governing our abstraction:
1. **Language Models are Processes, Not CPUs:** In classical systems, the CPU is the physical executor, while processes represent scheduled programs. In ModelVM, the physical host CPU and GPU accelerator remain the execution hardware. An open-weight language model is a specialized computational process containing frozen parameter weights that executes a cognitive transformation stage. ModelVM treats the model itself as the pageable computational resource.
2. **User-Space Runtime, Not Ring-0 Kernel:** ModelVM does not modify kernel-level memory management units (MMUs), modify OS page tables, or install custom device drivers. It is a user-space systems runtime and execution middleware that coordinates weight streaming, inference dispatch, and state tracking.
3. **Semantic State vs. Byte Buffers:** Classical operating systems are semantically agnostic; a page frame contains uninterpreted binary data. In contrast, language model handoffs require semantic state preservation. Swapping model weights alone is insufficient if the intermediate reasoning state is corrupted. ModelVM couples physical weight residency management with semantic state virtualization, ensuring that state transitions across heterogeneous architectures remain losslessly grounded.

---

## 3.2 Architectural Flow & Subsystem Coordination

The ModelVM architecture is organized into three tightly coupled subsystems coordinated by a centralized supervisory control path: the **Cognitive Kernel**, the **Model Pager**, and the **Cognitive Scheduler**.

```text
+===================================================================================================+
|                                    COGNITIVE KERNEL (Supervisor)                                  |
|                                                                                                   |
|   +-----------------------+     +--------------------------+     +----------------------------+   |
|   |   Task Decomposer     | --> | Stage Plan: S = [s_0..N] | --> | State Carrier: S_t (CSP)   |   |
|   +-----------------------+     +--------------------------+     +----------------------------+   |
+=============================================|==================================^==================+
                                              | Stage s_t                        | Verified Merge
                                              v                                  | \Delta S_t^*
+================================================================================|==================+
|                        PREDICTIVE COGNITIVE SCHEDULER & WORKING SET            |                  |
|                                                                                |                  |
|   +------------------------------------+     +---------------------------------+--------------+   |
|   |  CognitiveWorkingSetPredictor      |     |  Multi-Objective CognitiveScheduler            |   |
|   |  - Forecasts W(t, k) demand        | --> |  - Capability Profiling Matrix P               |   |
|   |  - Computes prefetch candidate     |     |  - Joint Utility: Score(m)                     |   |
|   +------------------------------------+     +---------------------------------+--------------+   |
+================================================================|==================================+
                                                                 | Selected Model M_t
                                                                 v
+===================================================================================================+
|                                     MODEL PAGER (Memory Manager)                                  |
|                                                                                                   |
|   Enforces: \sum_{m \in R_t} RAM_req(m) <= B_RAM (8.0 GB)       Headroom Buffer >= 1.0 GB         |
|   Resident Set R_t Tracking                                     Cost-Aware Shielded Eviction      |
|                                                                                                   |
|         +-----------------------+                    +------------------------------------+       |
|         | Cache Hit (Resident)  |                    | Cache Miss (Evict & Stream Load)   |       |
|         +-----------+-----------+                    +-----------------+------------------+       |
|                     |                                                  |                          |
+=====================|==================================================|==========================+
                      | Weight Ptrs Ready                                | NVMe Bus Transfer
                      v                                                  v
+===================================================================================================+
|                                      EXECUTION BACKEND & TELEMETRY                                |
|                                                                                                   |
|   +------------------------------------+             +----------------------------------------+   |
|   |  Inference Backend (Host/CUDA)     |             |  Hardware Telemetry Instrumentation    |   |
|   |  - Generates \mathbf{y}_t          |             |  - Host RSS (/proc/statm)              |   |
|   |  - Extracts raw delta \Delta S_t   |             |  - GPU VRAM Breakdown (NVML)           |   |
|   +-----------------+------------------+             +----------------------------------------+   |
|                     |                                                                             |
|                     v                                                                             |
|   +------------------------------------+                                                          |
|   |  Independent AST Verifier          |                                                          |
|   |  - Validates arithmetic calcs      | ---------------------------------------------------------+
|   |  - Emits certified \Delta S_t^*    |
|   +------------------------------------+
+===================================================================================================+
```

### 1. The Cognitive Kernel (`CognitiveKernel`)
The Cognitive Kernel serves as the supervisory coordinator of the runtime:
- **Procedural Decomposition:** Given a high-level task goal $G \in \Sigma^*$, the kernel invokes `TaskDecomposer` to produce an ordered sequence of $N$ dependent capability stages $S = [s_0, s_1, \dots, s_{N-1}]$, where each stage $s_t$ defines capability requirement $C(s_t) \in \mathcal{C}$ and domain instruction $\tau_t$.
- **State Virtualization Lifecycle:** The kernel instantiates the root state carrier $\mathcal{S}_0 = \langle G, \emptyset, \emptyset, \emptyset, \emptyset, \emptyset, \emptyset, \emptyset, \emptyset \rangle$ and threads it across stage boundaries. At each transition, the kernel merges validated updates $\Delta \mathcal{S}_t^*$ into $\mathcal{S}_{t+1}$.
- **Confidence Assessment & Bounded Escalation:** Upon stage completion, the kernel queries `ConfidenceController`. If uncertainty exceeds tolerance, the kernel initiates a bounded escalation loop, dynamically scheduling a higher-capability specialist under loop termination constraints ($\le 2$ escalations per stage, capability delta $\ge \epsilon = 0.02$).

### 2. The Model Pager (`ModelPager`)
The Model Pager manages the physical memory footprint of candidate models under budget $\mathcal{B}_{\text{RAM}}$:
- **Residency Management:** The pager maintains the resident model set $\mathcal{R}_t \subset \mathcal{M}$ and tracks access timestamps, access frequencies, and lifecycle states (`DISK`, `RESIDENT`, `PINNED`).
- **Cost-Aware Eviction with Shielding:** When admitting an incoming model requires freeing memory, the pager invokes `CostAwareEvictionPolicy`. Models identified in the forward working set $W(t, k)$ receive an eviction penalty multiplier ($\delta \times 1.8$), shielding imminent specialists from premature eviction.
- **Opportunistic Headroom Prefetching:** If the forward working set identifies an imminent model whose prefetch utility $U_{\text{prefetch}} > 0$, and active memory maintains a tested safety margin $(\text{RAM}_{\text{free}} - \text{RAM}_{\text{req}}(m) \ge 1.0\,\text{GB})$, the pager opportunistically stages model weights into memory ahead of stage invocation without evicting resident models.

### 3. The Cognitive Scheduler (`CognitiveScheduler`)
The Cognitive Scheduler performs multi-objective model selection for each execution stage $s_t$:
- **Empirical Capability Fitness:** Candidate models are evaluated against empirical capability matrix $\mathbf{P} \in [0, 1]^{K \times |\mathcal{C}|}$, established via offline benchmark probes (`ModelProfiler`) across 7 foundational domains, eliminating subjective manual scoring.
- **Joint Utility Optimization:** The scheduler scores candidate models by jointly balancing capability fitness against memory cost, cold-load transfer latency, energy factor, eviction penalty, and future stage reuse:
  $$\text{Score}(m) = F_{\text{cap}}(m, C) - \alpha M_{\text{cost}}(m) - \beta L_{\text{load}}(m) - \gamma E_{\text{energy}}(m) - \delta E_{\text{eviction}}(m) + \eta F_{\text{future}}(m)$$
  subject to hard admission constraint $\text{RAM}_{\text{req}}(m) \le \mathcal{B}_{\text{RAM}}$.
- **Lookahead Integration:** The future utility term $F_{\text{future}}(m)$ is dynamically populated by querying `CognitiveWorkingSetPredictor`, rewarding models that satisfy upcoming pipeline stages and penalizing candidates that provoke downstream thrashing.

---

## 3.3 The Formal Memory Invariant

Deterministic execution on resource-constrained hardware requires mathematical guarantees against memory exhaustion. We now formulate the residency state and prove that ModelVM strictly preserves the configured runtime memory invariant under all execution trajectories.

### Residency State Space
Let $\mathcal{M} = \{m_1, \dots, m_K\}$ denote the full catalog of $K$ available models, where each model $m \in \mathcal{M}$ is characterized by a static parameter RAM requirement $\text{RAM}_{\text{req}}(m) > 0$. At any discrete stage transition $t \in \{0, \dots, N\}$, the memory state of the runtime is completely defined by the resident set:
$$\mathcal{R}_t \subseteq \mathcal{M}$$
The total active parameter memory occupied by the runtime at stage $t$ is:
$$M_{\text{active}}(t) = \sum_{m \in \mathcal{R}_t} \text{RAM}_{\text{req}}(m)$$
and available free parameter memory is:
$$\text{RAM}_{\text{free}}(t) = \max\left(0.0, \;\mathcal{B}_{\text{RAM}} - M_{\text{active}}(t)\right)$$

### Theorem 1 (Configured Headroom Admission Invariant)
Let $\mathcal{B}_{\text{RAM}} > 0$ denote the configured active memory budget. If the initial state satisfies $M_{\text{active}}(0) \le \mathcal{B}_{\text{RAM}}$, and if every individual candidate model satisfies $\text{RAM}_{\text{req}}(m) \le \mathcal{B}_{\text{RAM}}$, then under the ModelVM paging protocol, the active memory footprint satisfies:
$$\sum_{m \in \mathcal{R}_t} \text{RAM}_{\text{req}}(m) \le \mathcal{B}_{\text{RAM}}, \qquad \forall t \ge 0$$

#### Proof:
We prove Theorem 1 by structural induction over discrete runtime transitions $t \to t+1$.

**Base Case ($t=0$):** At runtime initialization, the resident set is either empty ($\mathcal{R}_0 = \emptyset$), yielding $M_{\text{active}}(0) = 0 \le \mathcal{B}_{\text{RAM}}$, or pre-populated with a single designated model $m_0$ satisfying $\text{RAM}_{\text{req}}(m_0) \le \mathcal{B}_{\text{RAM}}$. In either case, the invariant holds at $t=0$.

**Inductive Hypothesis:** Assume that at stage $t$, the invariant holds:
$$M_{\text{active}}(t) = \sum_{m \in \mathcal{R}_t} \text{RAM}_{\text{req}}(m) \le \mathcal{B}_{\text{RAM}}$$

**Inductive Step ($t \to t+1$):** Let stage $s_t$ require execution on model $M_{t+1} \in \mathcal{M}$. The runtime encounters one of three mutually exclusive operational cases:

1. **Case 1: Cache Hit ($M_{t+1} \in \mathcal{R}_t$).** Model $M_{t+1}$ is already resident in active memory. The pager emits a `CACHE_HIT` event (duration $0.0\,\text{s}$) and updates the model's access metadata. The resident set remains unmodified:
   $$\mathcal{R}_{t+1} = \mathcal{R}_t \implies M_{\text{active}}(t+1) = M_{\text{active}}(t) \le \mathcal{B}_{\text{RAM}}$$
   The invariant is preserved.

2. **Case 2: Cache Miss ($M_{t+1} \notin \mathcal{R}_t$).** Model $M_{t+1}$ must be paged in from secondary storage. If $\text{RAM}_{\text{req}}(M_{t+1}) > \mathcal{B}_{\text{RAM}}$, the model exceeds total configured capacity; admission is rejected immediately via an explicit `MemoryError`, preventing execution and leaving $\mathcal{R}_t$ intact.

   If $\text{RAM}_{\text{req}}(M_{t+1}) \le \mathcal{B}_{\text{RAM}}$, the pager evaluates available headroom:
   - **Sufficient Spare Capacity:** If $\text{RAM}_{\text{free}}(t) \ge \text{RAM}_{\text{req}}(M_{t+1})$, no evictions are required. The model is admitted directly into active memory:
     $$\mathcal{R}_{t+1} = \mathcal{R}_t \cup \{M_{t+1}\}$$
     Because $\text{RAM}_{\text{free}}(t) = \mathcal{B}_{\text{RAM}} - M_{\text{active}}(t) \ge \text{RAM}_{\text{req}}(M_{t+1})$, we obtain:
     $$M_{\text{active}}(t+1) = M_{\text{active}}(t) + \text{RAM}_{\text{req}}(M_{t+1}) \le \mathcal{B}_{\text{RAM}}$$
   - **Insufficient Spare Capacity (Eviction Triggered):** If $\text{RAM}_{\text{free}}(t) < \text{RAM}_{\text{req}}(M_{t+1})$, the pager invokes the eviction subsystem $\mathcal{E}$. The eviction routine iteratively selects victim models $\mathcal{V} \subseteq \mathcal{R}_t \setminus \{M_{t+1}\}$ to unload. The loop terminates when:
     $$\sum_{v \in \mathcal{V}} \text{RAM}_{\text{req}}(v) \ge \text{RAM}_{\text{req}}(M_{t+1}) - \text{RAM}_{\text{free}}(t)$$
     Because $\text{RAM}_{\text{req}}(M_{t+1}) \le \mathcal{B}_{\text{RAM}}$, such a victim set $\mathcal{V}$ is guaranteed to exist. Unloading $\mathcal{V}$ produces the intermediate memory state:
     $$M_{\text{active}}' = M_{\text{active}}(t) - \sum_{v \in \mathcal{V}} \text{RAM}_{\text{req}}(v) \le \mathcal{B}_{\text{RAM}} - \text{RAM}_{\text{req}}(M_{t+1})$$
     The incoming model $M_{t+1}$ is then loaded into memory:
     $$\mathcal{R}_{t+1} = (\mathcal{R}_t \setminus \mathcal{V}) \cup \{M_{t+1}\}$$
     yielding:
     $$M_{\text{active}}(t+1) = M_{\text{active}}' + \text{RAM}_{\text{req}}(M_{t+1}) \le \mathcal{B}_{\text{RAM}}$$
   The invariant is preserved across all cache-miss transitions.

3. **Case 3: Opportunistic Prefetch Staging.** Prior to stage execution, the working-set predictor may recommend staging a future candidate $m_{\text{pre}} \notin \mathcal{R}_t$. ModelVM enforces an explicit admission gate: prefetching is admitted if and only if:
   $$U_{\text{prefetch}}(m_{\text{pre}}) > 0 \quad \land \quad \text{RAM}_{\text{free}}(t) - \text{RAM}_{\text{req}}(m_{\text{pre}}) \ge \Delta_{\text{headroom}}$$
   where $\Delta_{\text{headroom}} = 1.0\,\text{GB}$. Upon admission:
   $$M_{\text{active}}(t+1) = M_{\text{active}}(t) + \text{RAM}_{\text{req}}(m_{\text{pre}}) \le \mathcal{B}_{\text{RAM}} - \Delta_{\text{headroom}} < \mathcal{B}_{\text{RAM}}$$
   The invariant is strictly preserved.

By mathematical induction, the invariant holds for all discrete stages $t \ge 0$. $\blacksquare$

### Physical Memory Decomposition & Dynamic Headroom Safety
Theorem 1 guarantees that static parameter tensor allocations never exceed $\mathcal{B}_{\text{RAM}}$. In physical deployment, total memory consumption encompasses dynamic runtime overheads:
$$M_{\text{physical}}(t) = M_{\text{weights}}(t) + M_{\text{workspace}}(t) + M_{\text{KV}}(t) + M_{\text{runtime}}$$
where $M_{\text{weights}}(t) \equiv M_{\text{active}}(t)$, $M_{\text{workspace}}$ represents CUDA execution scratchpads, $M_{\text{runtime}}$ represents process binary overhead ($0.4$--$0.6\,\text{GB}$), and $M_{\text{KV}}(t)$ is the Key-Value attention cache.

To prevent dynamic allocations from breaching physical hardware ceilings, ModelVM implements two protective architectural constraints:
1. **Strict KV-Cache Bounding:** Context lengths are capped at $W_{\text{in}} = 4,096$ input tokens and $T_{\text{gen}} = 1,024$ output tokens under greedy decoding ($T=0.0$). For a 7B-parameter transformer with $L=32$ layers, $H=32$ heads, and key dimension $d_k=128$ in 16-bit precision, peak KV memory is strictly bounded:
   $$M_{\text{KV}}^{\text{peak}} = 2 \cdot L \cdot H \cdot d_k \cdot (W_{\text{in}} + T_{\text{gen}}) \cdot 2\,\text{bytes} \approx 0.53\,\text{GB}$$
2. **Headroom Buffer Enforcement:** The configured headroom safety buffer $\Delta_{\text{headroom}} \ge 1.0\,\text{GB}$ ensures that:
   $$\Delta_{\text{headroom}} > M_{\text{KV}}^{\text{peak}} + M_{\text{workspace}} + M_{\text{runtime}}$$
   Consequently, total physical memory remains safely below host capacity, eliminating Out-Of-Memory (OOM) kernel terminations across all evaluated hardware configurations.
