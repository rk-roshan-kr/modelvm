# ModelVM: Paper Master Skeleton & Empirical Mapping Matrix

This document provides the definitive architectural blueprint for the full manuscript. Each subsection is defined with its exact scientific claim, formal mathematics, required tables/figures, empirical grounding, and specific reviewer defenses.

---

## Final Paper Layout (14 Sections)

```text
0.  Abstract
1.  Introduction
2.  Problem Formulation & Design Goals
3.  ModelVM Architecture & Runtime Abstraction
4.  Semantic State Virtualization (Cognitive State Packet / CSP)
5.  Predictive Model Residency & Working Set
6.  Resource-Aware Cognitive Scheduling
7.  Implementation & Systems Mechanics
8.  Experimental Methodology
9.  Results
10. Discussion & Systems Implications
11. Related Work
12. Limitations & Threats to Validity
13. Conclusion
References & Appendix
```

---

## Detailed Section-by-Section Master Skeleton

### 8. Experimental Methodology (First Writing Segment)

#### 8.1 Research Questions
* **Claim Established:** The experimental evaluation systematically targets four concrete hypotheses derived directly from our systems abstraction (RQ1 $\rightarrow$ H1, RQ2 $\rightarrow$ H2, RQ3 $\rightarrow$ H3, RQ4 $\rightarrow$ H4).
* **Formal Artifact:** Mapping table of $RQ \times \text{Hypothesis} \times \text{Experiment} \times \text{Primary Metric}$.
* **Writing Style / Texture:** Deliberate, exact, assertive. Abrupt opening: *"Systems claims require empirical isolation."* Varied sentence length contrasting formal hypotheses with explicit boundary conditions.

#### 8.2 Hardware Testbeds & Measurement Apparatus
* **Claim Established:** Telemetry captures physical host and accelerator behavior across an enforced 8.0\,GB runtime memory budget ($\mathcal{B}_{\text{RAM}}$), accounting for cold-load I/O, memory pinning, and bus contention.
* **Hierarchical Memory Model:** Explicit tracking across three tiers: $\text{Storage} \rightarrow \text{Host RAM} \rightarrow \text{Accelerator VRAM}$. Tracks $M_{\text{RAM}}(t)$ via `/proc/[pid]/statm` and $M_{\text{VRAM}}(t) = M_{\text{weights}} + M_{\text{workspace}} + M_{\text{KV}}$ via NVML.
* **Telemetry Primitives:** Hardware RSS extraction via OS kernel calls (`psutil`), GPU delta tracking (`nvml`), and high-resolution wall-clock timers.

#### 8.3 The Heterogeneous Model Catalog
* **Claim Established:** The 10-model catalog (52.7\,GB storage baseline) represents genuine disciplinary specialization across open-weight transformer architectures (Mistral, Qwen2, DeepSeek, Llama3, StarCoder, Command-R), differing in quantization and parameter scales (6.7B–14B).
* **Formal Artifact:** Table 2: Model ID, Base Architecture, Quantization Format, Parameter Count, Host Footprint (GB), Dedicated Weights VRAM (GB), CUDA Workspace (GB), Cold Load Time (s), and Measured Token Latency. Grounded via empirical capability profiling matrix $\mathbf{P} \in [0, 1]^{N \times M}$ (`ModelProfiler`).

#### 8.4 Multi-Stage Cross-Domain Workloads
* **Claim Established:** Workloads intentionally span multiple specialized domains for which capability varies substantially across the model catalog.
* **Workload Pipeline:** $\text{Research} \rightarrow \text{Mathematics} \rightarrow \text{Coding} \rightarrow \text{Physics} \rightarrow \text{Synthesis}$.
* **Formal Artifact:** Task DAG definition $G = (S, E)$ with formal stage input/output dependencies and ground-truth definitions.

#### 8.5 Token-Budget & Execution Controls
* **Claim Established:** Confounding variables are eliminated through fixed token limits: $W_{\text{in}} = 4,096$ tokens, $T_{\text{gen}} = 1,024$ tokens, greedy decoding ($T=0.0$), FIFO sliding context window for raw text, and isolated CSP serialization overhead tracking.

#### 8.6 Baselines Spectrum
* **Claim Established:** Baselines represent a comprehensive, non-strawman continuum from standard practice to naive dynamic approaches:
  1. **$B_0$ (Static Monolith):** Single general-purpose model (`general-reasoner`, 7.1\,GB) executing all stages within memory.
  2. **$B_{\text{static}}$ (Static Specialist Ensemble):** Top-2 specialists fitting within 8.0\,GB runtime budget simultaneously (`mathematics-expert` + `coding-expert` = 5.4\,GB); routes only between resident models without paging.
  3. **$B_1$ (Unconstrained Specialist Router):** Capability-based model selection assuming an unconstrained memory pool ($\mathcal{B}_{\text{RAM}} = \infty$) as an upper-bound baseline.
  4. **$B_2$ (Router + Raw Text + Reactive LRU):** Dynamic loading under 8.0\,GB budget; reactive LRU eviction; raw text transcript concatenation.
  5. **$B_3$ (Router + CSP + Unconstrained):** Specialist routing with CSP state virtualization under unconstrained memory ($\mathcal{B}_{\text{RAM}} = \infty$).
  6. **$B_4$ (Router + CSP + Reactive LRU):** Dynamic loading under 8.0\,GB budget; reactive LRU eviction; typed CSP state handoff.
  7. **$B_5$ (Full ModelVM):** Dynamic loading under 8.0\,GB budget; predictive working set $W(t, k)$ + eviction shielding; multi-objective scheduling; typed CSP state handoff.
  8. **$B_{\text{oracle}}$ (Offline Oracle Scheduler):** Theoretical upper bound with perfect advance knowledge of pipeline stage requirements.

#### 8.7 Factorial Design & Feature Gating
* **Claim Established:** The $2^3$ orthogonal factorial matrix over the dynamic paging substrate permits systematic estimation of main effects ($\Delta_{\text{CSP}}, \Delta_{\text{WS}}, \Delta_{\text{Sched}}$) and multi-way interaction terms without confounding among the factorial factors.
* **Formal Artifact:** Matrix specification table (`C0` through `C7` + `REF_STATIC_MONOLITH`).

#### 8.8 Metrics Framework
* **Claim Established:** Evaluation measures performance across four complementary dimensions:
  1. **Quality ($Q$):** Capability Coverage Score (CCS) and AST-verified calculation ratio ($R_{\text{calcs}}$).
  2. **State Retention ($R$):** Ground-truth fact survival ratio ($R_{\text{facts}}$) and semantic drift index ($D_{\text{drift}}$).
  3. **Resource Consumption ($E$):** Peak physical RAM/VRAM footprint ($M_{\text{peak}}$), memory virtualization ratio ($T/B$).
  4. **Latency \& Systems Efficiency ($L$):** Total wall-clock execution time, cold-load paging time ($t_{\text{paging}}$), cache hit rate ($H_{\text{cache}}$), reload frequency ($N_{\text{reload}}$).

#### 8.9 Statistical Rigor & Non-Circularity Harness
* **Claim Established:** Evaluation eliminates circular self-grading via an external, non-mutating AST verifier (`ArithmeticVerifier`) and structured physical truth objects (`GroundTruthFact`). Defines $n=10$ matched trials, two-sided paired permutation tests, empirical bootstrap percentile intervals $\text{CI}_{95} = [q_{0.025}, q_{0.975}]$, and Holm-Bonferroni correction.

---

### 9. Results (Second Writing Segment)

#### 9.1 Overall System Comparison (The Signature Table)
* **Claim Established:** ModelVM achieves specialist-grade task accuracy under an 8.0 GB budget while outperforming monolithic models and reducing reload stalls compared to naive paging.
* **Primary Artifact:** The Signature Progression Table ($B_0, B_{\text{static}}, B_1, B_2, B_3, B_4, B_5$).

#### 9.2 Experiment 1: Semantic State Virtualization (CSP vs. Raw Text, H1 Validation)
* **Claim Established (H1 Validation):** CSP reduces the propagation of state and calculation errors across multi-model boundaries relative to unstructured text handoff as context length and pipeline depth increase.
* **Primary Artifact:** State retention curve ($R_{\text{facts}}$ and $R_{\text{calcs}}$ vs. stage index $t$).

#### 9.3 Experiment 2: Predictive Residency vs. Reactive Eviction (H2 Validation)
* **Claim Established (H2 Validation):** $W(t, k)$ lookahead and eviction shielding reduce memory thrashing and cold-load stalls relative to classical LRU eviction under the evaluated workloads.
* **Primary Artifact:** Cold-load latency ($t_{\text{paging}}$), cache hit rate ($H_{\text{cache}}$), eviction count, and reload count across $B_2$, $B_4$, and $B_5$.

#### 9.4 Experiment 3: Resource-Aware Scheduling vs. Greedy Selection (H3 Validation)
* **Claim Established (H3 Validation):** Multi-objective scoring avoids scheduling models that provoke massive eviction penalties or excessive cold loads when comparable resident models suffice, maintaining higher goodput and bounded regret against an offline oracle.
* **Primary Artifact:** Scheduling decision breakdown, goodput comparison, and regret gap ($\Delta_{\text{oracle}}$).

#### 9.5 Factorial Effect Decomposition (Yates Analysis)
* **Claim Established:** Quantitative isolation of mechanism contributions: $\Delta_{\text{CSP}}$ dominates task quality and state preservation, while $\Delta_{\text{WS}}$ and $\Delta_{\text{Sched}}$ govern latency reduction and memory stability.
* **Primary Artifact:** Replicated Yates analysis effect table with bootstrap 95% confidence intervals and ANOVA validation.

#### 9.6 Multi-Dimensional Quality–Resource Pareto Frontiers (H4 Validation)
* **Claim Established (H4 Validation):** ModelVM establishes a newly accessible operational region in Quality vs. Peak Memory and Quality vs. Execution Latency, dominating naive paging and static baselines.
* **Primary Artifact:** Two 2D Pareto frontier scatter plots (Quality vs. Memory; Quality vs. Latency) and 3D response surface.

#### 9.7 Experiment R1: Memory-Pressure Sweep (Robustness Validation)
* **Claim Established:** ModelVM degrades gracefully under extreme memory constraints ($\mathcal{B}_{\text{RAM}} \in \{4, 6, 8, 10, 12, 16\}$\,GB) rather than suffering catastrophic failure, approaching resident latency as budget expands.
* **Primary Artifact:** Quality–Memory–Latency response curves and OOM failure rate across memory envelopes.

#### 9.8 Experiment R2: Model-Transition Stress Test (Scalability Validation)
* **Claim Established:** State retention under typed CSP remains robust across repeated, cyclic specialist switches (up to 12 transitions), whereas raw text handoff exhibits rapid geometric state degradation.
* **Primary Artifact:** State retention ($R_{\text{facts}}, R_{\text{calcs}}, D_{\text{drift}}$) as a function of model transition depth ($W_1$ to $W_5$).

#### 9.9 Experiment R3: Workload-Distribution Robustness (Generalization Validation)
* **Claim Established:** The multi-objective scheduler generalizes across divergent workload regimes (Research-heavy, Compute-heavy, Coding-heavy, Mixed) without domain-specific retuning, maintaining low regret against the offline oracle.
* **Primary Artifact:** Goodput, CCS, reload frequency, and oracle gap ($\Delta_{\text{oracle}}$) across workload distributions.

---

### 7. Implementation & Systems Mechanics (Third Writing Segment)

* **7.1 The Runtime Control Loop:** Concrete execution state machine $(\mathcal{S}_t, s_t, \mathcal{R}_t) \to (W_t, M_t) \to \text{PageIn}(M_t) \to M_t(\mathcal{S}_t) \to \mathcal{S}_{t+1}$, formal algorithm distinguishing planning, residency, execution, AST verification, and state persistence.
* **7.2 CSP Schema Serialization & Delta Tracking:** Data structures for the 9-tuple $\mathcal{S}_t$, JSON and prompt serialization formats, arithmetic calculation records, evidence provenance, artifact dictionary versioning, monotonic `merge_update()`, and token footprint accounting.
* **7.3 Model Pager & Memory Manager:** Resident model tracking table $\mathcal{R}_t$, hard memory budget enforcement ($\sum_{m \in \mathcal{R}_t} \text{RAM}(m) \le \mathcal{B}_{\text{RAM}}$), LRU vs. Cost-Aware eviction policies, eviction shielding factor ($\delta \cdot 1.8$), and background prefetching buffers.
* **7.4 Working Set Predictor Engine:** Stage decomposition lookahead queue $W(t, k)$, distance-decay capability demand forecasting ($w_j = \gamma^{j-1}$), scheduler score integration, and prefetch utility $U_{\text{prefetch}}$ under headroom invariant $(\text{RAM}_{\text{free}} - \text{RAM}(m) \ge 1.0\,\text{GB})$.
* **7.5 Telemetry Instrumentation:** Concrete measurement layer: physical host RSS extraction via `/proc/[pid]/statm` and OS counters, NVML VRAM profiling ($M_{\text{VRAM}} = M_{\text{weights}} + M_{\text{workspace}} + M_{\text{KV}}$), wall-clock paging latency measurement ($T_{\text{page}} = T_{\text{ready}} - T_{\text{start}}$), and independent AST verification harness.

---

### 4. Semantic State Virtualization (Fourth Writing Segment)

* **4.1 The Incompatibility Barrier:** Incompatible tokenizers ($\mathcal{V}_A \neq \mathcal{V}_B$), latent space divergence ($\mathbf{h} \in \mathbb{R}^d$), and why text concatenation fails.
* **4.2 The 9-Tuple Formalism:** $\mathcal{S}_t = \langle \mathcal{G}, \mathcal{F}_t, \mathcal{C}_t, \mathcal{E}_t, \mathcal{A}_t, \mathcal{U}_t, \mathcal{D}_t, \mathcal{Q}_t, \mathcal{O}_t \rangle$.
* **4.3 State Transition Mechanics:** Mathematical state transition function $\mathcal{S}_{t+1} = \delta(\mathcal{S}_t, M_i, \tau_t)$.
* **4.4 Epistemic Diversity-Discounted Evidence Aggregation:** Formal derivation of $w_{\text{source}} = 0.65$ correlation discount.
* **4.5 Independent Verification & Non-Mutating Evaluation:** Formal AST verification model.
* **4.6 Computational Complexity & Token Overhead:** Concrete byte and token overhead of CSP serialization.

---

### 5. Predictive Model Residency (Fifth Writing Segment)

* **5.1 The Weight Residency Problem:** Hardware memory bounds and I/O bus latency profiles.
* **5.2 The Predictive Cognitive Working Set:** $W(t, k) = \{ \arg\max_{m} \text{CapabilityMatch}(m, C_{t+j}) \mid j \in [1, k] \}$.
* **5.3 Cost-Aware Eviction & Imminent Model Shielding:** Eviction penalty formula with $\delta \times 1.8$ shield factor.
* **5.4 Time-Domain Prefetch Utility:** $U_{\text{prefetch}} = P(m) \cdot \Delta L_{\text{avoided}} - \lambda M_{\text{cost}} - \mu E_{\text{prefetch}}$.
* **5.5 Predictor Misprediction Analysis:** System behavior and graceful degradation under task re-planning.

---

### 6. Resource-Aware Cognitive Scheduling (Sixth Writing Segment)

* **6.1 The Multi-Objective Optimization Problem:** Formal constrained optimization objective.
* **6.2 Unified Scoring Formulation:** Term-by-term definition of capability fitness, memory cost, load latency, energy, eviction, and future reuse.
* **6.3 Empirical Capability Profiling (`ModelProfiler`):** Replacing arbitrary weights with empirical benchmark probe matrices across 7 domains.
* **6.4 Parameter Sensitivity Analysis:** Stability analysis of hyperparameters $\alpha, \beta, \gamma, \delta, \eta$.

---

### 2. Problem Formulation & Design Goals (Seventh Writing Segment)

* **2.1 Formal System Model:** Hardware memory bounds $\sum \text{RAM}(M_i) \gg \mathcal{B}_{\text{RAM}}$, task state representations, and execution constraints.
* **2.2 Four Concrete Design Goals:** State Continuity (G1), Resource Boundedness (G2), Capability Specialization (G3), and Transition Efficiency (G4).

---

### 3. ModelVM Architecture & Runtime Abstraction (Eighth Writing Segment)

* **3.1 De-centering the OS Metaphor:** Explaining how state decoupling and pageable residency naturally inspire runtime primitives without overclaiming kernel identity.
* **3.2 Architectural Flow & Control Path:** Detailed architectural block diagram and dataflow paths.
* **3.3 The Memory Invariant:** Proof that active resident models never violate physical budget $\mathcal{B}_{\text{RAM}}$.

---

### 11. Related Work (Ninth Writing Segment)

* **11.1 Problem-Oriented Taxonomy:** Comparison against Model Routing, Tensor Offloading, Agent Operating Systems, and Adapter Serving.
* **11.2 Feature Comparison Matrix:** Side-by-side verification table across systems.

---

### 10. Discussion & Systems Implications (Tenth Writing Segment)

* **10.1 Why State Virtualization is Fundamental:** Beyond multi-agent prompting.
* **10.2 Why Residency Must Be Predictive:** Bus saturation and pipeline physics.
* **10.3 Failure Regimes:** Where ModelVM does not yield benefits (e.g. monolithic single-domain queries).
* **10.4 Broader Systems Implications:** Local AI computing without monolithic centralization.

---

### 12. Limitations & Threats to Validity (Eleventh Writing Segment)

* **12.1 Internal Validity:** Simulator vs. physical device characteristics; AST verifier scope.
* **12.2 External Validity:** Workload breadth, open-weight quantization formats, bus bandwidth dependencies.
* **12.3 Construct Validity:** Metrics coverage and non-circularity guarantees.

---

### 1. Introduction (Twelfth Writing Segment)

* **Narrative Arc:** Domain specialization frontier $\rightarrow$ Memory barrier $\rightarrow$ Tripartite separation $\rightarrow$ Systems insight $\rightarrow$ Summary of contributions.

---

### 13. Conclusion (Thirteenth Writing Segment)

* Concise summary of scientific thesis confirmation and forward outlook.

---

### 0. Abstract & Title (Final Step)

* Distilled directly from final empirical evidence and substantiated claims.
