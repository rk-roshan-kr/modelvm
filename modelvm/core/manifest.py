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

    def capability_score(self, target: Capability) -> float:
        """Returns primary or secondary capability match score (0.0 to 1.0)."""
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
