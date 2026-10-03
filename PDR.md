# PDR — ModelVM

## Virtual Memory for Intelligence

### 1. Project Summary

**ModelVM** is a local AI runtime that treats open-weight AI models as **pageable cognitive resources** rather than permanently loaded applications.

Instead of running one monolithic model or keeping many specialist models simultaneously in memory, ModelVM maintains a library of heterogeneous open-weight models and dynamically:

* selects the required capability,
* predicts which capabilities will be needed next,
* loads only the necessary model into memory,
* transfers task state through a model-neutral representation,
* unloads models when their role is complete,
* and escalates or switches models when confidence is insufficient.

The objective is to provide **multi-domain AI capability under a hard memory constraint**.

### 2. Problem

Open-weight models have made local AI increasingly practical, but specialization creates a deployment problem.

A useful local AI may require separate capabilities for:

* coding,
* mathematics,
* science,
* research,
* writing,
* finance,
* vision,
* data analysis.

Keeping all of these models resident can exceed the RAM/VRAM of a consumer device.

Existing research addresses important pieces of this problem. Heterogeneous LLM routing systems such as HyDRA select models according to capability requirements, while FLARE explicitly considers resource-efficient routing. Recent orchestration work also considers future model demand, model residency and loading costs.

The proposed question is therefore narrower:

> **Can heterogeneous open-weight models be treated as pageable cognitive resources, allowing a local AI system to dynamically construct multi-step intelligence within a strict memory budget?**

### 3. Core Insight

The key abstraction is:

> **Intelligence should be virtualized in the same way an operating system virtualizes memory.**

| Operating System | ModelVM                   |
| ---------------- | ------------------------- |
| Process          | AI capability             |
| RAM              | Active model memory       |
| Disk             | Model library             |
| Page-in          | Load model                |
| Page-out         | Unload model              |
| Cache            | Resident model cache      |
| Prefetch         | Predict next model        |
| Working set      | Predicted required models |
| Scheduler        | Cognitive scheduler       |
| Process state    | Cognitive State Packet    |

This analogy is an architectural design principle, not merely branding.

### 4. Proposed Architecture

```text
                         USER TASK
                             │
                             ▼
                  ┌─────────────────────┐
                  │   COGNITIVE KERNEL  │
                  │                     │
                  │ Task decomposition  │
                  │ Capability matching │
                  │ Resource awareness  │
                  │ Confidence control  │
                  │ Working-set predict │
                  └──────────┬──────────┘
                             │
                 ┌───────────▼───────────┐
                 │    MODEL SCHEDULER    │
                 │ capability × resource │
                 │ × future demand       │
                 └───────────┬───────────┘
                             │
                  ┌──────────▼──────────┐
                  │    MODEL PAGER      │
                  │                     │
                  │ load / evict / cache│
                  │ RAM budget          │
                  │ load-cost awareness │
                  └──────────┬──────────┘
                             │
       ┌─────────────────────┼─────────────────────┐
       ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Science      │      │ Coding       │      │ Mathematics  │
│ Expert       │      │ Expert       │      │ Expert       │
└──────────────┘      └──────────────┘      └──────────────┘

                + additional open-weight models
```

Only a subset is resident at any moment.

### 5. Cognitive State Packet

The most important mechanism beyond routing is the **Cognitive State Packet (CSP)**.

Models are allowed to have different architectures, tokenizers, sizes and training domains. They do not need to exchange raw hidden states.

Instead, a completed reasoning stage emits structured semantic state:

```json
{
  "goal": "...",
  "facts": [],
  "calculations": [],
  "evidence": [],
  "assumptions": [],
  "uncertainties": [],
  "decisions": [],
  "open_questions": [],
  "next_capability": "..."
}
```

The next model consumes this state.

Therefore:

```text
Model A
  ↓
Cognitive State Packet
  ↓
unload Model A
  ↓
load Model B
  ↓
Cognitive State Packet
  ↓
unload Model B
  ↓
load Model C
```

This allows the system to perform a long multi-domain task without requiring every specialist to remain in memory.

### 6. Example

User:

> “Analyze this scientific paper, reproduce its numerical result, write the implementation, and explain the physical meaning.”

ModelVM predicts:

```text
research → mathematics → coding → physics → synthesis
```

Execution:

```text
Research Expert
     │
     ├── extracts equations
     ├── identifies assumptions
     └── produces CSP
             │
             ▼
       model unloaded

Math Expert
     │
     ├── reproduces calculation
     └── produces CSP
             │
             ▼
       model unloaded

Coding Expert
     │
     ├── writes implementation
     └── produces CSP
             │
             ▼
       model unloaded

Physics Expert
     │
     └── interprets result
             │
             ▼
       final synthesizer
```

A machine may have a 50 GB model library while maintaining an 8 GB active-model budget.

### 7. Novelty

The project should **not** claim novelty in:

> “routing queries between multiple LLMs”

or:

> “dynamically loading models.”

Both have substantial prior art.

The proposed contribution is the combination of four system-level mechanisms:

**1. Pageable cognitive resources**
Independent open-weight models are treated as interchangeable cognitive modules whose residency is dynamically managed.

**2. Model-neutral semantic state**
A standardized Cognitive State Packet allows heterogeneous models to participate sequentially without requiring shared architecture or tokenizer.

**3. Predictive cognitive working set**
The runtime predicts the sequence of capabilities required for a task and can prefetch the next model before it is needed.

**4. Joint capability/resource scheduling**
Model selection considers not only task suitability but also memory footprint, loading cost, latency, current residency and predicted future demand.

The resulting research direction is:

> **Virtualization of heterogeneous AI capability under constrained memory.**

### 8. Research Hypothesis

> A collection of specialized open-weight models managed by a cognitive paging runtime can provide broad multi-domain capability with substantially lower peak memory consumption than keeping all specialist models resident, while preserving acceptable task quality.

### 9. MVP Architecture

The competition prototype uses 3–4 core models and supports arbitrary additional models.

Recommended capabilities:
- General / Reasoning
- Science / Research
- Coding
- Mathematics

Components:
- `model_registry/`
- `scheduler/`
- `memory_manager/`
- `cognitive_state/`
- `router/`
- `executor/`
- `benchmark/`
- `visualizer/`

Every model receives a manifest:

```yaml
name:
path:
capabilities:
ram_required:
load_time:
latency:
quality:
offline:
```

### 10. Resource-Aware Scheduling

Scheduling objective:

$$Score(m) = F_{capability} - \alpha M_{cost} - \beta L_{load} - \gamma E_{energy} - \delta E_{eviction} + \eta F_{future}$$

where:
* $F_{capability}$ = predicted task fit
* $M_{cost}$ = memory requirement
* $L_{load}$ = model loading latency
* $E_{energy}$ = estimated energy cost
* $E_{eviction}$ = cost of removing a currently resident model
* $F_{future}$ = predicted usefulness for upcoming task stages

### 11. Demonstration

A hard memory-budget experiment:
- Model library: 10 models, 52.7 GB total
- Active memory budget: 8.0 GB max resident

### 12. Evaluation

Measure four dimensions:
1. **Memory**: $\text{MemorySavings} = 1 - \frac{\text{PeakMemory}_{\text{ModelVM}}}{\text{PeakMemory}_{\text{AllResident}}}$
2. **Quality**: Task completion / benchmark accuracy against baselines
3. **Latency**: First-token latency, model loading time, total task time, paging overhead
4. **Efficiency**: $\text{CapabilityDensity} = \frac{\text{Task Capability Coverage}}{\text{Peak Resident Memory}}$

### 13. Critical Ablation Study

Run four configurations:
- **A. Static single-model routing**
- **B. Routing + dynamic loading**
- **C. Routing + dynamic loading + CSP**
- **D. Full ModelVM (CSP + predictive working set + resource-aware scheduling)**
