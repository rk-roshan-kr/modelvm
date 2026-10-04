# ModelVM Developer & Extensibility Guide

This guide provides practical instructions for extending, customizing, and benchmarking the ModelVM runtime.

---

## 1. Environment Setup

ModelVM requires Python 3.10+ and standard lightweight dependencies:

```bash
cd d:\hacktoberfest

# Install dependencies
pip install -r requirements.txt

# Run test suite to verify installation
python -m unittest discover -s tests
```

---

## 2. Registering a New Specialist Model

Model manifests define how ModelVM evaluates and manages each model. You can register models programmatically or by creating a YAML file in `modelvm/registry/manifests/`.

### Example: Adding a Starcoder3 Security Specialist
Create `modelvm/registry/manifests/starcoder3-security.yaml`:

```yaml
id: starcoder3-security
name: StarCoder3-Security-15B
capabilities:
  - security
  - coding
ram_required: 7.4
load_time: 2.4
latency: 0.038
quality: 0.95
offline: true
architecture: StarCoder3ForCausalLM
parameters_billion: 15.0
quantization: Q4_K_M
context_window: 16384
energy_cost_factor: 1.1
description: Deep vulnerability auditing, taint analysis, and cryptographic implementation.
```

The catalog automatically loads any `.yaml` files placed in this directory upon initialization.

### Programmatic Registration
```python
from modelvm.core.manifest import ModelManifest
from modelvm.core.types import Capability
from modelvm.registry.catalog import ModelCatalog

catalog = ModelCatalog()
manifest = ModelManifest(
    id="custom-chem-7b",
    name="Llama-Chemistry-7B",
    capabilities=[Capability.SCIENCE, Capability.RESEARCH],
    ram_required: 3.2,
    load_time: 1.1,
    quality: 0.94,
    quantization: "Q4_K_M",
    description="Computational chemistry, reaction kinetics, and stoichiometry.",
)
catalog.register(manifest)
```

---

## 3. Implementing a Custom Eviction Policy

ModelVM allows plugging in custom eviction algorithms by subclassing `EvictionPolicy`.

### Example: Adaptive Frequency & Size (AFS) Eviction
```python
import time
from typing import Dict, List, Optional, Set
from modelvm.core.manifest import ModelManifest
from modelvm.pager.policy import EvictionPolicy

class AdaptiveFrequencySizePolicy(EvictionPolicy):
    """Prefers evicting models with low access counts and large memory yields."""
    
    def select_eviction_candidates(
        self,
        resident_models: Dict[str, ModelManifest],
        required_ram_gb: float,
        available_ram_gb: float,
        protected_ids: Optional[Set[str]] = None,
        future_demanded_ids: Optional[Set[str]] = None,
    ) -> List[ModelManifest]:
        protected = protected_ids or set()
        future = future_demanded_ids or set()
        
        candidates = [m for m in resident_models.values() if m.id not in protected]
        
        def score(m: ModelManifest) -> float:
            future_shield = 500.0 if m.id in future else 0.0
            # Higher score = evict first
            return (m.ram_required * 2.0) - (m.access_count * 1.5) - future_shield
            
        candidates.sort(key=score, reverse=True)
        
        to_evict = []
        freed = 0.0
        deficit = required_ram_gb - available_ram_gb
        for m in candidates:
            if freed >= deficit:
                break
            to_evict.append(m)
            freed += m.ram_required
            
        return to_evict
```

To use it with the kernel:
```python
from modelvm.executor.kernel import CognitiveKernel

kernel = CognitiveKernel(memory_budget_gb=8.0)
kernel.pager.policy = AdaptiveFrequencySizePolicy()
```

---

## 4. Connecting a Real Local LLM Inference Engine

By default, ModelVM uses `SimulationBackend` for deterministic evaluation. You can connect local inference servers such as **Ollama**, **llama.cpp**, or **vLLM**.

### Subclassing `ModelBackend`
```python
from modelvm.core.manifest import ModelManifest
from modelvm.core.state_packet import CognitiveStatePacket
from modelvm.core.types import Capability
from modelvm.executor.backends import ModelBackend
import requests

class LlamaCppServerBackend(ModelBackend):
    def __init__(self, endpoint: str = "http://localhost:8080/completion"):
        self.endpoint = endpoint

    def execute_stage(
        self,
        model: ModelManifest,
        stage_title: str,
        stage_description: str,
        capability: Capability,
        input_csp: CognitiveStatePacket,
    ) -> CognitiveStatePacket:
        prompt = (
            f"You are {model.name}, specializing in {capability.value.upper()}.\n"
            f"STAGE: {stage_title}\n"
            f"{input_csp.to_prompt_context()}\n"
            f"Output your reasoning and update the Cognitive State Packet in a ```json code block."
        )
        
        resp = requests.post(self.endpoint, json={"prompt": prompt, "n_predict": 512})
        text = resp.json().get("content", "")
        
        # Robustly parse structured state
        return CognitiveStatePacket.extract_from_text(
            goal=input_csp.goal,
            text=text,
            stage_index=input_csp.stage_index + 1,
        )
```

Plug it into the kernel:
```python
kernel = CognitiveKernel(backend=LlamaCppServerBackend())
summary = kernel.execute_task("Analyze quantum harmonic oscillator")
```

---

## 5. Tuning Cognitive Scheduler Objective Weights

The scheduler objective is parameterized by five coefficients:

$$\text{Score}(m) = F_{\text{capability}} - \alpha M_{\text{cost}} - \beta L_{\text{load}} - \gamma E_{\text{energy}} - \delta E_{\text{eviction}} + \eta F_{\text{future}}$$

You can configure them for different deployment profiles:

```python
from modelvm.scheduler.cognitive_scheduler import CognitiveScheduler

# Profile A: Aggressive Caching & Latency Minimization (e.g. fast NVMe)
scheduler = CognitiveScheduler(
    catalog=kernel.catalog,
    pager=kernel.pager,
    alpha=0.10,  # Lower RAM penalty
    beta=0.40,   # Higher load latency penalty
    gamma=0.05,
    delta=0.35,  # Higher eviction avoidance
    eta=0.45,    # Stronger future lookahead prefetching
)
kernel.scheduler = scheduler
```

---

## 6. Running Benchmarks & Ablation Studies

### Programmatic Benchmark Execution
```python
from modelvm.benchmark.ablation import AblationStudyRunner

runner = AblationStudyRunner(memory_budget_gb=8.0)
report = runner.run_study(
    task_goal="Analyze this scientific paper, reproduce its numerical result, write the implementation, and explain the physical meaning."
)

for mode_name, metrics in report.runs.items():
    print(f"[{mode_name}] Peak RAM: {metrics.peak_memory_gb} GB | Quality: {metrics.capability_coverage_score*100:.0f}% | Density: {metrics.capability_density}")
```

### CLI Benchmarking
```bash
# Run 4-mode Critical Ablation Study
python -m modelvm.cli benchmark --budget 8.0

# Run with custom budget
python -m modelvm.cli benchmark --budget 12.0
```
