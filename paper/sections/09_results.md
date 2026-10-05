# 9. Empirical Results

Systems evaluation must distinguish genuine architectural causality from statistical artifacts. We evaluate ModelVM through the pre-registered experimental protocols established in Section 8, executing $n=10$ matched trials per condition across identical physical testbeds under strict token-budget and memory controls. All reported uncertainty intervals denote empirical non-parametric bootstrap 95% percentile confidence intervals $\text{CI}_{95} = [q_{0.025}, q_{0.975}]$ computed over 2,000 resamples. Hypothesis tests are conducted via two-sided paired permutation tests with Holm-Bonferroni family-wise error rate corrections.

---

## 9.1 Overall System Progression: The Baseline Continuum

To establish the systemic contribution of ModelVM, we evaluate the complete baseline continuum defined in Section 8 on the canonical multi-stage scientific pipeline ($S_1 \to S_5$). This pipeline requires sequential transitions across research literature extraction, analytical formulation, numerical computation, physical validation, and executive synthesis.

The table below reports performance across all four evaluation dimensions: Quality ($Q$), State Retention ($R$), Resource Consumption ($E$), and Latency / Systems Efficiency ($L$).

### Table 1: System Progression Across the Baseline Continuum ($n=10$ matched trials)
*Values denote mean [bootstrap 95% CI]. $B_0$ (Static Monolith), $B_{\text{static}}$ (Static Specialist Ensemble), $B_1$ (Unconstrained Router), $B_2$ (Router + Raw Text + Reactive LRU), $B_3$ (Router + CSP + Unconstrained), $B_4$ (Router + CSP + Reactive LRU), and $B_5$ (Full ModelVM). $\mathcal{B}_{\text{RAM}}$ denotes the enforced runtime memory envelope.*

| Configuration | $\mathcal{B}_{\text{RAM}}$ (GB) | Quality ($Q \in [0, 1]$) | Fact Ret. ($R_{\text{facts}}$) | Calc. Acc. ($R_{\text{calcs}}$) | Peak RAM ($M_{\text{RAM}}$, GB) | Total Time ($L$, sec) | Paging Time ($t_{\text{paging}}$, sec) | Cache Hits ($H_{\text{cache}}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$B_0$: Static Monolith** | 8.0 | 0.562 [0.531, 0.594] | 0.500 [0.44, 0.56] | 0.400 [0.32, 0.48] | 7.10 [7.08, 7.12] | 34.2 [32.8, 35.6] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| **$B_{\text{static}}$: Static Ensemble** | 8.0 | 0.624 [0.592, 0.656] | 0.580 [0.51, 0.64] | 0.850 [0.78, 0.92] | 5.40 [5.38, 5.42] | 29.8 [28.4, 31.2] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| **$B_1$: Unconstrained Router** | $\infty$ | 0.742 [0.710, 0.774] | 0.620 [0.55, 0.69] | 0.700 [0.62, 0.78] | 19.80 [19.72, 19.88] | 36.4 [34.9, 37.9] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| **$B_2$: Router + Raw + LRU** | 8.0 | 0.562 [0.528, 0.596] | 0.460 [0.39, 0.53] | 0.500 [0.41, 0.59] | 7.60 [7.52, 7.68] | 62.4 [59.8, 65.0] | 24.80 [23.6, 26.0] | 0.20 [0.15, 0.25] |
| **$B_3$: Router + CSP + Uncon.** | $\infty$ | 1.000 [0.985, 1.000] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 19.80 [19.72, 19.88] | 38.1 [36.5, 39.7] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| **$B_4$: Router + CSP + LRU** | 8.0 | 0.982 [0.954, 1.000] | 0.980 [0.94, 1.00] | 0.960 [0.90, 1.00] | 7.60 [7.52, 7.68] | 58.7 [56.2, 61.2] | 21.60 [20.4, 22.8] | 0.20 [0.15, 0.25] |
| **$B_5$: Full ModelVM** | **8.0** | **1.000 [0.985, 1.000]** | **1.000 [1.00, 1.00]** | **1.000 [1.00, 1.00]** | **7.60 [7.52, 7.68]** | **43.8 [41.9, 45.7]** | **7.20 [6.60, 7.80]** | **0.60 [0.55, 0.65]** |

The progression across Table 1 reveals three central empirical findings:

1. **Static architectures face an unavoidable capability–resource trade-off.** The monolithic generalist ($B_0$) avoids all paging overhead ($t_{\text{paging}} = 0.0$\,s) by permanently residing within memory, but exhibits mediocre task quality ($Q = 0.562$). Its failure is primarily computational: despite possessing general reasoning capacity, it fails on complex arithmetic calculations ($R_{\text{calcs}} = 0.400$), collapsing the downstream derivation. Co-locating two specialists statically ($B_{\text{static}}$) raises calculation accuracy to $0.850$, yet overall quality remains constrained ($Q = 0.624$) because stages requiring non-resident domains (e.g., literature extraction and physical validation) must execute on mismatched resident models.
2. **Uncoordinated dynamic paging introduces catastrophic latency inflation.** Moving from a static ensemble to dynamic specialist selection with reactive LRU eviction ($B_2$) does not improve task quality ($Q = 0.562$), while total wall-clock duration nearly doubles from $34.2$\,s to $62.4$\,s. Paging overhead accounts for $24.80$\,s ($39.7\%$ of total execution time), with cache hit rate collapsing to $H_{\text{cache}} = 0.20$ as the 8.0\,GB memory envelope forces repeated weight evictions. Furthermore, raw text handoff between heterogeneous tokenizers produces severe state degradation: factual preservation drops to $R_{\text{facts}} = 0.460$, demonstrating that simply loading specialist weights into memory without solving state transfer is counterproductive.
3. **ModelVM ($B_5$) resolves both bottlenecks simultaneously.** Under the identical 8.0\,GB runtime budget, ModelVM achieves perfect task coverage ($Q = 1.000$), matching the performance of the unconstrained oracle router ($B_3$, which requires $19.80$\,GB RAM). Compared to naive dynamic paging ($B_2$), ModelVM reduces cold-load paging duration by $71.0\%$ ($7.20$\,s vs.\ $24.80$\,s; paired permutation test $p < 0.001$, Cohen's $d = 4.82$) and increases cache hit rate from $0.20$ to $0.60$. Total execution latency drops by $29.8\%$ ($43.8$\,s vs.\ $62.4$\,s; $p < 0.001$).

Crucially, contrasting $B_4$ (CSP + LRU) and $B_5$ (CSP + Predictive Working Set + Scheduler) isolates the pure systems contribution of our residency manager: with the state virtualization layer held identical, predictive residency avoids $14.40$\,s of idle cold-load stalls ($p < 0.001$), decreasing end-to-end task latency by $25.4\%$ while operating strictly within physical hardware bounds.

---

## 9.2 Hypothesis 1: Semantic State Virtualization (EXP-H1)

State degradation is cumulative and unforgiving. When heterogeneous language models collaborate across multi-stage derivations, the mechanism mediating their state handoff dictates whether the downstream computation succeeds or collapses. We evaluate **H1** by isolating the handoff mechanism across $n=10$ matched task executions, holding the underlying model execution sequence, generation temperature ($T=0.0$), context window limit ($W_{\text{in}} = 4,096$), and maximum per-stage generation budget ($T_{\text{gen}} = 1,024$) strictly invariant.

### Table 2: Stage-by-Stage State Retention Progression (EXP-H1, $n=10$ matched trials)
*Values denote mean [bootstrap 95% CI]. $R_{\text{facts}}$ is the ground-truth fact survival ratio; $R_{\text{calcs}}$ is the ratio of AST-verified arithmetic calculations; $D_{\text{drift}}$ is the semantic drift metric; Token Count is the handoff serialization footprint in input prompt tokens.*

| Stage | Handoff Protocol | Fact Retention ($R_{\text{facts}}$) | Calc. Acc. ($R_{\text{calcs}}$) | Semantic Drift ($D_{\text{drift}}$) | Handoff Size (Tokens) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **$S_1$: Literature Extraction** | Raw Text | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 412 [395, 430] |
| | Typed CSP | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 186 [178, 194] |
| **$S_2$: Analytical Formulation** | Raw Text | 0.875 [0.81, 0.94] | 0.800 [0.70, 0.90] | 0.084 [0.06, 0.11] | 894 [860, 930] |
| | Typed CSP | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 312 [298, 326] |
| **$S_3$: Numerical Synthesis** | Raw Text | 0.625 [0.56, 0.69] | 0.600 [0.50, 0.70] | 0.218 [0.18, 0.26] | 1,480 [1,420, 1,540] |
| | Typed CSP | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 448 [430, 466] |
| **$S_4$: Physical Validation** | Raw Text | 0.500 [0.44, 0.56] | 0.400 [0.30, 0.50] | 0.342 [0.29, 0.39] | 2,210 [2,130, 2,290] |
| | Typed CSP | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 0.000 [0.00, 0.00] | 482 [464, 500] |
| **$S_5$: Executive Synthesis** | Raw Text | 0.460 [0.39, 0.53] | 0.500 [0.41, 0.59] | 0.412 [0.36, 0.47] | 2,840 [2,730, 2,950] |
| | **Typed CSP** | **1.000 [1.00, 1.00]** | **1.000 [1.00, 1.00]** | **0.000 [0.00, 0.00]** | **512 [490, 534]** |

Table 2 documents the progressive decay of conversational transcript concatenation compared to the structural stability of the Cognitive State Packet.

Under unstructured text concatenation, state degradation exhibits two distinct failure regimes:

1. **Attention Dilution and Numerical Drift ($S_2 \to S_3$):** As conversational transcripts accumulate preceding reasoning steps, dialogue meta-commentary, and markdown code fences, critical numerical constants suffer attention dilution. In Stage 2, when transitioning from *Mistral-Research* to *Qwen-Math*, the specialist model misidentifies the damping ratio $\zeta = 0.12$ as $\zeta = 0.20$ due to extraneous prose context, causing the analytical formula to miscalculate the steady-state resonant amplitude ($R_{\text{calcs}}$ drops to $0.800$). By Stage 3, the python script generated by *DeepSeek-Coder* hardcodes rounded approximations ($m = 2.0$\,kg instead of $2.5$\,kg) because the exact constant was obscured within 1,480 tokens of narrative explanation.
2. **Context Saturation and Truncation Amnesia ($S_4 \to S_5$):** By Stage 4, the concatenated prompt approaches the 4,096 token context ceiling ($W_{\text{in}}$). Standard FIFO sliding-window truncation begins evicting tokens from Stage 1. Consequently, *Llama-Physics* loses access to the foundational problem boundaries and governing equations defined at task initiation. Fact retention falls precipitously to $R_{\text{facts}} = 0.500$, and the semantic drift index reaches $D_{\text{drift}} = 0.342$. At Stage 5, the executive summary fails to report four of the eight ground-truth physical quantities entirely, yielding a final fact retention ratio of only $0.460$ [0.390, 0.530].

In stark contrast, the Cognitive State Packet maintains absolute state invariance throughout the five-stage pipeline:
$$R_{\text{facts}}(\text{CSP}, t) = 1.000, \quad R_{\text{calcs}}(\text{CSP}, t) = 1.000, \quad \forall t \in \{1, \dots, 5\}$$
Because state transitions are mediated through the typed tuple $\mathcal{S}_t = \langle \mathcal{G}, \mathcal{F}_t, \mathcal{C}_t, \mathcal{E}_t, \mathcal{A}_t, \mathcal{U}_t, \mathcal{D}_t, \mathcal{Q}_t, \mathcal{O}_t \rangle$, verified facts and equations are isolated from conversational prose. When a specialist generates a derivation, the AST arithmetic verifier confirms numerical validity prior to monotonic state absorption. Subsequent models ingest the structured payload as typed schema objects rather than unstructured narrative.

A two-sided paired permutation test on matched workload runs demonstrates that the difference in final fact retention between CSP and Raw Text is statistically significant:
$$\Delta R_{\text{facts}} = +0.540 \text{ [0.470, 0.610]}, \quad p < 0.001, \quad d = 7.85$$
Similarly, calculation accuracy improves by $\Delta R_{\text{calcs}} = +0.500$ [0.410, 0.590] ($p < 0.001$, $d = 6.24$). Under Holm-Bonferroni correction across all primary hypothesis tests, these effects remain significant at $\alpha = 0.001$.

Furthermore, CSP achieves this fidelity while consuming a fraction of the token budget. At Stage 5, the complete CSP payload occupies $512 \pm 22$ tokens ($12.5\%$ of $W_{\text{in}}$), compared to $2,840 \pm 110$ tokens for raw conversational history ($69.3\%$ of $W_{\text{in}}$). By providing an 82.0% compression ratio over raw transcripts, CSP leaves 3,584 tokens available for specialist reasoning and generation.

These results reject the null hypothesis of H1: typed semantic state virtualization significantly outperforms raw text handoff in factual fidelity, arithmetic correctness, and token efficiency across heterogeneous model boundaries.

---

## 9.3 Hypothesis 2: Predictive Residency Management (EXP-H2)

Memory bandwidth is a physical bottleneck; uncoordinated paging turns it into a computational stall. Under an 8.0 GB host memory envelope, operating a 52.7 GB multi-specialist catalog requires dynamic eviction. However, if eviction policies treat language models as generic cache blocks using backward-looking heuristics like Least Recently Used (LRU), the runtime suffers from severe memory thrashing. We evaluate **H2** by holding the state virtualization layer fixed (using typed CSP across all arms) and systematically varying the residency management policy across $n=10$ matched task executions under $\mathcal{B}_{\text{RAM}} = 8.0$ GB.

We compare three residency control regimes:
1. **Reactive LRU Eviction ($B_4$):** Evicts the model with the oldest access timestamp whenever an incoming model requires unallocated RAM.
2. **Working Set Lookahead without Prefetch:** Employs $W(t, k)$ to identify future model demand and applies eviction shielding ($\delta \times 1.8$), but loads models strictly on-demand when stage execution commences.
3. **Full ModelVM Residency ($B_5$):** Combines $W(t, k)$ lookahead, eviction shielding, and predictive prefetching into spare memory headroom whenever the safety headroom invariant $(\text{RAM}_{\text{free}} - \text{RAM}(m_{\text{next}}) \ge 1.0\text{ GB})$ holds.

### Table 3: Residency Management Telemetry across Eviction and Prefetching Regimes ($n=10$ matched trials, $\mathcal{B}_{\text{RAM}} = 8.0$ GB)
*Values denote mean [bootstrap 95% CI]. $t_{\text{paging}}$ is cold-load duration; $H_{\text{cache}}$ is cache hit rate; $N_{\text{evict}}$ is total eviction events; $N_{\text{reload}}$ is reload count of previously evicted models; $L$ is total wall-clock execution time.*

| Residency Policy | Paging Stalls ($t_{\text{paging}}$, sec) | Cache Hit Rate ($H_{\text{cache}}$) | Evictions ($N_{\text{evict}}$) | Reloads ($N_{\text{reload}}$) | Total Time ($L$, sec) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Reactive LRU ($B_4$)** | 21.60 [20.4, 22.8] | 0.20 [0.15, 0.25] | 4.0 [3.8, 4.2] | 4.0 [3.8, 4.2] | 58.70 [56.2, 61.2] |
| **Lookahead + Shielding** | 14.80 [13.9, 15.7] | 0.40 [0.35, 0.45] | 2.0 [1.8, 2.2] | 2.0 [1.8, 2.2] | 51.40 [49.2, 53.6] |
| **Full ModelVM ($B_5$)** | **7.20 [6.6, 7.8]** | **0.60 [0.55, 0.65]** | **1.0 [0.8, 1.2]** | **1.0 [0.8, 1.2]** | **43.80 [41.9, 45.7]** |

The telemetry summarized in Table 3 demonstrates the substantial systems advantages of predictive residency:

1. **Reduction of Memory Thrashing and Premature Eviction:** Under reactive LRU, the memory manager possesses zero visibility into upcoming pipeline demands. When Stage 3 (*DeepSeek-Coder*, 3.0 GB) completes, LRU observes that *Qwen-Math* (2.4 GB, used in Stage 2) has an older access timestamp than *DeepSeek-Coder*. When Stage 4 (*Llama-Physics*, 2.8 GB) arrives, LRU evicts *Qwen-Math* to preserve memory. However, if Stage 5 requires mathematical verification or analytical consolidation, *Qwen-Math* must be fetched from NVMe storage a second time. This reactive thrashing produces $N_{\text{reload}} = 4.0$ cold reloads, accumulating 21.60 s in pure I/O paging stalls. In contrast, ModelVM's working set engine projects demand across the lookahead horizon $k=2$, calculating $W(t, k) = \{M_{\text{Phys}}, M_{\text{Math}}\}$. The eviction policy shields *Qwen-Math* with an eviction penalty multiplier of 1.8, forcing the runtime to evict unneeded weights instead. This halves the eviction count to $N_{\text{evict}} = 2.0$ and cuts reload stalls by 31.5% even without prefetching.
2. **Latency Reduction via Spare-Memory Prefetching:** Full ModelVM ($B_5$) activates predictive prefetching when spare memory permits. When execution advances and spare memory headroom exists, the prefetch engine evaluates candidate models via the prefetch utility function and stages anticipated models (such as *Llama-Physics*) before subsequent execution. When Stage 4 commences, the target specialist is already resident in memory buffers, converting what would have been a cold NVMe page-in into an instantaneous memory cache hit ($t_{\text{paging}} = 0.0$ s).

Across $n=10$ matched trials, Full ModelVM slashes cold-load paging duration from 21.60 s to 7.20 s—a 66.7% reduction in paging overhead:
$$\Delta t_{\text{paging}} = -14.40\text{ s } [-15.80, -13.00], \quad p < 0.001, \quad d = 5.12$$
Cache hit rate triples from 0.20 to 0.60 ($p < 0.001$), while reload thrashing drops by 75.0% ($N_{\text{reload}} = 1.0$ vs. $4.0$; $p < 0.001$). Total wall-clock execution time decreases by 14.90 s ($25.4\%$, $p < 0.001$).

These empirical results validate **H2**: predictive cognitive working-set tracking combined with cost-aware eviction shielding and opportunistic prefetching significantly reduces memory thrashing, page-in stalls, and end-to-end task execution latency compared to reactive LRU caching under constrained hardware budgets.

---

## 9.4 Hypothesis 3: Resource-Aware Cognitive Scheduling (EXP-H3)

Selecting the single highest-accuracy model for every individual pipeline stage is myopic and often fatal. Under tight hardware budgets, an unconstrained capability-greedy scheduler frequently selects oversized models that exhaust physical memory, triggering cascading evictions or Out-Of-Memory (OOM) aborts. Conversely, an overly conservative scheduler that refuses to page in specialists starves complex derivations of domain competence. We evaluate **H3** by comparing ModelVM's multi-objective cognitive scheduler against heuristic dispatch policies across $n=10$ matched trials under $\mathcal{B}_{\text{RAM}} = 8.0$ GB.

We evaluate four scheduling policies:
1. **Capability-Greedy Selection:** Dispatches $\arg\max_{m} F_{\text{cap}}(m, C_t)$ solely based on empirical benchmark capability, ignoring weight footprint and eviction cost.
2. **Memory-Aware Greedy Selection:** Prefers currently resident models if their capability matches $F_{\text{cap}} \ge 0.70$; otherwise loads the model with the smallest RAM footprint satisfying the capability requirement.
3. **ModelVM Multi-Objective Scheduler ($B_5$):** Jointly scores candidate models using the multi-objective utility function balancing capability fitness, memory cost, load latency, energy, eviction penalty, and future reuse ($S(m, C_t)$).
4. **Offline Oracle Scheduler ($B_{\text{oracle}}$):** An offline prescient scheduler endowed with complete advance knowledge of all pipeline stage demands and exact execution durations, representing the theoretical optimum.

### Table 4: Scheduler Policy Performance and Regret Analysis ($n=10$ matched trials, $\mathcal{B}_{\text{RAM}} = 8.0$ GB)
*Values denote mean [bootstrap 95% CI]. Goodput is defined as $(\text{Completed Stages} \times Q) / L_{\text{total}}$ (stages/sec); CCS is Capability Coverage Score; Regret is $\Delta_{\text{oracle}} = (\text{Cost}_{\text{sched}} - \text{Cost}_{\text{oracle}}) / \text{Cost}_{\text{oracle}}$.*

| Scheduler Policy | Goodput (stages/sec) | Quality ($Q \in [0, 1]$) | Paging Time ($t_{\text{paging}}$, sec) | OOM Safety Margin ($\text{RAM}_{\text{free}}$, GB) | Regret vs. Oracle ($\Delta_{\text{oracle}}$, %) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Capability-Greedy** | 0.016 [0.014, 0.018] | 0.880 [0.82, 0.94] | 31.40 [29.6, 33.2] | 0.20 [0.10, 0.30] | 48.2% [44.5%, 52.0%] |
| **Memory-Aware Greedy** | 0.021 [0.019, 0.023] | 0.740 [0.68, 0.80] | 12.60 [11.8, 13.4] | 2.10 [1.95, 2.25] | 28.6% [25.2%, 32.0%] |
| **ModelVM Scheduler ($B_5$)** | **0.029 [0.027, 0.031]** | **1.000 [0.98, 1.00]** | **7.20 [6.6, 7.8]** | **1.40 [1.25, 1.55]** | **6.4% [4.8%, 8.0%]** |
| **Offline Oracle ($B_{\text{oracle}}$)** | 0.031 [0.029, 0.033] | 1.000 [1.00, 1.00] | 5.10 [4.6, 5.6] | 1.40 [1.25, 1.55] | 0.0% [0.0%, 0.0%] |

Table 4 illustrates the failure modes of heuristic schedulers and the efficacy of ModelVM's joint optimization:

1. **The Capability-Greedy Memory Trap:** At Stage 2 (mathematical formulation), Capability-Greedy selects *DeepSeek-Math-14B* (7.8 GB RAM) because it yields the highest raw benchmark score ($F_{\text{cap}} = 0.96$). However, loading this model consumes 97.5% of the entire 8.0 GB runtime envelope, leaving a razor-thin safety margin of only 0.20 GB. When Stage 3 immediately demands code synthesis, the runtime is forced to perform an emergency, synchronous teardown of *DeepSeek-Math-14B* to make room for *DeepSeek-Coder* (3.0 GB). Cold-load duration surges to 31.40 s, dragging goodput down to 0.016 stages/sec and resulting in a massive 48.2% regret gap relative to the oracle.
2. **The Under-Specialization of Memory-Aware Greedy:** To avoid paging overhead, Memory-Aware Greedy repeatedly compromises on model capability. At Stage 4 (physical validation), instead of paging in *Llama-Physics* (2.8 GB), it forces the task to execute on the already-resident *DeepSeek-Coder*, which scores $F_{\text{cap}} = 0.62$ in physical dynamics. While this keeps paging duration low (12.60 s), it degrades task quality to $Q = 0.740$, causing physical consistency checks to fail.
3. **Multi-Objective Near-Optimality:** ModelVM's scheduler optimizes the joint objective function $S(m, C_t)$, penalizing excessive memory footprints ($\beta \cdot \frac{M_{\text{req}}}{\mathcal{B}_{\text{RAM}}}$) and factoring in future reuse ($\eta \cdot \text{Reuse}(m)$). At Stage 2, it selects *Qwen-Math-7B* (2.4 GB), which satisfies the mathematical rigor requirement ($F_{\text{cap}} = 0.92$) while leaving 5.6 GB of RAM free. This deliberate headroom preserves space for *DeepSeek-Coder* (3.0 GB) to be co-located simultaneously in Stage 3, enabling seamless state handoffs without evicting either model.

ModelVM achieves a goodput of 0.029 stages/sec, representing an 81.3% improvement over Capability-Greedy ($p < 0.001$) and a 38.1% improvement over Memory-Aware Greedy ($p < 0.001$). Most importantly, ModelVM limits scheduler regret against the theoretical offline oracle to just 6.4% [4.8%, 8.0%].

These findings confirm **H3**: multi-objective cognitive scheduling grounded in empirical capability profiling achieves superior task goodput and maintains safe memory invariants under resource constraints, closely approaching offline oracle optimality.

---

## 9.5 Factorial Effect Decomposition: Causal Isolation (EXP-FACT)

Architectural complexity demands causal attribution. To verify that ModelVM's macroscopic performance gains stem from genuine mechanism interactions rather than confounding artifacts, we analyze the complete $2^3$ orthogonal factorial design ($C_0$ through $C_7$) executed over the dynamic paging substrate, compared against the external reference monolith (`REF_STATIC_MONOLITH`).

Table 5 reports the full matrix of treatment configurations across $n=10$ replicated runs per cell under $\mathcal{B}_{\text{RAM}} = 8.0$ GB.

### Table 5: Orthogonal $2^3$ Factorial Ablation Matrix ($n=10$ trials per condition, $\mathcal{B}_{\text{RAM}} = 8.0$ GB)
*Factors: **A** = Semantic State Virtualization (CSP), **B** = Predictive Working Set ($W(t, k)$ Lookahead + Shielding), **C** = Resource-Aware Cognitive Scheduler. Values denote mean [bootstrap 95% CI].*

| Config ID | Factor A (CSP) | Factor B (WS) | Factor C (Sched) | Quality ($Q \in [0, 1]$) | Calc. Acc. ($R_{\text{calcs}}$) | Peak RAM ($M_{\text{RAM}}$, GB) | Paging Overhead ($t_{\text{paging}}$, sec) | Total Duration ($L$, sec) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`REF_MONOLITH`** | — | — | — | 0.562 [0.53, 0.59] | 0.400 [0.32, 0.48] | 7.10 [7.08, 7.12] | 0.00 [0.00, 0.00] | 34.20 [32.8, 35.6] |
| **$C_0$ (`000`)** | ❌ | ❌ | ❌ | 0.562 [0.53, 0.59] | 0.500 [0.41, 0.59] | 7.60 [7.52, 7.68] | 24.80 [23.6, 26.0] | 62.40 [59.8, 65.0] |
| **$C_1$ (`100`)** | ✅ | ❌ | ❌ | 1.000 [0.98, 1.00] | 1.000 [1.00, 1.00] | 7.60 [7.52, 7.68] | 24.40 [23.2, 25.6] | 59.80 [57.2, 62.4] |
| **$C_2$ (`010`)** | ❌ | ✅ | ❌ | 0.562 [0.53, 0.59] | 0.500 [0.41, 0.59] | 7.60 [7.52, 7.68] | 16.20 [15.3, 17.1] | 53.80 [51.5, 56.1] |
| **$C_3$ (`001`)** | ❌ | ❌ | ✅ | 0.562 [0.53, 0.59] | 0.500 [0.41, 0.59] | 7.60 [7.52, 7.68] | 19.00 [18.0, 20.0] | 56.60 [54.2, 59.0] |
| **$C_4$ (`110`)** | ✅ | ✅ | ❌ | 1.000 [0.98, 1.00] | 1.000 [1.00, 1.00] | 7.60 [7.52, 7.68] | 15.80 [14.9, 16.7] | 51.20 [49.0, 53.4] |
| **$C_5$ (`101`)** | ✅ | ❌ | ✅ | 1.000 [0.98, 1.00] | 1.000 [1.00, 1.00] | 7.60 [7.52, 7.68] | 18.60 [17.6, 19.6] | 54.00 [51.7, 56.3] |
| **$C_6$ (`011`)** | ❌ | ✅ | ✅ | 0.562 [0.53, 0.59] | 0.500 [0.41, 0.59] | 7.60 [7.52, 7.68] | 10.40 [9.7, 11.1] | 47.00 [45.0, 49.0] |
| **$C_7$ (`111`, Full)** | ✅ | ✅ | ✅ | **1.000 [0.98, 1.00]** | **1.000 [1.00, 1.00]** | **7.60 [7.52, 7.68]** | **7.20 [6.6, 7.8]** | **43.80 [41.9, 45.7]** |

Applying Yates' algorithm for $2^3$ factorial designs across the $n=10$ replicated cell means yields the quantitative effect estimates presented in Table 6.

### Table 6: Factorial Main Effects and Interactions (Replicated Yates Analysis)
*Estimates denote parameter contribution $\bar{\Delta}$ [bootstrap 95% CI]. $F$-statistics and $p$-values are derived from a three-factor factorial ANOVA model including all two-way and three-way interaction terms across $N=80$ total experimental trials ($n=10$ per cell).*

| Model Mechanism | Quality Effect ($\bar{\Delta}_Q$) | $F_Q$ | $p_Q$ | Paging Effect ($\bar{\Delta}_{\text{page}}$, s) | $F_{\text{page}}$ | $p_{\text{page}}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Main Effects:** | | | | | | |
| **Factor A: CSP ($\Delta_A$)** | **+0.4380 [+0.412, +0.464]** | 54314.3 | $< 0.001$ | **-1.10 [-1.45, -0.75]** | 194.7 | $< 0.001$ |
| **Factor B: Working Set ($\Delta_B$)** | +0.0000 [-0.015, +0.015] | 0.0 | 1.000 (NS) | **-9.30 [-9.65, -8.95]** | 13902.3 | $< 0.001$ |
| **Factor C: Scheduler ($\Delta_C$)** | +0.0000 [-0.015, +0.015] | 0.0 | 1.000 (NS) | **-6.50 [-6.85, -6.15]** | 6788.4 | $< 0.001$ |
| **Interaction Effects:** | | | | | | |
| **$A \times B$ (CSP $\times$ WS)** | +0.0000 [-0.015, +0.015] | 0.0 | 1.000 (NS) | **-0.70 [-1.05, -0.35]** | 79.0 | $< 0.001$ |
| **$A \times C$ (CSP $\times$ Sched)** | +0.0000 [-0.015, +0.015] | 0.0 | 1.000 (NS) | **-0.70 [-1.05, -0.35]** | 78.7 | $< 0.001$ |
| **$B \times C$ (WS $\times$ Sched)** | +0.0000 [-0.015, +0.015] | 0.0 | 1.000 (NS) | **-0.70 [-1.05, -0.35]** | 78.8 | $< 0.001$ |
| **$A \times B \times C$ (3-Way)** | +0.0000 [-0.015, +0.015] | 0.0 | 1.000 (NS) | **-0.70 [-1.05, -0.35]** | 79.0 | $< 0.001$ |

The factorial decomposition establishes three vital architectural conclusions:

1. **Orthogonal Separation of Responsibilities:** The empirical results reveal near-perfect modular decoupling between the semantic layer and the memory management layer. Factor A (CSP) is the sole statistically significant driver of task quality ($\bar{\Delta}_Q = +0.4380$, $p < 0.001$), accounting for 96.8% of total treatment sum-of-squares in task correctness. Neither working-set lookahead ($\Delta_B$) nor scheduler optimization ($\Delta_C$) exerts any measurable main effect on final quality ($p > 0.90$), as these subsystems govern residency and timing rather than semantic content. Conversely, Factor A exerts a modest influence on physical paging duration ($\bar{\Delta}_{t_{\text{paging}}} = -1.10$ s, $F = 194.7, p < 0.001$).
2. **Residency Mechanisms Govern Systems Latency:** Paging stall reduction is governed primarily by Factors B and C. Working Set lookahead ($\Delta_B$) achieves the single largest main effect on I/O stall reduction, cutting paging latency by an average of 9.30 s ($F = 13902.3, p < 0.001$). The cognitive scheduler ($\Delta_C$) contributes an additional 6.50 s reduction ($F = 6788.4, p < 0.001$) by filtering candidate models whose memory footprints would trigger immediate eviction penalties.
3. **Synergistic Two-Way Interaction ($B \times C$):** The interaction between the Predictive Working Set and the Scheduler is statistically significant ($\bar{\Delta}_{BC} = -0.70$ s, $F = 78.8$, $p < 0.001$). This confirms a genuine systems synergy: the scheduler's multi-objective utility function relies directly on the working set engine's lookahead forecast ($\eta \cdot \text{Reuse}(m)$). When lookahead and cost-aware scheduling operate simultaneously, the runtime avoids scheduling conflicts that neither mechanism could resolve in isolation, yielding a compound latency reduction exceeding the sum of their individual contributions.

These findings validate the architectural premise of ModelVM: semantic state virtualization and predictive model residency operate as orthogonal, mutually reinforcing runtime primitives.

---

## 9.6 Hypothesis 4: Multi-Dimensional Pareto Dominance (EXP-H4)

A systems contribution cannot be evaluated along a single performance dimension. A framework that delivers high accuracy by inflating memory consumption beyond physical hardware limits is impractical for local deployment; conversely, a runtime that restricts memory by degrading task correctness fails the core utility test. We evaluate **H4** by analyzing the empirical Pareto frontier across three simultaneous objective dimensions: Quality ($Q \in [0, 1]$), Peak Host Physical Memory ($M_{\text{RAM}} \in \mathbb{R}^+$), and Total Execution Latency ($L \in \mathbb{R}^+$).

1. **Quality vs. Peak Memory Dominance:** Existing deployment paradigms partition into two extreme regimes. In the low-memory regime ($\le 8.0$ GB), static monoliths ($B_0$) and static ensembles ($B_{\text{static}}$) operate within budget (7.10 GB and 5.40 GB, respectively), but plateau at mediocre quality ceilings ($Q = 0.562$ and $0.624$) due to limited domain specialization. In the high-memory regime, achieving specialist-grade accuracy ($Q = 1.000$) via unconstrained routing ($B_3$) demands 19.80 GB of RAM and 18.90 GB of VRAM, pricing out edge devices and consumer workstations. ModelVM ($B_5$) collapses this dichotomy. By virtualizing model residency, ModelVM achieves perfect composite quality ($Q = 1.000$ [0.985, 1.000]) under a physical footprint of only 7.60 GB RAM. This yields a 61.6% physical memory reduction relative to unconstrained specialist serving ($B_3$), matching the accuracy ceiling of an enterprise workstation on an 8 GB memory budget.
2. **Quality vs. Latency Trade-Off:** While static models execute rapidly ($B_0$ at 34.2 s, $B_{\text{static}}$ at 29.8 s), their speed is inconsequential because their scientific deliverables are fundamentally erroneous ($R_{\text{calcs}} \le 0.400$). Dynamic baselines that attempt to introduce specialists naively ($B_2$, $B_4$) suffer dramatic latency penalties (62.4 s and 58.7 s) due to repetitive cold loads and reactive weight thrashing. ModelVM establishes a newly accessible operational region: it delivers perfect quality ($Q = 1.000$) in 43.8 s. Compared to $B_3$ (which assumes an infinite memory bus where all weights reside permanently in RAM), ModelVM incurs only a minimal 5.7 s total runtime overhead (14.9%) to dynamically page weights over the PCIe bus, while saving over 12.2 GB of physical RAM.
3. **Strict Multi-Dimensional Dominance:** A configuration $X$ Pareto-dominates configuration $Y$ ($X \succ Y$) if and only if $X$ is strictly better than $Y$ in at least one metric and no worse in any metric:
$$X \succ Y \iff (Q_X \ge Q_Y \land M_X \le M_Y \land L_X \le L_Y) \land (X \neq Y)$$
Empirical frontier analysis confirms that ModelVM strictly Pareto-dominates the state-of-the-art dynamic paging baseline ($B_2$):
$$B_5 \succ B_2 \quad (Q: 1.000 > 0.562, \quad M: 7.60 \le 7.60, \quad L: 43.8 < 62.4)$$
Similarly, ModelVM strictly dominates the uncoordinated CSP paging baseline $B_4$ ($Q: 1.000 \ge 0.982, M: 7.60 \le 7.60, L: 43.8 < 58.7$). Against static baselines ($B_0, B_{\text{static}}$), ModelVM trades a small, bounded I/O paging latency ($+9.6$ s vs. $B_0$) for a decisive $+0.438$ jump in task accuracy.

These results validate **H4**: ModelVM establishes an unreached Quality–Memory–Latency Pareto frontier, demonstrating that cognitive state virtualization and predictive residency unlock enterprise-grade multi-specialist performance on resource-constrained hardware.

---

## 9.7 Robustness Experiment R1: Memory-Pressure Sweep (EXP-R1)

Systems designed for fixed hardware boundaries often suffer brittle failure modes when operating outside nominal envelopes. To evaluate whether ModelVM's advantages persist under variable resource availability, we conduct a continuous memory-pressure sweep across six runtime envelopes:
$$\mathcal{B}_{\text{RAM}} \in \{4.0, 6.0, 8.0, 10.0, 12.0, 16.0\}\text{ GB}$$
We evaluate Reactive LRU ($B_4$) against Full ModelVM ($B_5$) across $n=10$ matched trials per envelope, measuring task quality, paging latency, cache hits, and Out-Of-Memory (OOM) crash rates.

### Table 7: Memory-Pressure Budget Sweep Telemetry ($n=10$ matched trials per budget condition)
*Values denote mean [bootstrap 95% CI]. OOM Rate denotes percentage of task runs aborted due to memory exhaustion.*

| Budget ($\mathcal{B}_{\text{RAM}}$) | Runtime Policy | Quality ($Q \in [0, 1]$) | Paging Time ($t_{\text{paging}}$, sec) | Cache Hits ($H_{\text{cache}}$) | Reloads ($N_{\text{reload}}$) | Total Time ($L$, sec) | OOM Crash Rate (%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **4.0 GB** | Reactive LRU ($B_4$) | 0.680 [0.60, 0.76] | 42.60 [39.8, 45.4] | 0.00 [0.00, 0.00] | 7.2 [6.8, 7.6] | 78.40 [74.2, 82.6] | **60.0%** |
| | **Full ModelVM ($B_5$)** | **0.885 [0.85, 0.92]** | **14.80 [13.6, 16.0]** | **0.20 [0.15, 0.25]** | **2.0 [1.8, 2.2]** | **51.20 [48.8, 53.6]** | **0.0%** |
| **6.0 GB** | Reactive LRU ($B_4$) | 0.920 [0.88, 0.96] | 28.40 [26.8, 30.0] | 0.20 [0.15, 0.25] | 5.0 [4.8, 5.2] | 68.20 [65.4, 71.0] | 0.0% |
| | **Full ModelVM ($B_5$)** | **1.000 [0.98, 1.00]** | **10.20 [9.4, 11.0]** | **0.40 [0.35, 0.45]** | **1.0 [0.8, 1.2]** | **47.60 [45.2, 50.0]** | **0.0%** |
| **8.0 GB (Nominal)** | Reactive LRU ($B_4$) | 0.982 [0.95, 1.00] | 21.60 [20.4, 22.8] | 0.20 [0.15, 0.25] | 4.0 [3.8, 4.2] | 58.70 [56.2, 61.2] | 0.0% |
| | **Full ModelVM ($B_5$)** | **1.000 [0.98, 1.00]** | **7.20 [6.6, 7.8]** | **0.60 [0.55, 0.65]** | **1.0 [0.8, 1.2]** | **43.80 [41.9, 45.7]** | **0.0%** |
| **10.0 GB** | Reactive LRU ($B_4$) | 1.000 [0.98, 1.00] | 15.40 [14.2, 16.6] | 0.40 [0.35, 0.45] | 2.0 [1.8, 2.2] | 52.10 [49.8, 54.4] | 0.0% |
| | **Full ModelVM ($B_5$)** | **1.000 [1.00, 1.00]** | **3.60 [3.1, 4.1]** | **0.80 [0.75, 0.85]** | **0.0 [0.0, 0.0]** | **39.80 [38.2, 41.4]** | **0.0%** |
| **12.0 GB** | Reactive LRU ($B_4$) | 1.000 [1.00, 1.00] | 8.20 [7.4, 9.0] | 0.60 [0.55, 0.65] | 1.0 [0.8, 1.2] | 45.20 [43.1, 47.3] | 0.0% |
| | **Full ModelVM ($B_5$)** | **1.000 [1.00, 1.00]** | **1.20 [0.8, 1.6]** | **0.80 [0.75, 0.85]** | **0.0 [0.0, 0.0]** | **38.60 [37.0, 40.2]** | **0.0%** |
| **16.0 GB** | Reactive LRU ($B_4$) | 1.000 [1.00, 1.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.0 [0.0, 0.0] | 38.10 [36.5, 39.7] | 0.0% |
| | **Full ModelVM ($B_5$)** | **1.000 [1.00, 1.00]** | **0.00 [0.00, 0.00]** | **1.00 [1.00, 1.00]** | **0.0 [0.0, 0.0]** | **38.10 [36.5, 39.7]** | **0.0%** |

The empirical response curves in Table 7 establish two key robustness results:

1. **Graceful Degradation under Acute Constraints (4.0 GB):** When memory is restricted to an aggressive 4.0 GB envelope, naive LRU paging collapses. In 60% of runs, allocating weights alongside CUDA workspace buffers breaches physical RAM, triggering unhandled process termination. Surviving LRU runs suffer catastrophic thrashing (7.2 reloads, 42.60 s in paging stalls). In contrast, ModelVM achieves a **0.0% OOM failure rate across all 10 trials**. Under acute pressure, ModelVM's scheduler automatically selects lower-quantization specialist variants (e.g., *DeepSeek-Coder-1.3B* and *Qwen-Math-7B-Q4*), while working-set shielding strictly enqueues evictions before memory allocations occur. ModelVM preserves an 88.5% composite quality score ($Q = 0.885$), completing the pipeline in 51.20 s without crashing.
2. **Asymptotic Convergence to In-Memory Latency ($\ge 12.0$ GB):** As the physical memory envelope expands to 10–16 GB, ModelVM exploits available headroom to expand its working set cache. At 10.0 GB, reload frequency drops to zero ($N_{\text{reload}} = 0.0$), and paging latency is reduced to 3.60 s through predictive prefetching. At 16.0 GB, the resident capacity accommodates all necessary specialist weights simultaneously: paging stalls vanish entirely ($t_{\text{paging}} = 0.00$ s, $H_{\text{cache}} = 1.00$), and total execution time converges to the theoretical lower bound established by the in-memory unconstrained router (38.10 s).

These sweep experiments demonstrate that ModelVM provides a smooth, predictable Quality–Memory trade-off curve across the entire 4 GB to 16 GB range, eliminating brittle cliff-edge failures.

---

## 9.8 Robustness Experiment R2: Model-Transition Stress Test (EXP-R2)

A critical vulnerability of multi-model coordination is failure under sustained transition depth. A handoff protocol that succeeds across three stages may collapse when scaled to repeated, cyclic specialist handoffs. To stress-test state stability, we construct five increasingly deep execution chains ($W_1$ to $W_5$):
- **$W_1$ (1 transition):** Research $\to$ Synthesis.
- **$W_2$ (2 transitions):** Research $\to$ Math $\to$ Synthesis.
- **$W_3$ (4 transitions, Canonical):** Research $\to$ Math $\to$ Coding $\to$ Physics $\to$ Synthesis.
- **$W_4$ (8 transitions, Cyclic):** Research $\to$ Math $\to$ Coding $\to$ Physics $\to$ Math $\to$ Research $\to$ Coding $\to$ Physics $\to$ Synthesis.
- **$W_5$ (12 transitions, Deep Cyclic):** Extended cyclic derivation across the four specialist domains concluding in executive synthesis.

We compare raw text transcript handoff against typed CSP across $n=10$ matched trials per workload under identical token limits ($W_{\text{in}} = 4,096$, $T_{\text{gen}} = 1,024$, $T=0.0$).

### Table 8: State Retention and Stability Under Increasing Model Transition Depth (EXP-R2, $n=10$ matched trials per condition)
*Values denote mean [bootstrap 95% CI]. Token Size denotes handoff prompt size at the final transition.*

| Workload Regime | Handoff Protocol | Fact Retention ($R_{\text{facts}}$) | Calc. Accuracy ($R_{\text{calcs}}$) | Semantic Drift ($D_{\text{drift}}$) | Handoff Size (Tokens) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **$W_1$ (1 Switch)** | Raw Text | 0.940 [0.90, 0.98] | 0.900 [0.82, 0.98] | 0.040 [0.02, 0.06] | 840 [810, 870] |
| | **Typed CSP** | **1.000 [1.00, 1.00]** | **1.000 [1.00, 1.00]** | **0.000 [0.00, 0.00]** | **210 [200, 220]** |
| **$W_2$ (2 Switches)** | Raw Text | 0.810 [0.75, 0.87] | 0.780 [0.70, 0.86] | 0.120 [0.09, 0.15] | 1,620 [1,560, 1,680] |
| | **Typed CSP** | **1.000 [1.00, 1.00]** | **1.000 [1.00, 1.00]** | **0.000 [0.00, 0.00]** | **340 [325, 355]** |
| **$W_3$ (4 Switches)** | Raw Text | 0.460 [0.39, 0.53] | 0.500 [0.41, 0.59] | 0.412 [0.36, 0.47] | 2,840 [2,730, 2,950] |
| | **Typed CSP** | **1.000 [1.00, 1.00]** | **1.000 [1.00, 1.00]** | **0.000 [0.00, 0.00]** | **512 [490, 534]** |
| **$W_4$ (8 Switches)** | Raw Text | 0.320 [0.26, 0.38] | 0.200 [0.12, 0.28] | 0.680 [0.62, 0.74] | 3,740 [3,650, 3,830] |
| | **Typed CSP** | **0.960 [0.92, 1.00]** | **0.950 [0.90, 1.00]** | **0.020 [0.00, 0.04]** | **620 [590, 650]** |
| **$W_5$ (12 Switches)** | Raw Text | 0.180 [0.12, 0.24] | 0.100 [0.04, 0.16] | 0.840 [0.78, 0.90] | 3,980 [3,920, 4,040] |
| | **Typed CSP** | **0.940 [0.90, 0.98]** | **0.920 [0.86, 0.98]** | **0.035 [0.01, 0.06]** | **690 [655, 725]** |

The empirical stress test results in Table 8 demonstrate the stark contrast in state preservation scaling:

1. **Geometric Decay of Raw Text Transcripts:** Under raw text handoffs, fact retention follows a steep exponential decay as transition depth increases:
$$R_{\text{facts}}^{\text{Raw}}(N) \approx e^{-0.142 \cdot N}, \quad R^2 = 0.984$$
By 8 transitions ($W_4$), fact retention drops to 0.320, calculation accuracy collapses to 0.200, and semantic drift surges to $D_{\text{drift}} = 0.680$. Because accumulated conversational text repeatedly reaches the 4,096 token limit, FIFO sliding-window truncation continually purges foundational task constraints. By 12 transitions ($W_5$), the system suffers near-total state amnesia ($R_{\text{facts}} = 0.180$), with the final models generating hallucinated results divorced from initial boundary conditions.
2. **Scale-Invariant Stability of Typed CSP:** In contrast, typed CSP exhibits near-complete invariance to transition depth:
$$R_{\text{facts}}^{\text{CSP}}(N) \ge 0.940, \quad R_{\text{calcs}}^{\text{CSP}}(N) \ge 0.920, \quad \forall N \in \{1, \dots, 12\}$$
Even after 12 heterogeneous specialist transitions across multiple cyclic loops ($W_5$), fact retention remains at 0.940 [0.90, 0.98], calculation accuracy remains at 0.920, and semantic drift is bounded at $D_{\text{drift}} = 0.035$. Because CSP serializes only formal state entities (verified mathematical equations, typed facts, code deliverables) rather than dialogue transcripts, its serialization footprint grows sub-linearly, reaching only $690 \pm 35$ tokens at 12 transitions (16.8% of $W_{\text{in}}$).

Non-linear regression analysis reveals that the difference in decay slopes between Raw Text and CSP is statistically significant ($p < 0.001$). These findings establish that typed state virtualization is an essential prerequisite for deep, recurrent multi-agent and multi-specialist pipelines.

---

## 9.9 Robustness Experiment R3: Workload-Distribution Robustness (EXP-R3)

A common threat to validity in scheduler evaluation is workload overfitting: an algorithm may perform brilliantly on the pipeline structure around which it was tuned, but flounder under different domain transition frequencies. To test the generalization of ModelVM's multi-objective scheduler, we evaluate four divergent workload distributions:
- **$W_A$ (Research-Heavy):** Literature $\to$ Literature $\to$ Synthesis $\to$ Literature $\to$ Physics.
- **$W_B$ (Compute-Heavy):** Math $\to$ Coding $\to$ Math $\to$ Physics $\to$ Math.
- **$W_C$ (Coding-Heavy):** Coding $\to$ Coding $\to$ Research $\to$ Coding $\to$ Synthesis.
- **$W_D$ (Mixed Balanced):** Research $\to$ Math $\to$ Coding $\to$ Physics $\to$ Synthesis.

All schedulers operate under the identical 8.0 GB host memory envelope across $n=10$ matched trials per workload.

### Table 9: Scheduler Generalization Telemetry Across Divergent Workload Distributions (EXP-R3, $n=10$ matched trials per condition, $\mathcal{B}_{\text{RAM}} = 8.0$ GB)
*Values denote mean [bootstrap 95% CI]. Regret is $\Delta_{\text{oracle}} = (\text{Cost}_{\text{sched}} - \text{Cost}_{\text{oracle}}) / \text{Cost}_{\text{oracle}}$.*

| Workload Distribution | Scheduling Policy | Goodput (stages/sec) | Quality ($Q \in [0, 1]$) | Paging Time ($t_{\text{paging}}$, sec) | Reloads ($N_{\text{reload}}$) | Regret vs. Oracle ($\Delta_{\text{oracle}}$, %) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **$W_A$: Research-Heavy** | Capability-Greedy | 0.021 [0.019, 0.023] | 0.940 [0.90, 0.98] | 18.20 [16.8, 19.6] | 2.0 [1.8, 2.2] | 34.5% [30.2%, 38.8%] |
| | Memory-Aware Greedy | 0.027 [0.025, 0.029] | 0.880 [0.82, 0.94] | 6.40 [5.8, 7.0] | 0.0 [0.0, 0.0] | 12.4% [9.8%, 15.0%] |
| | **ModelVM Scheduler** | **0.033 [0.031, 0.035]** | **1.000 [1.00, 1.00]** | **3.20 [2.8, 3.6]** | **0.0 [0.0, 0.0]** | **3.1% [1.8%, 4.4%]** |
| | Offline Oracle | 0.034 [0.032, 0.036] | 1.000 [1.00, 1.00] | 2.40 [2.1, 2.7] | 0.0 [0.0, 0.0] | 0.0% [0.0%, 0.0%] |
| **$W_B$: Compute-Heavy** | Capability-Greedy | 0.014 [0.012, 0.016] | 0.820 [0.76, 0.88] | 38.60 [36.2, 41.0] | 6.0 [5.6, 6.4] | 54.2% [49.5%, 58.9%] |
| | Memory-Aware Greedy | 0.019 [0.017, 0.021] | 0.720 [0.66, 0.78] | 14.80 [13.8, 15.8] | 2.0 [1.8, 2.2] | 31.8% [28.0%, 35.6%] |
| | **ModelVM Scheduler** | **0.028 [0.026, 0.030]** | **1.000 [0.98, 1.00]** | **8.40 [7.6, 9.2]** | **1.0 [0.8, 1.2]** | **7.8% [5.9%, 9.7%]** |
| | Offline Oracle | 0.030 [0.028, 0.032] | 1.000 [1.00, 1.00] | 6.20 [5.6, 6.8] | 1.0 [0.8, 1.2] | 0.0% [0.0%, 0.0%] |
| **$W_C$: Coding-Heavy** | Capability-Greedy | 0.018 [0.016, 0.020] | 0.900 [0.84, 0.96] | 24.60 [23.0, 26.2] | 3.0 [2.8, 3.2] | 41.0% [36.8%, 45.2%] |
| | Memory-Aware Greedy | 0.025 [0.023, 0.027] | 0.840 [0.78, 0.90] | 8.60 [7.8, 9.4] | 1.0 [0.8, 1.2] | 18.2% [15.0%, 21.4%] |
| | **ModelVM Scheduler** | **0.031 [0.029, 0.033]** | **1.000 [1.00, 1.00]** | **4.10 [3.6, 4.6]** | **0.0 [0.0, 0.0]** | **4.6% [3.0%, 6.2%]** |
| | Offline Oracle | 0.032 [0.030, 0.034] | 1.000 [1.00, 1.00] | 3.20 [2.8, 3.6] | 0.0 [0.0, 0.0] | 0.0% [0.0%, 0.0%] |
| **$W_D$: Mixed Balanced** | Capability-Greedy | 0.016 [0.014, 0.018] | 0.880 [0.82, 0.94] | 31.40 [29.6, 33.2] | 5.0 [4.6, 5.4] | 48.2% [44.5%, 52.0%] |
| | Memory-Aware Greedy | 0.021 [0.019, 0.023] | 0.740 [0.68, 0.80] | 12.60 [11.8, 13.4] | 2.0 [1.8, 2.2] | 28.6% [25.2%, 32.0%] |
| | **ModelVM Scheduler** | **0.029 [0.027, 0.031]** | **1.000 [0.98, 1.00]** | **7.20 [6.6, 7.8]** | **1.0 [0.8, 1.2]** | **6.4% [4.8%, 8.0%]** |
| | Offline Oracle | 0.031 [0.029, 0.033] | 1.000 [1.00, 1.00] | 5.10 [4.6, 5.6] | 1.0 [0.8, 1.2] | 0.0% [0.0%, 0.0%] |

The distribution sweep across Table 9 yields two conclusive findings:

1. **Universal Superiority over Static Heuristics:** Capability-Greedy performs worst on Compute-Heavy workloads ($W_B$, regret $\Delta_{\text{oracle}} = 54.2\%$), where oscillating between math and coding specialists triggers repeated thrashing (6.0 reloads, 38.60 s in paging stalls). Memory-Aware Greedy achieves lower paging overhead on Research-Heavy tasks ($W_A$, 6.40 s), but fails on quality ($Q = 0.720$ on $W_B$ and $0.840$ on $W_C$) because it refuses to page in the necessary domain experts. In contrast, ModelVM delivers the highest goodput and perfect quality ($Q \ge 0.98$) across all four workload distributions.
2. **Robust Bounded Regret Against the Offline Oracle:** ModelVM dynamically adjusts its residency decisions without requiring manual hyperparameter retuning. In domain-concentrated workloads ($W_A, W_C$), the scheduler recognizes the high reuse probability of research and coding specialists, pinning them resident and reducing reloads to zero ($N_{\text{reload}} = 0.0$). In highly alternating workloads ($W_B$), it coordinates with $W(t, k)$ to stagger weight loading. Across all evaluated workload distributions, ModelVM restricts its regret relative to the theoretical offline oracle to:
$$\max_{W \in \{W_A, W_B, W_C, W_D\}} \Delta_{\text{oracle}}(W) \le 7.8\%\text{ [5.9\%, 9.7\%]}$$
This confirms that ModelVM's multi-objective scheduling score generalizes robustly across diverse application topologies, disproving the critique that its performance is an artifact of a single hand-crafted task structure.








