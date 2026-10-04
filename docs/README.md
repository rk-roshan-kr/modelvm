# ModelVM Documentation Suite

Welcome to the comprehensive documentation suite for **ModelVM: Virtual Memory for Intelligence**.

This directory contains both academic research papers / literature analyses and full engineering / API specifications for the implemented codebase.

---

## 1. Academic Research & Theoretical Foundations

| Document | Description | Target Venue |
| :--- | :--- | :--- |
| **[`research_gap_and_novelty.md`](file:///d:/hacktoberfest/docs/research_gap_and_novelty.md)** | **Research Gap, Novelty Defense & Scientific Contributions**<br>Formal three-way gap definition, state-of-the-art analysis, detailed novelty defense across 4 system mechanisms, concrete contributions, and counter-arguments to reviewer critiques. | Theoretical Positioning & Reviewer Defense |
| **[`positioning_paper.md`](file:///d:/hacktoberfest/docs/positioning_paper.md)** | **Full Academic Research Paper (Preprint)**<br>Abstract, Formal System Architecture, Cognitive State Packet Formalism, Predictive Working Set Theory, Resource-Aware Scheduling Objective, Critical Ablation Study (Configurations A, B, C, D), Discussion & Benchmark Analysis. | Conference Preprint (MLSys / OSDI / NeurIPS style) |
| **[`literature_review.md`](file:///d:/hacktoberfest/docs/literature_review.md)** | **Comprehensive Literature Survey**<br>In-depth critical analysis across 5 research axes: (1) Heterogeneous LLM Routing (HyDRA, FLARE, RouteLLM, FrugalGPT), (2) Tensor Offloading (FlexGen, LLM in a flash, PowerInfer), (3) OS Abstractions for AI (MemGPT, AIOS), (4) Multi-Agent Systems & State Transfer, and (5) Classical Working Set Theory (Denning). | Academic Literature Review |
| **[`taxonomy.md`](file:///d:/hacktoberfest/docs/taxonomy.md)** | **Comparative Systems Matrix & Dimensional Analysis**<br>Direct feature-by-feature comparison table evaluating ModelVM against 11 major systems across Paging Unit, Hard Budget Enforcement, Heterogeneity, Inter-Model State, and Working Set Prediction. | Systems Matrix & Taxonomy |
| **[`biblio.bib`](file:///d:/hacktoberfest/docs/biblio.bib)** | **BibTeX Reference Database**<br>Full BibTeX citations for all related papers (HyDRA, FLARE, FlexGen, LLM in a flash, RouteLLM, FrugalGPT, MemGPT, AIOS, PowerInfer, S-LoRA, vLLM, AutoGen, CAMEL, DSPy, and Peter Denning's seminal working set papers). | BibTeX Database |

---

## 2. Implemented Codebase & Engineering Specifications

| Document | Description | Audience |
| :--- | :--- | :--- |
| **[`codebase_architecture.md`](file:///d:/hacktoberfest/docs/codebase_architecture.md)** | **System Architecture & Technical Specification**<br>Detailed architectural blueprint of the implemented Python codebase (`modelvm/`). Covers Core Data Models, Virtual Memory Pager, Eviction Policies, Cognitive Scheduler, Task Decomposer, Working Set Predictor, Confidence Controller, and Web Visualizer. | Systems Engineers & Contributors |
| **[`api_reference.md`](file:///d:/hacktoberfest/docs/api_reference.md)** | **Complete API & Technical Reference**<br>Full signatures, parameters, return types, and usage examples for all classes (`CognitiveStatePacket`, `ModelPager`, `CognitiveScheduler`, `CognitiveKernel`, `AblationStudyRunner`, REST & WebSocket endpoints). | Developers & Integrators |
| **[`developer_guide.md`](file:///d:/hacktoberfest/docs/developer_guide.md)** | **Developer & Extensibility Guide**<br>Step-by-step tutorials: (1) Registering new models with YAML manifests, (2) Implementing custom eviction algorithms, (3) Connecting real local LLMs (Ollama, llama.cpp, vLLM), and (4) Tuning scheduler weights ($\alpha, \beta, \gamma, \delta, \eta$). | Developers & Researchers |

---

## 3. High-Level Summary of Findings

* **The Problem:** Deploying a diverse suite of 10 specialized open-weight models requires **52.7 GB of memory**, causing Out-Of-Memory (OOM) on consumer hardware with 8.0 GB RAM envelopes.
* **The Solution:** Treating models as pageable cognitive resources that are dynamically paged into RAM, synchronized through model-neutral **Cognitive State Packets (CSP)**, and evicted using cost-aware working-set policies.
* **Key Results:**
  * **85.6% Physical Memory Savings** (Operates inside 7.6 GB peak RAM under an 8.0 GB budget).
  * **98% Quality Coverage** (Zero information loss across 5 domain hops).
  * **0.66 Capability Density** (Top score in Critical Ablation Study).
