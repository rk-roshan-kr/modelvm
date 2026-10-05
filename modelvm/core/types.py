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


class FactorialConfig(str, Enum):
    """The 8 configurations of the 2^3 factorial matrix on the dynamic paging substrate,
    plus the external reference baseline.
    
    Factors:
    - Factor A: CSP in {0, 1}
    - Factor B: Predictive Working Set W(t, k) in {0, 1}
    - Factor C: Multi-Objective Scheduler in {0, 1}
    """
    REF_STATIC_MONOLITH = "REF_STATIC_MONOLITH"   # Paging: 0, CSP: 0, WS: 0, Sched: 0
    C0_PAGING_BASE = "C0_PAGING_BASE"             # Paging: 1, CSP: 0, WS: 0, Sched: 0
    C1_CSP = "C1_CSP"                             # Paging: 1, CSP: 1, WS: 0, Sched: 0
    C2_WS = "C2_WS"                               # Paging: 1, CSP: 0, WS: 1, Sched: 0
    C3_SCHEDULER = "C3_SCHEDULER"                 # Paging: 1, CSP: 0, WS: 0, Sched: 1
    C4_CSP_WS = "C4_CSP_WS"                       # Paging: 1, CSP: 1, WS: 1, Sched: 0
    C5_CSP_SCHEDULER = "C5_CSP_SCHEDULER"         # Paging: 1, CSP: 1, WS: 0, Sched: 1
    C6_WS_SCHEDULER = "C6_WS_SCHEDULER"           # Paging: 1, CSP: 0, WS: 1, Sched: 1
    C7_FULL_MODELVM = "C7_FULL_MODELVM"           # Paging: 1, CSP: 1, WS: 1, Sched: 1


class ExecutionMode(str, Enum):
    """Execution backend fidelity and enforcement mode."""
    SIMULATION = "SIMULATION"        # Explicitly synthetic deterministic emulation
    REAL = "REAL"                    # Real local inference (e.g., Ollama) with configurable fallback
    STRICT_REAL = "STRICT_REAL"      # Strict real execution: failures raise exceptions, never silently simulate


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
