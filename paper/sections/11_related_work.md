# Section 11: Related Work & Feature Taxonomy

The challenge of deploying high-capability language model intelligence under constrained hardware resources has motivated substantial research across the machine learning systems and systems software communities. Existing efforts broadly bifurcate into four distinct paradigms: (1) LLM routing and model cascading, (2) tensor and activation offloading, (3) multi-agent frameworks and agent operating systems, and (4) multi-tenant parameter adapter serving. In this section, we provide a problem-oriented taxonomy analyzing these four paradigms, highlighting their fundamental boundary conditions, and presenting a multi-dimensional feature comparison matrix contrasting ModelVM against representative state-of-the-art systems.

---

## 11.1 Problem-Oriented Systems Taxonomy

### 1. LLM Model Routing and Cascading
Model routing systems, such as RouteLLM, FrugalGPT, HyDRA, and FLARE, optimize inference quality and commercial API expenditure by dispatching incoming user queries across heterogeneous models. For example, simple factual questions are routed to lightweight or cheaper models (e.g., 7B open-weight models or GPT-3.5), whereas complex multi-step reasoning queries are escalated to frontier models (e.g., 70B models or GPT-4).

While conceptually related in their pursuit of capability matching, existing routers operate under an unstated physical assumption: **zero-cost model access**. Routers assume that candidate models are either hosted as stateless remote HTTP endpoints in commercial cloud datacenters or held simultaneously resident in large, unconstrained cluster memory pools. Consequently, they optimize single-shot classification objectives without modeling the physical latency of streaming multi-gigabyte weight tensors over local memory buses. When deployed on local consumer hardware equipped with fixed physical memory ($\mathcal{B}_{\text{RAM}} = 8.0\,\text{GB}$), standard routers suffer catastrophic thrashing or immediate Out-Of-Memory (OOM) aborts because dispatching a new model requires dynamically unloading and reloading tens of gigabytes of parameter weights. Furthermore, model routers treat queries as isolated, memoryless events, lacking mechanisms to virtualize and preserve cumulative state across multi-stage procedural pipelines. ModelVM resolves these limitations by explicitly unifying capability-aware scheduling with physical memory budgeting, predictive working-set eviction shielding, and typed state virtualization.

### 2. Weight and Activation Offloading Systems
To execute models exceeding physical accelerator capacity, offloading frameworks stream parameter tensors between storage tiers during forward inference. FlexGen optimizes high-throughput batch generation on a single GPU by storing model weights, activations, and Key-Value (KV) caches across a three-tier memory hierarchy (GPU VRAM, host CPU RAM, and secondary NVMe SSD), scheduling tensor computation and I/O transfers via zig-zag linear programming. LLM in a Flash leverages activation sparsity in Feed-Forward Networks (FFNs), dynamically streaming only the non-zero neuron parameter slices from high-speed flash storage into RAM. PowerInfer exploits activation locality by preloading "hot" neurons with high activation frequencies onto the GPU while evaluating rarely activated "cold" neurons on the host CPU.

Despite their throughput innovations, offloading systems exhibit two foundational architectural constraints that separate them from ModelVM:
1. **Monolithic Architectural Restriction:** Offloading frameworks virtualize the layers or neurons of a *single homogeneous neural architecture* (e.g., a single monolithic OPT-66B or Llama-2-70B model). They cannot coordinate heterogeneous open-weight specialists trained under disparate architectural configurations, vocabulary tokenizers, and hidden-state manifolds.
2. **Microscopic Paging Latency Penalty:** By operating at the micro-granularity of individual transformer layers or FFN neurons, offloading systems stream parameters across the PCIe bus repeatedly for every generated token. On commodity consumer hardware (PCIe 4.0 $\times 4$ at $3.0$--$4.0\,\text{GB/s}$), offloading a 70B parameter model limits generation speeds to an interactive stall ($< 0.2$--$0.5\,\text{tokens/s}$).

ModelVM adopts a macroscopic, **stage-level capability paging abstraction**: rather than thrashing weight slices on every token, ModelVM stages entire specialized open-weight models (6.7B--14B) for whole computational phases, amortizing the PCIe bus transfer latency over long execution sequences while maintaining semantic continuity via the Cognitive State Packet.

### 3. Multi-Agent Frameworks and Agent Operating Systems
Multi-agent systems, such as AutoGen, CAMEL, and declarative programming frameworks like DSPy, orchestrate complex reasoning pipelines by passing natural language messages between autonomous LLM instances. Concurrently, emerging "Agent Operating System" architectures, such as MemGPT and AIOS, propose systems abstractions for language models. MemGPT introduces OS-inspired hierarchical virtual memory to manage LLM context windows, paging conversational historical chunks between primary prompt memory and external vector databases. AIOS implements an agent kernel that schedules LLM tool invocations, manages context switching, and mediates access to external execution sandboxes.

However, existing multi-agent and agent OS architectures operate strictly at the *symbolic application layer*. In multi-agent frameworks, state transfer relies on raw conversational transcript concatenation, which triggers geometric context expansion ($L_{\text{ctx}} = O(t \cdot \bar{L}_{\text{gen}})$), lossy FIFO window truncation, and compounding arithmetic drift when crossing heterogeneous model boundaries. Furthermore, agent operating systems such as AIOS do not manage physical hardware memory budgets for model weights; they assume the underlying LLM is an omniscient, permanently resident server process or remote cloud API. ModelVM bridges this fundamental systems gap by virtualizing both levels: virtualizing semantic state across disparate specialist models through typed, AST-verified 9-tuples ($\mathcal{S}_t$), and virtualizing physical weight residency through hardware-enforced working-set paging ($W(t, k)$).

### 4. Multi-Tenant Parameter Adapter Serving
Systems such as S-LoRA and Punica address the multi-tenant deployment bottleneck by serving thousands of domain-specialized Low-Rank Adaptation (LoRA) adapters on top of a single shared base model. S-LoRA manages adapter parameter tensor allocations in unified host-GPU memory pools, dynamically loading low-rank weight matrices ($\Delta W = BA$) into GPU memory while reusing the frozen base model weights. vLLM optimizes memory management for attention states via PagedAttention, eliminating external memory fragmentation.

While adapter multiplexing achieves high efficiency for homogeneous adapter sets, it cannot address the broader reality of open-weight open-source specialization:
- **Heterogeneous Base Model Incompatibility:** The leading open-weight specialists are trained on completely independent foundational architectures and tokenizers. For example, state-of-the-art mathematical reasoning is achieved by *Qwen2.5-Math* (specialized vocabulary, rotary base $10^6$), code synthesis by *DeepSeek-Coder* (2T multi-language code pretraining), physical reasoning by *Llama-3-Physics*, and biomedical extraction by *Mistral-Research*. These models cannot be expressed as low-rank adjustments over a single generic base model.
- **Architectural Freedom:** ModelVM treats the heterogeneous open-weight ecosystem as an unconstrained computational catalog, enabling edge workstations to orchestrate independently developed specialist models without requiring weight re-training, structural alignment, or shared base topologies.

---

## 11.2 Multi-Dimensional Feature Comparison Matrix

Table 1 provides a comprehensive, multi-dimensional feature comparison contrasting ModelVM against prominent systems across the LLM systems landscape.

### Table 1: Architectural Comparison: ModelVM vs. Representative State-of-the-Art Language Model Systems

| Systems Dimension | FlexGen | LLM in Flash | RouteLLM | AIOS | S-LoRA | ModelVM (Ours) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Target Memory Environment** | Constrained GPU / CPU / NVMe | Constrained RAM / Flash | Cloud / Server (Unconstrained) | Application Layer (Unconstrained) | Multi-tenant Server GPU | **Constrained Hardware ($\mathcal{B}_{\text{RAM}} = 8.0\,\text{GB}$)** |
| **Model Heterogeneity** | Monolithic Single Model | Monolithic Single Model | Heterogeneous Cloud Endpoints | Homogeneous Resident Base | Homogeneous Shared Base | **Heterogeneous Specialists ($10$ Architectures)** |
| **Paging Granularity** | Layer-wise Tensors | FFN Neuron Slices | None (Stateless API Call) | Tool / Agent Context Call | LoRA Adapter ($\Delta W$) | **Stage-Level Model Weights** |
| **State Representation** | KV-Cache Tensors | KV-Cache Tensors | Raw Conversational Strings | Unstructured Dialog Strings | Shared Token Context | **Typed 9-Tuple CSP ($\mathcal{S}_t$)** |
| **Arithmetic Verification** | None | None | None | None | None | **Independent AST Verification** |
| **Residency Management** | Zig-Zag Linear Program | Dynamic Neuron Activation | None (Permanently Resident) | Tool Queue Scheduling | Unified Paged Adapter Pool | **Predictive Working Set $W(t, k)$** |
| **Eviction Policy** | Pre-computed Static Schedule | Neuron Reactivation LRU | None | Priority Agent Scheduling | LRU Adapter Eviction | **Cost-Aware Shielded Eviction** |
| **Bus Contention Mitigation** | Pipelined Block Offloading | Flash Read Merging | None | None | Adapter Tensor Prefetch | **Headroom-Gated Staging ($U_{\text{prefetch}}$)** |
| **Zero-Training Deployment** | Yes | Yes | Requires Router Classifier | Yes | Requires LoRA Fine-Tuning | **Yes (Off-the-Shelf Models)** |

As demonstrated in Table 1, ModelVM is the first systems runtime to simultaneously address physical hardware memory boundedness, heterogeneous model architectures, predictive residency management, and architecture-agnostic semantic state preservation.
