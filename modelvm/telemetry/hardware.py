"""Hardware Telemetry and Resource Profiler.

Captures real-time physical hardware metrics:
- Wall-clock page-in / page-out transition latency
- Host process RSS (Resident Set Size) memory
- Delta GPU VRAM (pre-load, post-load, peak, post-unload)
- Non-intrusive probe with automatic fallback for CPU/virtualized environments
"""

from __future__ import annotations
import os
import subprocess
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

try:
    import torch
    _HAS_TORCH_CUDA = torch.cuda.is_available()
except ImportError:
    _HAS_TORCH_CUDA = False


class MemorySnapshot(BaseModel):
    """Point-in-time hardware memory measurement."""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    process_rss_mb: float = Field(description="Host process resident set size in MB")
    gpu_vram_used_mb: float = Field(default=0.0, description="GPU VRAM currently allocated in MB")
    gpu_vram_reserved_mb: float = Field(default=0.0, description="GPU VRAM reserved by runtime in MB")
    gpu_vram_total_mb: float = Field(default=0.0, description="Total physical GPU VRAM in MB")
    device_name: str = Field(default="CPU/Host", description="Hardware device probed")


class TransitionTelemetry(BaseModel):
    """Telemetry captured across a model page-in, page-out, or prefetch transition."""
    model_id: str
    action: str  # "PAGE_IN", "PAGE_OUT", "PREFETCH"
    start_time: float
    end_time: float
    wall_clock_duration_sec: float
    
    # Host RSS Memory Deltas
    pre_rss_mb: float
    post_rss_mb: float
    delta_rss_mb: float
    
    # GPU VRAM Deltas
    pre_vram_mb: float
    post_vram_mb: float
    delta_vram_mb: float
    peak_vram_mb: float


class HardwareTelemetry:
    """Manages physical hardware telemetry and transitions profiling."""

    def __init__(self):
        self._process = psutil.Process() if _HAS_PSUTIL else None
        self._history: List[TransitionTelemetry] = []
        self._baseline_snapshot = self.take_snapshot()

    def get_process_rss_mb(self) -> float:
        """Returns current host process resident set size in megabytes."""
        if self._process is not None:
            try:
                return round(self._process.memory_info().rss / (1024.0 * 1024.0), 2)
            except Exception:
                pass
        return 0.0

    def get_gpu_vram_mb(self) -> Tuple[float, float, float, str]:
        """Returns (allocated_mb, reserved_mb, total_mb, device_name)."""
        if _HAS_TORCH_CUDA:
            try:
                allocated = torch.cuda.memory_allocated() / (1024.0 * 1024.0)
                reserved = torch.cuda.memory_reserved() / (1024.0 * 1024.0)
                total = torch.cuda.get_device_properties(0).total_memory / (1024.0 * 1024.0)
                device_name = torch.cuda.get_device_name(0)
                return round(allocated, 2), round(reserved, 2), round(total, 2), device_name
            except Exception:
                pass

        # Subprocess probe via nvidia-smi as fallback
        try:
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total,name", "--format=csv,nounits,noheader"],
                capture_output=True,
                text=True,
                timeout=1,
            )
            if res.returncode == 0:
                parts = [p.strip() for p in res.stdout.strip().split(",")]
                if len(parts) >= 3:
                    return float(parts[0]), float(parts[0]), float(parts[1]), parts[2]
        except Exception:
            pass

        return 0.0, 0.0, 0.0, "Host / Virtual Emulated"

    def take_snapshot(self) -> MemorySnapshot:
        """Takes an instantaneous snapshot of physical system resources."""
        rss = self.get_process_rss_mb()
        alloc, reserved, total, dev = self.get_gpu_vram_mb()
        return MemorySnapshot(
            process_rss_mb=rss,
            gpu_vram_used_mb=alloc,
            gpu_vram_reserved_mb=reserved,
            gpu_vram_total_mb=total,
            device_name=dev,
        )

    def measure_transition(
        self,
        model_id: str,
        action: str,
        transition_fn: Callable[[], Any],
    ) -> Tuple[Any, TransitionTelemetry]:
        """Profiles a model transition function, recording duration, RSS delta, and VRAM delta."""
        pre_snap = self.take_snapshot()
        t_start = time.perf_counter()

        # Execute transition callback
        result = transition_fn()

        t_end = time.perf_counter()
        post_snap = self.take_snapshot()
        duration = round(t_end - t_start, 4)

        delta_rss = round(post_snap.process_rss_mb - pre_snap.process_rss_mb, 2)
        delta_vram = round(post_snap.gpu_vram_used_mb - pre_snap.gpu_vram_used_mb, 2)
        peak_vram = max(pre_snap.gpu_vram_used_mb, post_snap.gpu_vram_used_mb)

        telemetry = TransitionTelemetry(
            model_id=model_id,
            action=action,
            start_time=t_start,
            end_time=t_end,
            wall_clock_duration_sec=duration,
            pre_rss_mb=pre_snap.process_rss_mb,
            post_rss_mb=post_snap.process_rss_mb,
            delta_rss_mb=delta_rss,
            pre_vram_mb=pre_snap.gpu_vram_used_mb,
            post_vram_mb=post_snap.gpu_vram_used_mb,
            delta_vram_mb=delta_vram,
            peak_vram_mb=peak_vram,
        )
        self._history.append(telemetry)
        return result, telemetry

    def get_history(self) -> List[TransitionTelemetry]:
        """Returns the full record of measured transitions."""
        return list(self._history)

    def reset(self) -> None:
        """Clears transition history and refreshes baseline."""
        self._history.clear()
        self._baseline_snapshot = self.take_snapshot()
