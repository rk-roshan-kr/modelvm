# ModelVM Research Paper Package

This directory contains the complete conference publication manuscripts and bibliographic assets for:

**ModelVM: Virtualizing Semantic State and Model Residency for Resource-Constrained Language Model Systems**  
*Tagline: Virtual Memory for Intelligence*  
*Target Venues:* MLSys 2026 / OSDI 2026 / EuroSys 2026

---

## Directory Contents

| File | Purpose | Format |
| :--- | :--- | :--- |
| [`PAPER_STRUCTURE.md`](file:///d:/hacktoberfest/paper/PAPER_STRUCTURE.md) | **Primary Structural Blueprint:** Section-by-section outline, page budgets, formulas, and arguments | Markdown |
| [`paper.md`](file:///d:/hacktoberfest/paper/paper.md) | Working paper draft manuscript | Markdown |
| [`main.tex`](file:///d:/hacktoberfest/paper/main.tex) | Double-column conference LaTeX template | LaTeX |
| [`references.bib`](file:///d:/hacktoberfest/paper/references.bib) | Full BibTeX citation bibliography | BibTeX |

---

## Compilation Instructions

To compile the LaTeX source into a double-column camera-ready PDF:

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Alternatively, the contents of `paper/main.tex` and `paper/references.bib` can be directly imported into an Overleaf project.

---

## Core Systems Claim

> **ModelVM is a resource-aware runtime that virtualizes semantic state and model residency while coordinating heterogeneous model execution under constrained hardware resources.**

---

## The Three Systems Contributions

1. **Semantic State Virtualization (Cognitive State Packet / CSP):** A model-neutral, typed semantic intermediate representation that preserves structured task state (verified facts, calculations, evidence, assumptions, decisions, artifacts) across models with incompatible tokenizers and architectures without hidden-state projection bridges.
2. **Predictive Model Residency:** Paging open-weight models under hard physical memory budgets (8.0 GB active budget for a 52.7 GB library), managed via working-set lookahead ($W(t, k)$), eviction shielding, and opportunistic background weight prefetching.
3. **Resource-Aware Cognitive Scheduling:** A multi-objective optimization function balancing capability fit, memory footprint, cold-load latency, energy consumption, eviction penalties, and future stage reuse, grounded by empirical capability profiling over held-out benchmark probes.
4. **Controlled Orthogonal $2^3$ Factorial Evaluation:** Isolating main effects ($\Delta_{\text{CSP}} = +0.4380, \Delta_{\text{WS}} = 0.0, \Delta_{\text{Sched}} = 0.0$) across 8 configurations on the dynamic paging substrate (`C0`–`C7`) evaluated against an external static monolithic baseline (`REF_STATIC_MONOLITH`) across four independent dimensions: Quality ($Q$), State Retention ($R$), Resource Efficiency ($E$), and Latency ($L$).
