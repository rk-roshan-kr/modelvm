"""Model Catalog: Registry of available open-weight models."""

from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, List, Optional
import yaml

from modelvm.core.manifest import ModelManifest
from modelvm.core.types import Capability, ModelStatus


# Default 10 heterogeneous models matching PDR Section 11 (Total: 52.7 GB)
DEFAULT_MODELS: List[Dict] = [
    {
        "id": "research-expert",
        "name": "Mistral-Research-7B",
        "capabilities": [Capability.RESEARCH, Capability.SCIENCE],
        "ram_required": 3.1,
        "gpu_vram_weights_gb": 2.2,
        "gpu_vram_workspace_gb": 0.4,
        "cpu_ram_required": 0.5,
        "disk_size_gb": 4.2,
        "kv_cache_per_1k_tokens": 0.08,
        "load_time": 1.2,
        "latency": 0.032,
        "quality": 0.92,
        "offline": True,
        "architecture": "MistralForCausalLM",
        "parameters_billion": 7.2,
        "quantization": "Q4_K_M",
        "description": "Specialized in scientific literature analysis, equation extraction, and domain hypothesis formation.",
    },
    {
        "id": "mathematics-expert",
        "name": "Qwen-Math-7B",
        "capabilities": [Capability.MATHEMATICS],
        "ram_required": 2.4,
        "gpu_vram_weights_gb": 1.6,
        "gpu_vram_workspace_gb": 0.3,
        "cpu_ram_required": 0.5,
        "disk_size_gb": 3.6,
        "kv_cache_per_1k_tokens": 0.08,
        "load_time": 0.9,
        "latency": 0.028,
        "quality": 0.96,
        "offline": True,
        "architecture": "Qwen2ForCausalLM",
        "parameters_billion": 7.0,
        "quantization": "Q4_K_S",
        "description": "State-of-the-art formal mathematical reasoning, numerical computation, and symbolic theorem derivation.",
    },
    {
        "id": "coding-expert",
        "name": "DeepSeek-Coder-6.7B",
        "capabilities": [Capability.CODING],
        "ram_required": 3.0,
        "gpu_vram_weights_gb": 2.1,
        "gpu_vram_workspace_gb": 0.4,
        "cpu_ram_required": 0.5,
        "disk_size_gb": 3.9,
        "kv_cache_per_1k_tokens": 0.08,
        "load_time": 1.1,
        "latency": 0.030,
        "quality": 0.94,
        "offline": True,
        "architecture": "DeepSeekForCausalLM",
        "parameters_billion": 6.7,
        "quantization": "Q4_K_M",
        "description": "High-efficiency code synthesis, algorithmic implementation, unit testing, and numerical simulations.",
    },
    {
        "id": "physics-expert",
        "name": "Llama-Physics-8B",
        "capabilities": [Capability.PHYSICS, Capability.SCIENCE],
        "ram_required": 3.2,
        "gpu_vram_weights_gb": 2.3,
        "gpu_vram_workspace_gb": 0.4,
        "cpu_ram_required": 0.5,
        "disk_size_gb": 4.4,
        "kv_cache_per_1k_tokens": 0.08,
        "load_time": 1.3,
        "latency": 0.034,
        "quality": 0.90,
        "offline": True,
        "architecture": "LlamaForCausalLM",
        "parameters_billion": 8.0,
        "quantization": "Q4_K_M",
        "description": "Domain expert in classical mechanics, quantum theory, thermodynamic laws, and physical interpretations.",
    },
    {
        "id": "general-reasoner",
        "name": "Llama-3.1-8B-Instruct",
        "capabilities": [Capability.GENERAL, Capability.RESEARCH],
        "ram_required": 7.1,
        "gpu_vram_weights_gb": 6.0,
        "gpu_vram_workspace_gb": 0.6,
        "cpu_ram_required": 0.5,
        "disk_size_gb": 8.5,
        "kv_cache_per_1k_tokens": 0.08,
        "load_time": 2.1,
        "latency": 0.038,
        "quality": 0.91,
        "offline": True,
        "architecture": "LlamaForCausalLM",
        "parameters_billion": 8.0,
        "quantization": "Q6_K",
        "description": "Broad common-sense reasoning, task planning, decomposition, and multi-turn conversational synthesis.",
    },
    {
        "id": "multimodal-vision",
        "name": "Phi-3.5-Vision-4.2B",
        "capabilities": [Capability.VISION],
        "ram_required": 5.6,
        "gpu_vram_weights_gb": 4.6,
        "gpu_vram_workspace_gb": 0.5,
        "cpu_ram_required": 0.5,
        "disk_size_gb": 5.8,
        "kv_cache_per_1k_tokens": 0.08,
        "load_time": 1.7,
        "latency": 0.035,
        "quality": 0.88,
        "offline": True,
        "architecture": "Phi3VForCausalLM",
        "parameters_billion": 4.2,
        "quantization": "FP16/Q4",
        "description": "Chart parsing, visual scientific diagram extraction, image comprehension, and OCR table extraction.",
    },
    {
        "id": "code-auditor",
        "name": "StarCoder2-15B-Q4",
        "capabilities": [Capability.SECURITY, Capability.CODING],
        "ram_required": 7.2,
        "gpu_vram_weights_gb": 6.1,
        "gpu_vram_workspace_gb": 0.6,
        "cpu_ram_required": 0.5,
        "disk_size_gb": 8.8,
        "kv_cache_per_1k_tokens": 0.08,
        "load_time": 2.5,
        "latency": 0.042,
        "quality": 0.92,
        "offline": True,
        "architecture": "StarCoder2ForCausalLM",
        "parameters_billion": 15.0,
        "quantization": "Q4_K_M",
        "description": "Deep security auditing, vulnerability scanning, static analysis, and concurrency debugging.",
    },
    {
        "id": "biomedical-expert",
        "name": "Bio-Mistral-7B",
        "capabilities": [Capability.MEDICINE, Capability.SCIENCE],
        "ram_required": 6.8,
        "gpu_vram_weights_gb": 5.8,
        "gpu_vram_workspace_gb": 0.5,
        "cpu_ram_required": 0.5,
        "disk_size_gb": 7.9,
        "kv_cache_per_1k_tokens": 0.08,
        "load_time": 2.2,
        "latency": 0.036,
        "quality": 0.93,
        "offline": True,
        "architecture": "MistralForCausalLM",
        "parameters_billion": 7.0,
        "quantization": "Q6_K",
        "description": "Genomics, pharmacological pathways, clinical trials analysis, and molecular biology.",
    },
    {
        "id": "financial-analyst",
        "name": "Fin-LLaMA-8B",
        "capabilities": [Capability.FINANCE, Capability.MATHEMATICS],
        "ram_required": 6.7,
        "gpu_vram_weights_gb": 5.7,
        "gpu_vram_workspace_gb": 0.5,
        "cpu_ram_required": 0.5,
        "disk_size_gb": 7.8,
        "kv_cache_per_1k_tokens": 0.08,
        "load_time": 2.0,
        "latency": 0.035,
        "quality": 0.89,
        "offline": True,
        "architecture": "LlamaForCausalLM",
        "parameters_billion": 8.0,
        "quantization": "Q6_K",
        "description": "Quantitative risk modeling, Black-Scholes options pricing, financial statement ratios, and macro forecasting.",
    },
    {
        "id": "synthesizer-master",
        "name": "Command-R-Synthesizer-14B",
        "capabilities": [Capability.SYNTHESIS, Capability.GENERAL, Capability.WRITING],
        "ram_required": 7.6,
        "gpu_vram_weights_gb": 6.5,
        "gpu_vram_workspace_gb": 0.6,
        "cpu_ram_required": 0.5,
        "disk_size_gb": 9.1,
        "kv_cache_per_1k_tokens": 0.08,
        "load_time": 2.7,
        "latency": 0.046,
        "quality": 0.96,
        "offline": True,
        "architecture": "CohereForCausalLM",
        "parameters_billion": 14.0,
        "quantization": "Q4_K_M",
        "description": "Comprehensive document synthesis, executive reporting, cross-domain reconciliation, and final publication writing.",
    },
]


class ModelCatalog:
    """Manages the full open-weight model library."""

    def __init__(self, manifests_dir: Optional[str] = None):
        self._models: Dict[str, ModelManifest] = {}
        self._manifests_dir = manifests_dir
        self.load_defaults()
        if manifests_dir and os.path.isdir(manifests_dir):
            self.load_from_directory(manifests_dir)

    def load_defaults(self) -> None:
        """Populates the catalog with the 10 reference specialist models (52.7 GB total)."""
        for item in DEFAULT_MODELS:
            manifest = ModelManifest(**item)
            self._models[manifest.id] = manifest

    def register(self, manifest: ModelManifest) -> None:
        """Registers or updates a model manifest in the catalog."""
        self._models[manifest.id] = manifest

    def get(self, model_id: str) -> Optional[ModelManifest]:
        """Retrieves a model manifest by ID."""
        return self._models.get(model_id)

    def all_models(self) -> List[ModelManifest]:
        """Returns all models in the library."""
        return list(self._models.values())

    def list_models(self) -> List[ModelManifest]:
        """Alias for all_models()."""
        return self.all_models()

    def get_by_capability(self, capability: Capability) -> List[ModelManifest]:
        """Returns all models capable of handling the target capability, sorted by match quality."""
        matches = [m for m in self._models.values() if capability in m.capabilities]
        return sorted(matches, key=lambda m: (m.capability_score(capability), m.quality), reverse=True)

    def total_library_size_gb(self) -> float:
        """Calculates total disk footprint of the library (sum of RAM requirements)."""
        return round(sum(m.ram_required for m in self._models.values()), 2)

    def load_from_directory(self, dir_path: str) -> int:
        """Loads YAML model manifests from a directory."""
        loaded = 0
        p = Path(dir_path)
        for yml_file in p.glob("*.yaml"):
            try:
                with open(yml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict) and "id" in data:
                        self.register(ModelManifest(**data))
                        loaded += 1
            except Exception as e:
                print(f"[ModelCatalog] Error loading {yml_file}: {e}")
        return loaded

    def save_to_directory(self, dir_path: str) -> None:
        """Saves current catalog models as YAML files to a directory."""
        os.makedirs(dir_path, exist_ok=True)
        for m in self._models.values():
            file_path = os.path.join(dir_path, f"{m.id}.yaml")
            data = m.model_dump(mode="json")
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, sort_keys=False)
