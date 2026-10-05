# Appendix: Empirical Ablation Benchmark Results

**Execution Timestamp:** `2026-10-05T16:36:58.381967`  
**Target Task:** *Analyze this scientific paper, reproduce its numerical result, write the implementation, and explain the physical meaning.*  
**RAM Budget Constraint:** `8.0 GB` | **All-Resident Catalog Baseline:** `52.7 GB`

---

## 1. Orthogonal 2³ Factorial Ablation Matrix (Dynamic Paging Substrate)

| Configuration ID | Paging | Factor A: CSP | Factor B: WS | Factor C: Sched | Peak RAM | MSR (%) | Quality (CCS) | Cap Density | Paging (s) | Verified Calcs |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `REF_STATIC_MONOLITH` | ❌ None | ❌ Off | ❌ Off | ❌ Off | 7.1 GB | 86.5% | **0.69** | 0.48 | 2.1s | 0 |
| `C0_PAGING_BASE` | ✅ Active | ❌ Off | ❌ Off | ❌ Off | 7.6 GB | 85.6% | **0.69** | 0.45 | 7.2s | 0 |
| `C1_CSP` | ✅ Active | ✅ On | ❌ Off | ❌ Off | 7.6 GB | 85.6% | **1.00** | 0.66 | 7.2s | 4 |
| `C2_WS` | ✅ Active | ❌ Off | ✅ On | ❌ Off | 7.6 GB | 85.6% | **0.69** | 0.45 | 7.2s | 0 |
| `C3_SCHEDULER` | ✅ Active | ❌ Off | ❌ Off | ✅ On | 7.6 GB | 85.6% | **0.69** | 0.45 | 7.2s | 0 |
| `C4_CSP_WS` | ✅ Active | ✅ On | ✅ On | ❌ Off | 7.6 GB | 85.6% | **1.00** | 0.66 | 7.2s | 4 |
| `C5_CSP_SCHEDULER` | ✅ Active | ✅ On | ❌ Off | ✅ On | 7.6 GB | 85.6% | **1.00** | 0.66 | 7.2s | 4 |
| `C6_WS_SCHEDULER` | ✅ Active | ❌ Off | ✅ On | ✅ On | 7.6 GB | 85.6% | **0.69** | 0.45 | 7.2s | 0 |
| `C7_FULL_MODELVM` | ✅ Active | ✅ On | ✅ On | ✅ On | 7.6 GB | 85.6% | **1.00** | 0.66 | 7.2s | 4 |

### Statistical Factor Effects & Interactions (Yates Analysis)

```text
2^3 Factorial Analysis (Dynamic Paging Substrate):
  - Main Effect of CSP (Factor A): Δ = +0.3120
  - Main Effect of Working Set (Factor B): Δ = +0.0000
  - Main Effect of Scheduler (Factor C): Δ = +0.0000
  - Interaction CSP x WS: Δ = +0.0000
  - Interaction CSP x Scheduler: Δ = +0.0000
  - Interaction WS x Scheduler: Δ = +0.0000
  - 3-Way Interaction (CSP x WS x Sched): Δ = +0.0000
  - Paging Overhead Comparison (C0 Base -> C7 Full): 7.20s -> 7.20s
```

---

## 1. Comprehensive Cross-Configuration Comparison

| Mode | Peak RAM | MSR (%) | Quality (CCS) | Cap Density | Total Time | Paging Overhead | Cache Hit | Facts | Verified Calcs |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `A_STATIC_ROUTER` | 7.1 GB | 86.5% | **0.69** | 0.48 | 2.85s | 2.1s | 0.0% | 3 | 0 |
| `B_DYNAMIC_NO_CSP` | 7.6 GB | 85.6% | **0.69** | 0.45 | 2.46s | 7.2s | 0.0% | 3 | 0 |
| `C_DYNAMIC_WITH_CSP` | 7.6 GB | 85.6% | **1.00** | 0.66 | 2.46s | 7.2s | 0.0% | 10 | 4 |
| `D_FULL_MODELVM` | 7.6 GB | 85.6% | **1.00** | 0.66 | 2.46s | 7.2s | 16.7% | 10 | 4 |

---

## 2. Detailed Stage Traces & Memory Events

### Configuration: `A_STATIC_ROUTER`

- **Peak Resident Memory:** 7.1 GB (Savings: 86.5%)
- **Quality Score (CCS):** 0.688 (Derived from 3 facts, 0 verified calcs)
- **Cache Hit Rate:** 0.0% | Paging Overhead: 2.1s

#### Stage Execution Log:
| Stage Index | Stage Title | Capability | Executing Model | Time (s) | Paging Action |
| :---: | :--- | :--- | :--- | :---: | :--- |
| 0 | Extract scientific assumptions & equations | `Capability.RESEARCH` | `general-reasoner` | 0.57s | PagingAction.CACHE_HIT |
| 1 | Formal mathematical derivation & numerical solving | `Capability.MATHEMATICS` | `general-reasoner` | 0.57s | PagingAction.CACHE_HIT |
| 2 | Algorithm implementation & simulation code | `Capability.CODING` | `general-reasoner` | 0.57s | PagingAction.CACHE_HIT |
| 3 | Physical interpretation & thermodynamic analysis | `Capability.PHYSICS` | `general-reasoner` | 0.57s | PagingAction.CACHE_HIT |
| 4 | Comprehensive synthesis & executive report | `Capability.SYNTHESIS` | `general-reasoner` | 0.57s | PagingAction.CACHE_HIT |

### Configuration: `B_DYNAMIC_NO_CSP`

- **Peak Resident Memory:** 7.6 GB (Savings: 85.6%)
- **Quality Score (CCS):** 0.688 (Derived from 3 facts, 0 verified calcs)
- **Cache Hit Rate:** 0.0% | Paging Overhead: 7.2s

#### Stage Execution Log:
| Stage Index | Stage Title | Capability | Executing Model | Time (s) | Paging Action |
| :---: | :--- | :--- | :--- | :---: | :--- |
| 0 | Extract scientific assumptions & equations | `Capability.RESEARCH` | `research-expert` | 0.48s | PagingAction.PAGE_IN |
| 1 | Formal mathematical derivation & numerical solving | `Capability.MATHEMATICS` | `mathematics-expert` | 0.42s | PagingAction.PAGE_IN |
| 2 | Algorithm implementation & simulation code | `Capability.CODING` | `coding-expert` | 0.45s | PagingAction.PAGE_IN |
| 3 | Physical interpretation & thermodynamic analysis | `Capability.PHYSICS` | `physics-expert` | 0.51s | PagingAction.PAGE_IN |
| 4 | Comprehensive synthesis & executive report | `Capability.SYNTHESIS` | `synthesizer-master` | 0.60s | PagingAction.PAGE_IN |

### Configuration: `C_DYNAMIC_WITH_CSP`

- **Peak Resident Memory:** 7.6 GB (Savings: 85.6%)
- **Quality Score (CCS):** 1.0 (Derived from 10 facts, 4 verified calcs)
- **Cache Hit Rate:** 0.0% | Paging Overhead: 7.2s

#### Stage Execution Log:
| Stage Index | Stage Title | Capability | Executing Model | Time (s) | Paging Action |
| :---: | :--- | :--- | :--- | :---: | :--- |
| 0 | Extract scientific assumptions & equations | `Capability.RESEARCH` | `research-expert` | 0.48s | PagingAction.PAGE_IN |
| 1 | Formal mathematical derivation & numerical solving | `Capability.MATHEMATICS` | `mathematics-expert` | 0.42s | PagingAction.PAGE_IN |
| 2 | Algorithm implementation & simulation code | `Capability.CODING` | `coding-expert` | 0.45s | PagingAction.PAGE_IN |
| 3 | Physical interpretation & thermodynamic analysis | `Capability.PHYSICS` | `physics-expert` | 0.51s | PagingAction.PAGE_IN |
| 4 | Comprehensive synthesis & executive report | `Capability.SYNTHESIS` | `synthesizer-master` | 0.60s | PagingAction.PAGE_IN |

### Configuration: `D_FULL_MODELVM`

- **Peak Resident Memory:** 7.6 GB (Savings: 85.6%)
- **Quality Score (CCS):** 1.0 (Derived from 10 facts, 4 verified calcs)
- **Cache Hit Rate:** 16.7% | Paging Overhead: 7.2s

#### Stage Execution Log:
| Stage Index | Stage Title | Capability | Executing Model | Time (s) | Paging Action |
| :---: | :--- | :--- | :--- | :---: | :--- |
| 0 | Extract scientific assumptions & equations | `Capability.RESEARCH` | `research-expert` | 0.48s | PagingAction.PAGE_IN |
| 1 | Formal mathematical derivation & numerical solving | `Capability.MATHEMATICS` | `mathematics-expert` | 0.42s | PagingAction.CACHE_HIT |
| 2 | Algorithm implementation & simulation code | `Capability.CODING` | `coding-expert` | 0.45s | PagingAction.PAGE_IN |
| 3 | Physical interpretation & thermodynamic analysis | `Capability.PHYSICS` | `physics-expert` | 0.51s | PagingAction.PAGE_IN |
| 4 | Comprehensive synthesis & executive report | `Capability.SYNTHESIS` | `synthesizer-master` | 0.60s | PagingAction.PAGE_IN |
