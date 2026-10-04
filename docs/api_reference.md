# ModelVM API & Technical Reference

This document provides complete API reference documentation for the core classes, methods, and schemas in ModelVM.

---

## 1. `modelvm.core`

### 1.1 `CognitiveStatePacket`
Located in [`modelvm/core/state_packet.py`](file:///d:/hacktoberfest/modelvm/core/state_packet.py).

The standardized semantic container passed between paged specialist models.

```python
class CognitiveStatePacket(BaseModel):
    goal: str
    stage_index: int = 0
    current_capability: Optional[str] = None
    next_capability: Optional[str] = None
    facts: List[str] = []
    calculations: List[CalculationItem] = []
    evidence: List[EvidenceItem] = []
    assumptions: List[str] = []
    uncertainties: List[str] = []
    decisions: List[str] = []
    open_questions: List[str] = []
    artifacts: Dict[str, Any] = {}
    history_trace: List[StageTrace] = []
```

#### Key Methods:

##### `to_prompt_context() -> str`
Formats the packet into a markdown context block for prompt injection into an LLM.
* **Returns:** Formatted markdown string containing Goal, Facts, Calculations, Evidence, Assumptions, Uncertainties, and Prior Decisions.

##### `merge_update(update: CognitiveStatePacket) -> CognitiveStatePacket`
Monotonically merges new knowledge from a completed stage into the state packet without losing prior context.
* **Parameters:** `update` — State packet emitted by the currently executing model.
* **Behavior:** Appends new facts (deduplicated), calculations, and evidence; updates decisions and assumptions; purges answered open questions.
* **Returns:** Updated self instance.

##### `extract_from_text(goal: str, text: str, stage_index: int = 0) -> CognitiveStatePacket`
Parses raw LLM text (JSON code blocks or markdown lists) into a validated `CognitiveStatePacket`.

---

### 1.2 `ModelManifest`
Located in [`modelvm/core/manifest.py`](file:///d:/hacktoberfest/modelvm/core/manifest.py).

```python
class ModelManifest(BaseModel):
    id: str
    name: str
    path: str = ""
    capabilities: List[Capability] = []
    ram_required: float
    load_time: float
    latency: float = 0.04
    quality: float = 0.90
    offline: bool = True
    architecture: str = "decoder-only"
    parameters_billion: float = 7.0
    quantization: str = "Q4_K_M"
    context_window: int = 8192
    energy_cost_factor: float = 1.0
    description: str = ""
    status: ModelStatus = ModelStatus.DISK
```

#### Key Methods:
##### `capability_score(target: Capability) -> float`
Calculates capability match: $1.0$ for primary specialization, $0.75$ for secondary, $0.50$ for general models, $0.05$ otherwise.

---

## 2. `modelvm.pager`

### 2.1 `ModelPager`
Located in [`modelvm/pager/memory_manager.py`](file:///d:/hacktoberfest/modelvm/pager/memory_manager.py).

Virtual memory subsystem managing physical model weight residency within a strict RAM/VRAM envelope.

```python
class ModelPager:
    def __init__(
        self,
        catalog: ModelCatalog,
        memory_budget_gb: float = 8.0,
        policy: Optional[EvictionPolicy] = None
    )
```

#### Properties:
* `active_memory_gb -> float`: Sum of RAM of currently loaded resident models.
* `free_memory_gb -> float`: Available memory headroom ($\text{budget} - \text{active}$).
* `peak_memory_gb -> float`: Maximum active RAM observed.

#### Key Methods:

##### `page_in(model_id: str, protected_ids: Optional[Set[str]] = None, future_demanded_ids: Optional[Set[str]] = None) -> PagingEvent`
Brings a model from storage into active memory.
* **Behavior:** If model is already loaded, returns a `CACHE_HIT` event (zero latency). If free memory is insufficient, triggers `_evict_for()` to free the required RAM using the active `EvictionPolicy`.
* **Raises:** `MemoryError` if model size exceeds the entire device memory budget.

##### `page_out(model_id: str, action: PagingAction = PagingAction.PAGE_OUT, reason: str = "") -> PagingEvent`
Unloads a model from RAM back to disk, freeing memory.

##### `prefetch(model_id: str, protected_ids: Optional[Set[str]] = None, future_demanded_ids: Optional[Set[str]] = None) -> Optional[PagingEvent]`
Loads a model into spare memory in the background if $\text{free\_memory\_gb} \ge \text{model.ram\_required}$.

##### `add_listener(listener: Callable[[PagingEvent], None]) -> None`
Subscribes a callback to receive real-time paging events.

---

### 2.2 `CostAwareEvictionPolicy`
Located in [`modelvm/pager/policy.py`](file:///d:/hacktoberfest/modelvm/pager/policy.py).

```python
class CostAwareEvictionPolicy(EvictionPolicy):
    def select_eviction_candidates(
        self,
        resident_models: Dict[str, ModelManifest],
        required_ram_gb: float,
        available_ram_gb: float,
        protected_ids: Optional[Set[str]] = None,
        future_demanded_ids: Optional[Set[str]] = None,
    ) -> List[ModelManifest]
```
Calculates eviction priority based on access recency, RAM yield, reload latency, and predicted future working set protection.

---

## 3. `modelvm.scheduler`

### 3.1 `CognitiveScheduler`
Located in [`modelvm/scheduler/cognitive_scheduler.py`](file:///d:/hacktoberfest/modelvm/scheduler/cognitive_scheduler.py).

Multi-objective scheduler balancing domain suitability against systems loading costs and future stage demand.

```python
class CognitiveScheduler:
    def __init__(
        self,
        catalog: ModelCatalog,
        pager: ModelPager,
        alpha: float = 0.20,  # RAM weight
        beta: float = 0.25,   # Load latency weight
        gamma: float = 0.10,  # Energy weight
        delta: float = 0.30,  # Eviction cost weight
        eta: float = 0.35,    # Future demand bonus weight
    )
```

#### Key Methods:

##### `compute_score(model: ModelManifest, target_capability: Capability, future_capabilities: Optional[List[Capability]] = None, future_model_ids: Optional[Set[str]] = None) -> SchedulingScoreBreakdown`
Evaluates the objective function:

$$\text{Score}(m) = F_{\text{capability}} - \alpha M_{\text{cost}} - \beta L_{\text{load}} - \gamma E_{\text{energy}} - \delta E_{\text{eviction}} + \eta F_{\text{future}}$$

Returns a `SchedulingScoreBreakdown` with exact numerical terms.

##### `select_best_model(target_capability: Capability, future_capabilities: Optional[List[Capability]] = None, future_model_ids: Optional[Set[str]] = None) -> Tuple[ModelManifest, List[SchedulingScoreBreakdown]]`
Scores all candidate models that fit within the active budget and returns the winning model along with full score rankings.

---

## 4. `modelvm.executor`

### 4.1 `CognitiveKernel`
Located in [`modelvm/executor/kernel.py`](file:///d:/hacktoberfest/modelvm/executor/kernel.py).

The central runtime coordinator.

```python
class CognitiveKernel:
    def __init__(
        self,
        catalog: Optional[ModelCatalog] = None,
        memory_budget_gb: float = 8.0,
        backend: Optional[ModelBackend] = None,
    )
```

#### Key Methods:

##### `execute_task(goal: str, ablation_mode: AblationMode = AblationMode.D_FULL_MODELVM, custom_stages: Optional[List[CognitiveStagePlan]] = None) -> TaskExecutionSummary`
Executes an end-to-end multi-step task under virtual memory management.
* **Parameters:**
  * `goal`: The overarching task prompt.
  * `ablation_mode`: Architecture mode (`A_STATIC_ROUTER`, `B_DYNAMIC_NO_CSP`, `C_DYNAMIC_WITH_CSP`, `D_FULL_MODELVM`).
  * `custom_stages`: Optional list of explicit stage definitions.
* **Returns:** `TaskExecutionSummary` with stage results, memory telemetry, metrics, and final CSP.

##### `add_stage_listener(listener: Callable[[StageExecutionResult], None]) -> None`
Registers a listener callback triggered whenever a cognitive stage finishes.

---

## 5. `modelvm.benchmark`

### 5.1 `AblationStudyRunner`
Located in [`modelvm/benchmark/ablation.py`](file:///d:/hacktoberfest/modelvm/benchmark/ablation.py).

```python
class AblationStudyRunner:
    def __init__(self, memory_budget_gb: float = 8.0): ...
    def run_study(self, task_goal: Optional[str] = None) -> AblationReport: ...
```
Executes all four configurations (Modes A, B, C, D) side-by-side on an identical task, compiling Memory Savings, Quality Coverage, Capability Density, and Latency into an `AblationReport`.

---

## 6. REST & WebSocket API Reference

The FastAPI application is served by [`modelvm/api/server.py`](file:///d:/hacktoberfest/modelvm/api/server.py).

### Endpoints

| Method | Path | Request Body | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/status` | None | Returns active memory, budget, free RAM, resident models, and disk models. |
| `GET` | `/api/models` | None | Returns all registered model manifests in the library catalog. |
| `POST` | `/api/budget` | `{"budget_gb": 8.0}` | Dynamically adjusts the active RAM budget envelope. |
| `POST` | `/api/page_in` | `{"model_id": "qwen-math-7b"}` | Manually pages a model into active RAM for testing. |
| `POST` | `/api/page_out` | `{"model_id": "qwen-math-7b"}` | Manually unloads a model from active RAM. |
| `POST` | `/api/run` | `{"goal": str, "budget_gb": float, "ablation_mode": str}` | Executes task and broadcasts live stage telemetry over WebSocket. |
| `POST` | `/api/ablation` | `{"goal": str, "budget_gb": float}` | Runs full 4-mode Critical Ablation Study and returns comparison. |
| `WS` | `/ws` | WebSocket Stream | Emits real-time `PAGING_EVENT`, `STAGE_COMPLETED`, and `TASK_FINISHED` JSON events. |
| `GET` | `/` | None | Serves the interactive Cyber-OS Web Visualizer dashboard. |
