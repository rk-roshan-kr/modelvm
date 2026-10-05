# ModelVM: Frozen Scientific Claim Sheet (Step 0 — Audited)

**Document Status:** FROZEN — Immutable scientific contract across all paper sections.  
**System Under Test:** ModelVM (Resource-Aware Runtime for Heterogeneous Open-Weight Language Models)

---

## 1. Central Research Question

> **Can heterogeneous open-weight language models be treated as pageable computational resources while preserving task state and improving quality–resource tradeoffs under constrained hardware?**

---

## 2. Core Hypotheses Decomposition

### Hypothesis 1 (H1 — Semantic State Virtualization / CSP)
> **H1:** A model-neutral, typed intermediate state representation ($\mathcal{S}_t$) preserves domain facts, arithmetic precision, and procedural deliverables across transitions between heterogeneous specialist models significantly better than raw conversational text handoffs under identical context limits ($W_{\text{in}} = 4,096$), generation budgets ($T_{\text{gen}} = 1,024$), and runtime memory budgets ($\mathcal{B}_{\text{RAM}} = 8.0\,\text{GB}$).
* **Independent Variable:** State handoff mechanism (Typed $\text{CSP}$ vs. Unstructured raw text concatenation).
* **Controlled Variables:** Model sequence, prompt instructions, context window limits ($4,096$ tokens), generation ceiling ($1,024$ tokens), decoding parameters ($T=0.0$, greedy), runtime memory budget ($8.0\,\text{GB}$).
* **Primary Metrics:** Factual retention ratio ($R_{\text{facts}}$), verified calculation correctness ($R_{\text{calcs}}$ via AST check), cumulative drift error ($D_{\text{drift}}$).
* **Failure Criterion:** If $R_{\text{facts}}(\text{CSP}) \le R_{\text{facts}}(\text{Raw Text})$ or $R_{\text{calcs}}(\text{CSP}) \le R_{\text{calcs}}(\text{Raw Text})$ across matched trials ($p \ge 0.05$).

---

### Hypothesis 2 (H2 — Predictive Model Residency / Working Set)
> **H2:** Anticipating model requirements via stage-level working-set lookahead ($W(t, k)$) coupled with cost-aware eviction shielding and opportunistic prefetching significantly reduces cold-load I/O stalls and memory thrashing compared to reactive, recency-based eviction policies (LRU/LFU).
* **Independent Variable:** Residency management policy (Predictive $W(t, k)$ vs. Reactive LRU vs. Greedy unconstrained).
* **Controlled Variables:** State representation (held constant with CSP), task capability sequence, storage transfer rate, runtime memory budget $\mathcal{B}_{\text{RAM}}$.
* **Primary Metrics:** Total cold-load latency ($t_{\text{paging}}$), cache hit rate ($H_{\text{cache}}$), eviction count ($N_{\text{evict}}$), reload frequency ($N_{\text{reload}}$).
* **Failure Criterion:** If $t_{\text{paging}}(\text{Predictive } W(t, k)) \ge t_{\text{paging}}(\text{LRU})$ or $N_{\text{reload}}(\text{Predictive } W(t, k)) \ge N_{\text{reload}}(\text{LRU})$ across matched trials ($p \ge 0.05$).

---

### Hypothesis 3 (H3 — Resource-Aware Cognitive Scheduling)
> **H3:** A joint multi-objective scoring function balancing empirical capability fitness, memory footprint, load latency, energy factor, eviction penalty, and future lookahead utility produces superior model selections over greedy capability-only selection and memory-aware greedy selection, approaching offline oracle bounds under constrained runtime memory.
* **Independent Variable:** Model selection policy (Multi-Objective Score with empirical profiling vs. Greedy Capability vs. Memory-Aware Greedy vs. Offline Oracle).
* **Controlled Variables:** Model catalog, domain capabilities, runtime memory budget ($8.0\,\text{GB}$).
* **Primary Metrics:** Task execution goodput, out-of-memory avoidance rate, capability coverage score (CCS), scheduler gap relative to offline oracle ($\Delta_{\text{oracle}}$).
* **Failure Criterion:** If ModelVM scheduling goodput or CCS does not exceed greedy capability selection ($p \ge 0.05$).

---

### Hypothesis 4 (H4 — Integrated Pareto Frontier)
> **H4:** The integration of Semantic State Virtualization, Predictive Working Set Residency, and Multi-Objective Scheduling enables ModelVM to establish a superior Quality–Memory–Latency Pareto frontier than monolithic models ($B_0$), static specialist ensembles ($B_{\text{static}}$), or reactive paging frameworks ($B_2, B_4$).
* **Comparison Systems:** Monolithic generalist ($B_0$), Static specialist ensemble ($B_{\text{static}}$), Unconstrained specialist router ($B_1$), Router + Raw Text + LRU ($B_2$), Router + CSP + LRU ($B_4$), Full ModelVM ($B_5$).
* **Primary Metrics:** 2D/3D Pareto optimality across Quality ($Q$), Peak Memory ($M_{\text{peak}}$), and Total Latency ($L$).
* **Failure Criterion:** If ModelVM is Pareto-dominated by any physically deployable baseline ($B_0, B_{\text{static}}, B_2, B_4$).

---

## 3. Disallowed Claims & Epistemic Boundaries

1. **No Universal Bayesian Claims:** Evidence aggregation is strictly designated as an *epistemic diversity-discounted heuristic* ($w_{\text{source}} = 0.65$). It does not claim formal Bayesian independence.
2. **Runtime Memory Budget vs. Physical Capacity:** The $8.0\,\text{GB}$ limit is explicitly defined as a *runtime resident memory budget* enforced on model execution, not the physical RAM ceiling of the host system.
3. **Statistical Uncertainty on Factorial Effects:** Reported factorial effect estimates ($\Delta_{\text{CSP}}, \Delta_{\text{WS}}, \Delta_{\text{Sched}}$) are calculated across replicated trials and reported with empirical bootstrap 95% confidence intervals $[q_{0.025}, q_{0.975}]$, rather than single-run scalar points.
4. **Hierarchical Memory Separation:** Memory tracking strictly separates secondary storage, host CPU RAM (RSS), and accelerator VRAM (weights, workspace, KV cache).
