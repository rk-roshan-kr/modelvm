# ModelVM: Pre-Registered Experiment Registry (Step 1B — Expanded)

This registry establishes the binding scientific contract between **Section 8 (Methodology)** and **Section 9 (Results)**. No metric, baseline, or statistical test may be added or removed post-hoc during results reporting.

---

## 1. Primary Hypothesis Experiments (P0)

| Exp ID | Hyp. | Independent Variable (IV) | Control Condition | Fixed / Controlled Variables | Workload Trials | Primary Metric | Secondary Metrics | Statistical Test | CI Method | Correction | Expected Direction | Failure Criterion |
| :--- | :---: | :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-H1** | **H1** | State handoff: Typed CSP ($\mathcal{S}_t$) | Unstructured raw text handoff | Model sequence, prompt instructions, context limit ($4,096$), gen budget ($1,024$), greedy ($T=0.0$), $8.0$\,GB budget | $n=10$ matched task instances | Factual preservation ratio ($R_{\text{facts}}$) | Calculation accuracy ($R_{\text{calcs}}$), Token overhead, Drift ($D_{\text{drift}}$) | Two-sided paired permutation test | Bootstrap 95\% percentile $[q_{0.025}, q_{0.975}]$ | Holm | $\text{CSP} > \text{Raw Text}$ | $p \ge 0.05$ or $R_{\text{facts}}(\text{CSP}) \le R_{\text{facts}}(\text{Raw})$ |
| **EXP-H2** | **H2** | Residency policy: Predictive $W(t, k)$ | Classical reactive LRU eviction | State layer held fixed (CSP), task sequence, model catalog, $8.0$\,GB budget | $n=10$ matched task instances | Cold-load paging time ($t_{\text{paging}}$) | Cache hit rate ($H_{\text{cache}}$), Eviction count ($N_{\text{evict}}$), Reload count ($N_{\text{reload}}$) | Two-sided paired permutation test | Bootstrap 95\% percentile $[q_{0.025}, q_{0.975}]$ | Holm | $W(t, k) < \text{LRU}$ (latency/reloads); $W(t, k) > \text{LRU}$ (hits) | $p \ge 0.05$ or $t_{\text{paging}}(W) \ge t_{\text{paging}}(\text{LRU})$ |
| **EXP-H3** | **H3** | Scheduling policy: Multi-Objective Score | Greedy capability-only selection; Memory-aware greedy | State layer held fixed (CSP), memory budget ($8.0$\,GB), catalog capabilities | $n=10$ matched task instances | Task execution goodput | Capability coverage (CCS), OOM avoidance rate, Gap to Oracle ($\Delta_{\text{oracle}}$) | Two-sided paired permutation test | Bootstrap 95\% percentile $[q_{0.025}, q_{0.975}]$ | Holm | $\text{ModelVM} > \text{Greedy}$; $\text{ModelVM} \approx \text{Oracle}$ | $p \ge 0.05$ or $\text{Goodput}(\text{Score}) \le \text{Goodput}(\text{Greedy})$ |
| **EXP-H4** | **H4** | System architecture: Full ModelVM ($B_5$) | Monolith ($B_0$), Static Ensemble ($B_{\text{static}}$), Router+LRU ($B_2, B_4$) | Workload instances, hardware envelope ($8.0$\,GB), storage speed | $n=10$ matched task instances | 2D/3D Pareto dominance | Quality ($Q$), Peak Memory ($M_{\text{peak}}$), Total Latency ($L$) | Non-parametric Pareto frontier analysis | Empirical envelope estimation | N/A | ModelVM establishes unreached Pareto region | ModelVM is Pareto-dominated by $B_0$, $B_{\text{static}}$, $B_2$, or $B_4$ |
| **EXP-FACT**| **All** | Full $2^3$ orthogonal factorial matrix ($C_0$–$C_7$) | Base configuration ($C_0$) | Paging substrate, workload seeds, hardware environment | $n=10$ replicated runs | Yates main effect estimates ($\bar{\Delta}_A, \bar{\Delta}_B, \bar{\Delta}_C$) | Two-way and three-way interaction effects ($\bar{\Delta}_{AB}, \bar{\Delta}_{AC}, \bar{\Delta}_{BC}, \bar{\Delta}_{ABC}$) | Replicated Yates analysis with ANOVA validation | Bootstrap 95\% percentile $[q_{0.025}, q_{0.975}]$ | Holm-Bonferroni | $\bar{\Delta}_{\text{CSP}} > 0$; $\bar{\Delta}_{\text{WS}} \text{ on } L < 0$ | Main effects not distinguishable from zero ($p \ge 0.05$) |

---

## 2. Pre-Registered Robustness & Stress Experiments (P0 / P1)

| Exp ID | Priority | Target Vulnerability | Independent Variable (IV) | Control Conditions | Workload Regimes ($n=10$ trials each) | Primary Metric | Secondary Metrics | Statistical Test | Expected Direction | Failure Criterion |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-R1** | **P0** | Fixed-budget overspecialization ($8$\,GB only) | Runtime memory envelope $\mathcal{B}_{\text{RAM}}$ | Reactive LRU eviction ($B_4$) vs. Full ModelVM ($B_5$) | $\mathcal{B}_{\text{RAM}} \in \{4.0, 6.0, 8.0, 10.0, 12.0, 16.0\}\,\text{GB}$ under canonical 5-stage benchmark | Quality--Memory--Latency trade-off surface | Peak Host RSS, Peak VRAM, OOM crash frequency, $t_{\text{paging}}$, $H_{\text{cache}}$, $N_{\text{reload}}$, Goodput | Paired permutation test & Empirical curve estimation | ModelVM maintains $>85\%$ CCS at $4$\,GB with $0\%$ OOM; $t_{\text{paging}} \to 0$ as $\mathcal{B} \ge 12$\,GB | ModelVM OOM rate $> 0\%$ or dominated by LRU at any evaluated budget |
| **EXP-R2** | **P0** | Insufficient transition depth in baseline pipeline | Model transition count $N_{\text{trans}}$ | Raw text transcript handoff vs. Typed CSP ($\mathcal{S}_t$) | $W_1$ (1 switch), $W_2$ (2 switches), $W_3$ (4 switches), $W_4$ (8 switches), $W_5$ (12 switches) | State retention vs. transition count | Fact survival ($R_{\text{facts}}$), Calculation accuracy ($R_{\text{calcs}}$), Semantic drift ($D_{\text{drift}}$), Serialization overhead | Non-linear regression & permutation test on slope difference | CSP maintains $R_{\text{facts}} > 0.90$ across all $W_1$--$W_5$; Raw text degrades geometrically ($\le 0.40$ at $W_5$) | $R_{\text{facts}}(\text{CSP})$ drops below $0.75$ or is statistically indistinguishable from Raw Text at $W_4$--$W_5$ ($p \ge 0.05$) |
| **EXP-R3** | **P1** | Overfitting scheduler to single pipeline structure | Workload distribution regime | Capability-Greedy vs. Memory-Aware Greedy vs. ModelVM ($B_5$) vs. Offline Oracle ($B_{\text{oracle}}$) | $W_A$ (Research-heavy), $W_B$ (Compute-heavy), $W_C$ (Coding-heavy), $W_D$ (Mixed balanced) | Task execution goodput across regimes | Capability Coverage (CCS), $N_{\text{reload}}$, $t_{\text{paging}}$, Scheduler regret $\Delta_{\text{oracle}} = \frac{\text{Cost}_{\text{sched}} - \text{Cost}_{\text{oracle}}}{\text{Cost}_{\text{oracle}}}$ | Two-sided paired permutation tests with Holm-Bonferroni correction | ModelVM maintains highest goodput across all regimes; $\Delta_{\text{oracle}} \le 12\%$ across all workloads | ModelVM triggers OOM or achieves lower goodput than greedy heuristics on $>1$ distribution |

---

## 3. Experimental Control Specifications

### 3.1 Token-Budget Control (Protocol for EXP-H1 & EXP-R2)
* **Maximum Context Window ($W_{\text{in}}$):** $4,096$ tokens across all model invocations.
* **Maximum Generation Ceiling ($T_{\text{gen}}$):** $1,024$ tokens per stage.
* **Decoding Parameters:** Temperature $T = 0.0$ (greedy argmax), Top-$p = 1.0$, Repetition penalty $= 1.0$.
* **Raw Text Handoff Control:** Output text from previous stage $s_{t-1}$ is prepended to the system prompt of stage $s_t$. If accumulated text exceeds $W_{\text{in}} - T_{\text{gen}}$, a standard FIFO sliding window truncates early tokens.
* **CSP Handoff Control:** State packet $\mathcal{S}_{t-1}$ is serialized into structured, typed schema format within the prompt prefix. Token count of the serialization is recorded independently to evaluate compression efficiency.

### 3.2 Hierarchical Memory Tracking (Protocol for EXP-H2, EXP-R1, EXP-H4)
* **Tier 1 (Disk / Storage):** Serialized GGUF/Safetensors on NVMe SSD ($52.7$\,GB catalog).
* **Tier 2 (Host CPU RAM):** Measured process RSS via `/proc/[pid]/statm` and OS counters (CPU buffers, tokenizers, runtime).
* **Tier 3 (Accelerator GPU VRAM):** Measured allocated VRAM via NVML ($M_{\text{VRAM}} = M_{\text{weights}} + M_{\text{workspace}} + M_{\text{KV}}$).
* **Budget Invariant:** The runtime guarantees that $\sum_{m \in \mathcal{M}_{\text{resident}}} \text{RAM}(m) \le \mathcal{B}_{\text{RAM}}$ is enforced at all times.

### 3.3 Baseline Specification Continuum
* **$B_0$ (Static Monolith):** Single 8B generalist (`general-reasoner`, $7.1$\,GB RAM) resident in memory; no paging, no state transfer.
* **$B_{\text{static}}$ (Static Specialist Ensemble):** Top-2 specialists fitting within $8.0$\,GB budget simultaneously (`mathematics-expert` $2.4$\,GB + `coding-expert` $3.0$\,GB = $5.4$\,GB RAM); routes only between resident models; stages requiring other domains fall back to resident models.
* **$B_1$ (Unconstrained Specialist Router):** Selects optimal specialist for every stage; memory budget is set to $\infty$ (oracle routing upper bound, no residency limits).
* **$B_2$ (Router + Raw Text + Reactive LRU):** Dynamic loading under $8.0$\,GB budget; reactive LRU eviction; raw text concatenation handoff.
* **$B_3$ (Router + CSP + Unconstrained):** Specialist routing with CSP state virtualization; memory budget set to $\infty$ (isolates pure CSP contribution without paging overhead).
* **$B_4$ (Router + CSP + Reactive LRU):** Dynamic loading under $8.0$\,GB budget; reactive LRU eviction; typed CSP state handoff.
* **$B_5$ (Full ModelVM):** Dynamic loading under $8.0$\,GB budget; predictive working set $W(t, k)$ + eviction shielding; multi-objective scheduling; typed CSP state handoff.
* **$B_{\text{oracle}}$ (Offline Oracle Scheduler):** Prescient scheduler with perfect advance knowledge of all pipeline stage requirements, choosing optimal model sequence to minimize cold loads.
