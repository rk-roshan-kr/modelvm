"""FastAPI Web and WebSocket server for ModelVM Interactive Visualizer."""

from __future__ import annotations
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from modelvm.benchmark.ablation import AblationStudyRunner
from modelvm.core.types import AblationMode, PagingEvent
from modelvm.executor.kernel import CognitiveKernel, StageExecutionResult, TaskExecutionSummary
from modelvm.registry.catalog import ModelCatalog


app = FastAPI(title="ModelVM API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared kernel instance
catalog = ModelCatalog()
kernel = CognitiveKernel(catalog=catalog, memory_budget_gb=8.0)


class ConnectionManager:
    """Manages active WebSocket connections to push live telemetry."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                pass


manager = ConnectionManager()


# Register event listeners to broadcast paging and stage updates over WebSocket
def on_paging_event(event: PagingEvent):
    payload = {
        "type": "PAGING_EVENT",
        "data": event.to_dict(),
        "memory_status": kernel.pager.get_status(),
    }
    # Run in event loop safely
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast(payload))
    except RuntimeError:
        pass


def on_stage_event(stage: StageExecutionResult):
    payload = {
        "type": "STAGE_COMPLETED",
        "data": stage.model_dump(),
        "memory_status": kernel.pager.get_status(),
    }
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast(payload))
    except RuntimeError:
        pass


kernel.pager.add_listener(on_paging_event)
kernel.add_stage_listener(on_stage_event)


# Request schemas
class RunTaskRequest(BaseModel):
    goal: str = Field(default="Analyze this scientific paper, reproduce its numerical result, write the implementation, and explain the physical meaning.")
    budget_gb: float = Field(default=8.0)
    ablation_mode: AblationMode = Field(default=AblationMode.D_FULL_MODELVM)


class PagingRequest(BaseModel):
    model_id: str


class BudgetRequest(BaseModel):
    budget_gb: float


# REST Endpoints
@app.get("/api/status")
async def get_status():
    """Returns memory and residency status."""
    return kernel.pager.get_status()


@app.get("/api/models")
async def get_models():
    """Returns all models in the library."""
    return [m.model_dump(mode="json") for m in catalog.all_models()]


@app.post("/api/budget")
async def update_budget(req: BudgetRequest):
    """Dynamically updates the active memory budget."""
    kernel.pager.memory_budget_gb = req.budget_gb
    return kernel.pager.get_status()


@app.post("/api/page_in")
async def manual_page_in(req: PagingRequest):
    """Manually pages a model into active memory."""
    event = kernel.pager.page_in(req.model_id)
    return {"event": event.to_dict(), "status": kernel.pager.get_status()}


@app.post("/api/page_out")
async def manual_page_out(req: PagingRequest):
    """Manually unloads a model from memory."""
    event = kernel.pager.page_out(req.model_id)
    return {"event": event.to_dict(), "status": kernel.pager.get_status()}


@app.post("/api/run")
async def run_task(req: RunTaskRequest):
    """Executes a cognitive task."""
    kernel.pager.memory_budget_gb = req.budget_gb
    summary = kernel.execute_task(goal=req.goal, ablation_mode=req.ablation_mode)
    
    # Broadcast completion
    await manager.broadcast({
        "type": "TASK_FINISHED",
        "summary": summary.model_dump(),
        "memory_status": kernel.pager.get_status(),
    })
    
    return summary.model_dump()


@app.post("/api/ablation")
async def run_ablation(req: RunTaskRequest):
    """Runs the 4-mode Critical Ablation Study."""
    runner = AblationStudyRunner(memory_budget_gb=req.budget_gb)
    report = runner.run_study(task_goal=req.goal)
    return report.model_dump()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket stream for real-time live visualizer updates."""
    await manager.connect(websocket)
    # Send initial state
    await websocket.send_text(json.dumps({
        "type": "INITIAL_STATE",
        "memory_status": kernel.pager.get_status(),
        "models": [m.model_dump(mode="json") for m in catalog.all_models()],
    }))
    try:
        while True:
            data = await websocket.receive_text()
            # Can receive ping or interactive commands
            try:
                msg = json.loads(data)
                if msg.get("action") == "PING":
                    await websocket.send_text(json.dumps({"type": "PONG"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Mount static visualizer web app
web_dir = Path(__file__).resolve().parent.parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(web_dir / "index.html"))
