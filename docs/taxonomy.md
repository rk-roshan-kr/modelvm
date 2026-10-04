# Taxonomy & Comparative Systems Matrix

This document provides a systematic taxonomy comparing **ModelVM** against existing literature across five related domains:
1. **Dynamic Model Routers & Cascades** (HyDRA, FLARE, RouteLLM, FrugalGPT)
2. **Memory-Constrained Inference & Tensor Offloading** (FlexGen, LLM in a Flash, PowerInfer)
3. **OS-Inspired LLM Frameworks** (MemGPT, AIOS)
4. **Multi-Tenant Adapter Serving** (S-LoRA, Punica, vLLM)
5. **Multi-Agent Orchestration Frameworks** (AutoGen, CAMEL, LangGraph)

---

## 1. Comparative Architecture Matrix

| System | Paging / Management Unit | Hard RAM Budget Enforced? | Heterogeneous Models? | Inter-Model State Medium | Predictive Working Set / Lookahead? | Scheduling Objective |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HyDRA** (Microsoft/GitHub 2026) | Single Query Request | ❌ No (Assumes all models resident or cloud-hosted) | Yes (Catalog pool) | None (Single-hop dispatch) | ❌ No | Capability Shortfall Matching (ModernBERT encoder) |
| **FLARE** (Zhang et al. 2024) | Single Query Request | ❌ No (Cloud serving cluster) | Yes (Fixed API pool) | None (Single-hop dispatch) | ❌ No | Length-aware latency & cost optimization |
| **RouteLLM** (LMSYS 2024) | Single Query Request | ❌ No (Cloud APIs) | Limited (Strong vs Weak pair) | None (Binary choice) | ❌ No | User preference / Elo win-rate prediction |
| **FrugalGPT** (Chen et al. 2023) | Single Query Request | ❌ No (Cloud API spend limit) | Yes (Commercial APIs) | None (Sequential escalation cascade) | ❌ No | Monetary API cost minimization |
| **FlexGen** (Sheng et al. 2023) | Weights & KV Tensors | ✅ Yes (Single GPU VRAM) | ❌ No (Single static monolithic model, e.g. OPT-175B) | N/A (Internal activations within one model) | ❌ No (Fixed zigzag linear programming schedule) | Throughput / batch-size maximization |
| **LLM in a Flash** (Apple 2023) | Sparse Neurons / Weight Bundles | ✅ Yes (Mobile DRAM) | ❌ No (Single static model) | N/A (Internal neuron activations) | Windowing heuristic | Flash I/O reduction via row-column bundling |
| **PowerInfer** (Song et al. 2024) | Hot/Cold Activation Neurons | ✅ Yes (GPU VRAM) | ❌ No (Single static model) | N/A (Split GPU-CPU neuron graph) | Online predictor | Activation sparsity exploitation |
| **MemGPT** (Packer et al. 2023) | Context Window Tokens | ❌ No (RAM = Token Context, Disk = Vector DB) | ❌ No (Single foundation model) | N/A (External vector database paging) | ❌ No | Memory recall & context expansion |
| **AIOS** (Mei et al. 2024) | Agent System Calls / Tools | ❌ No (CPU/GPU process scheduling) | ❌ No (Treats LLMs as cloud or black-box servers) | Conversational text / Tool IO | ❌ No | Agent scheduling & access control |
| **S-LoRA / Punica** (Sheng et al. 2024) | LoRA Adapter Weights | ✅ Yes (Unified GPU memory) | ❌ No (Homogeneous base model + LoRA heads) | N/A (Parallel batched heads on one base model) | ❌ No | Batch throughput of LoRA adapters |
| **AutoGen / LangGraph** (Wu et al. 2023) | Conversational Agent Turns | ❌ No (Cloud token endpoints) | Yes (Via API wrappers) | Raw unstructured chat transcript | ❌ No | Heuristic or graph workflow rules |
| **ModelVM** (Ours) | **Cognitive Model Capability** | **✅ Yes (Hard RAM/VRAM Envelope, e.g. 8.0 GB)** | **✅ Yes (10+ Heterogeneous Open-Weight Models)** | **Cognitive State Packet (CSP: structured semantic state)** | **✅ Yes ($W(t, k)$ predictive lookahead & prefetching)** | **Resource-aware: $\text{Fit} - \alpha \text{RAM} - \beta \text{Load} - \gamma \text{Energy} - \delta \text{Evict} + \eta \text{Future}$** |

---

## 2. Dimensional Analysis & Conceptual Taxonomy

```text
                                  AI RUNTIME TAXONOMY
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        ▼                                 ▼                                 ▼
 1. TENSOR / WEIGHT               2. ROUTING & CASCADING             3. COGNITIVE VIRTUAL
    OFFLOADING SYSTEMS               SYSTEMS (CLOUD/RESIDENT)           MEMORY (ModelVM)
        │                                 │                                 │
  FlexGen, LLM in Flash,            HyDRA, FLARE, RouteLLM,           ModelVM Runtime:
  PowerInfer, DeepSpeed-ZeRO        FrugalGPT, AutoMix                Pageable Cognitive Units
        │                                 │                                 │
  • Unit: Tensors/Layers            • Unit: Queries/API calls         • Unit: Model Capabilities
  • Goal: Run 1 Huge Model          • Goal: Pick 1 Model from Pool    • Goal: Multi-Domain AI
  • Single Architecture Only        • All Models Assumed Ready        • Hard Memory Budget (8 GB)
  • No Domain Routing               • No Physical RAM Control         • Dynamic Page-In/Eviction
  • No Inter-Model State            • No Multi-Stage State Transfer   • Semantic State Packet (CSP)
```

### Distinction 1: The Paging Abstraction
* **Traditional Offloading (FlexGen, LLM in a flash):** The paging unit is a sub-tensor slice or feedforward weight row inside a **single monolithic model**. They allow running a 70B model on limited RAM, but incur massive I/O overhead on every forward token pass and cannot pivot between specialized domain models.
* **MemGPT:** The paging unit is **tokens within the context window**. The "virtual memory" is prompt tokens swapped to a vector database, while the underlying model is a static, permanently loaded LLM.
* **ModelVM:** The paging unit is **an entire cognitive specialist model**. An 8.0 GB device maintains a 52.7 GB library of domain masters (Math, Coding, Physics, Research, Medicine, Finance) and pages in only the active capability required for the current stage.

### Distinction 2: State Persistence Across Heterogeneity
* **Multi-Agent Systems (AutoGen, LangGraph):** Pass raw natural language chat logs. In multi-hop tasks, conversational drift, hallucination accumulation, and prompt truncation cause severe performance collapse.
* **ModelVM (Cognitive State Packet):** Enforces a model-neutral, structured semantic interface consisting of formal mathematical calculations, verified empirical facts, explicit assumptions, calibrated uncertainties, and generated artifacts. Heterogeneous models of completely different tokenizers and parameter sizes communicate losslessly.

### Distinction 3: Predictive Working Set vs. Reactive Paging
* **Reactive Routers (HyDRA, FLARE):** Evaluate each query as an isolated point in time ($t$).
* **ModelVM:** Formulates task execution as a cognitive pipeline with a predictive working set $W(t, k)$. If an analytical calculation will be followed by numerical simulation code and physical verification, the scheduler shields the coding expert from eviction and prefetches upcoming weights into spare memory in the background.
