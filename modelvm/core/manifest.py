"""Model manifest schema and loader for the ModelVM Library."""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from modelvm.core.types import Capability, ModelStatus


class ModelManifest(BaseModel):
    """Specification of an open-weight model registered in ModelVM."""
    id: str = Field(description="Unique model identifier, e.g. 'qwen-math-7b'")
    name: str = Field(description="Human readable model name")
    path: str = Field(default="", description="Local file path or HuggingFace/Ollama identifier")
    capabilities: List[Capability] = Field(default_factory=list, description="Capabilities supported by the model")
    ram_required: float = Field(description="Active RAM/VRAM footprint in gigabytes")
    load_time: float = Field(description="Typical page-in / cold load latency in seconds")
    latency: float = Field(default=0.04, description="Inference latency per token in seconds")
    quality: float = Field(default=0.90, ge=0.0, le=1.0, description="Normalized benchmark quality score (0.0 - 1.0)")
    offline: bool = Field(default=True, description="Whether the model executes fully offline locally")
    
    # Precise multi-tier memory accounting (P1)
    gpu_vram_weights_gb: Optional[float] = Field(default=None, description="VRAM allocated for model weights in GB")
    gpu_vram_workspace_gb: float = Field(default=0.4, description="CUDA workspace & activation buffer in GB")
    cpu_ram_required: float = Field(default=0.5, description="Host CPU memory for tokenizers and runtime in GB")
    disk_size_gb: Optional[float] = Field(default=None, description="Storage footprint on SSD/NVMe in GB")
    kv_cache_per_1k_tokens: float = Field(default=0.08, description="VRAM required per 1,000 context tokens in GB")

    # Empirical benchmark profiling (Addresses Reviewer Attack 3)
    empirical_capabilities: Dict[str, float] = Field(
        default_factory=dict,
        description="Empirically measured capability scores per domain from held-out benchmarks"
    )

    # Extended systems metadata
    architecture: str = Field(default="decoder-only", description="Transformer architecture or variant")
    parameters_billion: float = Field(default=7.0, description="Parameter count in billions")
    quantization: str = Field(default="Q4_K_M", description="Quantization format (e.g. Q4_K_M, Q8, FP16)")
    context_window: int = Field(default=8192, description="Maximum context window tokens")
    energy_cost_factor: float = Field(default=1.0, description="Relative computational/energy factor")
    description: str = Field(default="", description="Summary of domain specialization")
    
    # Runtime status (transient)
    status: ModelStatus = Field(default=ModelStatus.DISK, description="Current memory residency status")
    last_accessed: float = Field(default=0.0, description="Timestamp of last execution")
    access_count: int = Field(default=0, description="Number of times model was paged in")

    @property
    def peak_gpu_vram_gb(self) -> float:
        """Peak active GPU VRAM requirement (weights + workspace buffer)."""
        w = self.gpu_vram_weights_gb if self.gpu_vram_weights_gb is not None else max(0.1, round(self.ram_required - self.cpu_ram_required, 2))
        return round(w + self.gpu_vram_workspace_gb, 2)

    @property
    def effective_disk_size_gb(self) -> float:
        """Effective storage footprint on disk/NVMe."""
        return self.disk_size_gb if self.disk_size_gb is not None else round(self.ram_required * 1.1, 2)

    def capability_score(self, target: Capability) -> float:
        """Returns empirical capability score if available, or primary/secondary match score."""
        target_key = target.value if hasattr(target, "value") else str(target)
        if target_key in self.empirical_capabilities:
            return float(self.empirical_capabilities[target_key])
        if not self.capabilities:
            return 0.0
        if self.capabilities[0] == target:
            return 1.0
        if target in self.capabilities:
            return 0.75
        # General models have baseline fallback capability
        if Capability.GENERAL in self.capabilities:
            return 0.50
        return 0.05
