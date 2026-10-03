"""Enums and fundamental dataclasses for ModelVM."""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class Capability(str, Enum):
    """Cognitive capabilities provided by specialist models."""
    GENERAL = "general"
    RESEARCH = "research"
    SCIENCE = "science"
    MATHEMATICS = "mathematics"
    CODING = "coding"
    PHYSICS = "physics"
    VISION = "vision"
    SECURITY = "security"
    MEDICINE = "medicine"
    FINANCE = "finance"
    WRITING = "writing"
    DATA_ANALYSIS = "data_analysis"
    SYNTHESIS = "synthesis"


class PagingAction(str, Enum):
    """Actions performed by the Model Pager."""
    PAGE_IN = "PAGE_IN"
    PAGE_OUT = "PAGE_OUT"
    EVICT = "EVICT"
    CACHE_HIT = "CACHE_HIT"
    PREFETCH = "PREFETCH"
    PIN = "PIN"
    UNPIN = "UNPIN"


class ModelStatus(str, Enum):
    """Residency status of an open-weight model."""
    DISK = "DISK"             # In model library on storage
    LOADING = "LOADING"       # Being paged into RAM/VRAM
    RESIDENT = "RESIDENT"     # Loaded in active memory
    EXECUTING = "EXECUTING"   # Actively generating/inferring
    EVICTING = "EVICTING"     # Being unloaded from memory


class TaskStatus(str, Enum):
    """Status of an overarching task or subtask."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"


class AblationMode(str, Enum):
    """Configurations for the Critical Ablation Study (Section 13)."""
    A_STATIC_ROUTER = "A_STATIC_ROUTER"
    B_DYNAMIC_NO_CSP = "B_DYNAMIC_NO_CSP"
    C_DYNAMIC_WITH_CSP = "C_DYNAMIC_WITH_CSP"
    D_FULL_MODELVM = "D_FULL_MODELVM"


@dataclass
class PagingEvent:
    """Telemetry log record for memory management actions."""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    action: PagingAction = PagingAction.PAGE_IN
    model_id: str = ""
    ram_gb: float = 0.0
    active_memory_gb: float = 0.0
    memory_budget_gb: float = 8.0
    reason: str = ""
    duration_sec: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "action": self.action.value,
            "model_id": self.model_id,
            "ram_gb": round(self.ram_gb, 2),
            "active_memory_gb": round(self.active_memory_gb, 2),
            "memory_budget_gb": round(self.memory_budget_gb, 2),
            "reason": self.reason,
            "duration_sec": round(self.duration_sec, 3),
            "metadata": self.metadata,
        }
