"""
ClawCrew Dashboard API
FastAPI backend for agents, logs, token usage, and artifacts.
"""

import os
import json
import glob
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI(title="ClawCrew Dashboard API", version="1.0.0")

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
WORKSPACES = {
    "orca": BASE_DIR / "workspace-orca",
    "design": BASE_DIR / "workspace-design",
    "code": BASE_DIR / "workspace-code",
    "test": BASE_DIR / "workspace-test",
}

# Agent metadata
AGENT_META = {
    "orca": {"emoji": "🦑", "role": "Orchestrator", "color": "#6366f1"},
    "design": {"emoji": "🎨", "role": "Architect", "color": "#8b5cf6"},
    "code": {"emoji": "💻", "role": "Engineer", "color": "#3b82f6"},
    "test": {"emoji": "🧪", "role": "QA", "color": "#10b981"},
}

# In-memory state (in production, use Redis or DB)
agent_states = {
    "orca": {"status": "idle", "last_active": None, "current_task": None},
    "design": {"status": "idle", "last_active": None, "current_task": None},
    "code": {"status": "idle", "last_active": None, "current_task": None},
    "test": {"status": "idle", "last_active": None, "current_task": None},
}

# Token tracking (mock data, replace with real OpenClaw logs)
token_usage = {
    "total": 0,
    "by_agent": {"orca": 0, "design": 0, "code": 0, "test": 0},
    "history": [],  # [{timestamp, agent, tokens}]
}

# Log buffer
log_buffer = []


class AgentInfo(BaseModel):
    name: str
    emoji: str
    role: str
    status: str
    last_active: Optional[str]
    current_task: Optional[str]
    color: str


class TaskInfo(BaseModel):
    task_id: str
    title: str
    status: str
    created_at: str
    phases: list


class LogEntry(BaseModel):
    timestamp: str
    agent: str
    message: str
    level: str = "info"


def format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time string."""
    if dt is None:
        return "Never"
    delta = datetime.now() - dt
    if delta.seconds < 60:
        return "Just now"
    elif delta.seconds < 3600:
        mins = delta.seconds // 60
        return f"{mins} min ago"
    elif delta.seconds < 86400:
        hours = delta.seconds // 3600
        return f"{hours} hour ago"
    else:
        days = delta.days
        return f"{days} day ago"


def load_soul_summary(workspace_path: Path) -> str:
    """Load first few lines of SOUL.md as summary."""
    soul_file = workspace_path / "SOUL.md"
    if soul_file.exists():
        content = soul_file.read_text()
        lines = content.strip().split("\n")[:5]
        return "\n".join(lines)
    return "No SOUL.md found"


def load_recent_memory(workspace_path: Path, days: int = 3) -> list:
    """Load recent memory entries."""
    memory_dir = workspace_path / "memory"
    if not memory_dir.exists():
        return []

    entries = []
    today = datetime.now()
    for i in range(days):
        date = today - timedelta(days=i)
        filename = date.strftime("%Y-%m-%d.md")
        filepath = memory_dir / filename
        if filepath.exists():
            content = filepath.read_text()
            entries.append({"date": filename, "content": content[:500]})
    return entries


@app.get("/")
async def root():
    return {"message": "ClawCrew Dashboard API", "version": "1.0.0"}


@app.get("/api/agents")
async def get_agents() -> list[AgentInfo]:
    """Get all agents with their current status."""
    agents = []
    for name, workspace in WORKSPACES.items():
        meta = AGENT_META[name]
        state = agent_states[name]

        last_active_str = None
        if state["last_active"]:
            last_active_str = format_relative_time(state["last_active"])

        agents.append(AgentInfo(
            name=name,
            emoji=meta["emoji"],
            role=meta["role"],
            status=state["status"],
            last_active=last_active_str,
            current_task=state["current_task"],
            color=meta["color"],
        ))
    return agents


@app.get("/api/agents/{agent_name}")
async def get_agent_detail(agent_name: str):
    """Get detailed info for a specific agent."""
    if agent_name not in WORKSPACES:
        raise HTTPException(status_code=404, detail="Agent not found")

    workspace = WORKSPACES[agent_name]
    meta = AGENT_META[agent_name]
    state = agent_states[agent_name]

    return {
        "name": agent_name,
        "emoji": meta["emoji"],
        "role": meta["role"],
        "color": meta["color"],
        "status": state["status"],
        "last_active": format_relative_time(state["last_active"]) if state["last_active"] else "Never",
        "current_task": state["current_task"],
        "soul_summary": load_soul_summary(workspace),
        "recent_memory": load_recent_memory(workspace),
        "workspace_path": str(workspace),
    }


@app.post("/api/agents/{agent_name}/status")
async def update_agent_status(agent_name: str, status: str, task: Optional[str] = None):
    """Update agent status (called by agent-cli or orchestrator)."""
    if agent_name not in agent_states:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent_states[agent_name]["status"] = status
    agent_states[agent_name]["last_active"] = datetime.now()
    if task:
        agent_states[agent_name]["current_task"] = task

    # Add log entry
    log_buffer.append({
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "message": f"Status changed to {status}" + (f": {task}" if task else ""),
        "level": "info",
    })

    return {"success": True}


@app.get("/api/tasks")
async def get_tasks() -> list[TaskInfo]:
    """Get all tasks from artifacts directory."""
    tasks = []

    if not ARTIFACTS_DIR.exists():
        return tasks

    for task_dir in sorted(ARTIFACTS_DIR.iterdir(), reverse=True):
        if task_dir.is_dir():
            task_id = task_dir.name

            # Detect phases based on files
            phases = []
            files = list(task_dir.glob("*"))

            for f in files:
                if "design" in f.name.lower() or f.suffix == ".md":
                    phases.append({"name": "design", "status": "completed", "file": f.name})
                elif f.suffix == ".py" and "test" not in f.name.lower():
                    phases.append({"name": "code", "status": "completed", "file": f.name})
                elif "test" in f.name.lower():
                    phases.append({"name": "test", "status": "completed", "file": f.name})

            # Get creation time
            created = datetime.fromtimestamp(task_dir.stat().st_ctime)

            tasks.append(TaskInfo(
                task_id=task_id,
                title=f"Task {task_id[:8]}...",
                status="completed" if phases else "in_progress",
                created_at=created.isoformat(),
                phases=phases,
            ))

    return tasks[:20]  # Limit to recent 20


@app.get("/api/tasks/{task_id}")
async def get_task_detail(task_id: str):
    """Get detailed task info including artifacts."""
    task_dir = ARTIFACTS_DIR / task_id
    if not task_dir.exists():
        raise HTTPException(status_code=404, detail="Task not found")

    artifacts = []
    for f in task_dir.glob("**/*"):
        if f.is_file():
            artifacts.append({
                "name": f.name,
                "path": str(f.relative_to(ARTIFACTS_DIR)),
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            })

    return {
        "task_id": task_id,
        "artifacts": artifacts,
        "created_at": datetime.fromtimestamp(task_dir.stat().st_ctime).isoformat(),
    }


@app.get("/api/logs")
async def get_logs(limit: int = 100, agent: Optional[str] = None):
    """Get recent log entries."""
    logs = log_buffer[-limit:]
    if agent:
        logs = [l for l in logs if l["agent"] == agent]
    return logs


@app.post("/api/logs")
async def add_log(entry: LogEntry):
    """Add a log entry (called by agent-cli)."""
    log_buffer.append({
        "timestamp": entry.timestamp or datetime.now().isoformat(),
        "agent": entry.agent,
        "message": entry.message,
        "level": entry.level,
    })
    # Keep buffer size manageable
    if len(log_buffer) > 1000:
        log_buffer.pop(0)
    return {"success": True}


@app.get("/api/tokens")
async def get_token_usage():
    """Get token usage statistics."""
    return {
        "total": token_usage["total"],
        "by_agent": token_usage["by_agent"],
        "history": token_usage["history"][-50:],  # Last 50 entries
    }


@app.post("/api/tokens")
async def record_token_usage(agent: str, tokens: int):
    """Record token usage (called after LLM calls)."""
    token_usage["total"] += tokens
    if agent in token_usage["by_agent"]:
        token_usage["by_agent"][agent] += tokens

    token_usage["history"].append({
        "timestamp": datetime.now().isoformat(),
        "agent": agent,
        "tokens": tokens,
    })

    return {"success": True, "total": token_usage["total"]}


@app.get("/api/artifacts")
async def list_artifacts():
    """List all artifacts."""
    if not ARTIFACTS_DIR.exists():
        return {"tasks": [], "total_files": 0, "total_size": 0}

    tasks = []
    total_files = 0
    total_size = 0

    for task_dir in sorted(ARTIFACTS_DIR.iterdir(), reverse=True):
        if task_dir.is_dir():
            files = []
            for f in task_dir.glob("**/*"):
                if f.is_file():
                    files.append({
                        "name": f.name,
                        "path": str(f.relative_to(ARTIFACTS_DIR)),
                        "size": f.stat().st_size,
                        "type": f.suffix[1:] if f.suffix else "unknown",
                    })
                    total_files += 1
                    total_size += f.stat().st_size

            tasks.append({
                "task_id": task_dir.name,
                "files": files,
            })

    return {"tasks": tasks[:20], "total_files": total_files, "total_size": total_size}


@app.get("/api/artifacts/{task_id}/{filename:path}")
async def get_artifact_content(task_id: str, filename: str):
    """Get artifact file content."""
    filepath = ARTIFACTS_DIR / task_id / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Security: ensure path is within artifacts dir
    try:
        filepath.resolve().relative_to(ARTIFACTS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    content = filepath.read_text()
    return {
        "filename": filename,
        "content": content,
        "size": filepath.stat().st_size,
        "type": filepath.suffix[1:] if filepath.suffix else "txt",
    }


@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics."""
    # Count tasks
    task_count = 0
    if ARTIFACTS_DIR.exists():
        task_count = len([d for d in ARTIFACTS_DIR.iterdir() if d.is_dir()])

    # Agent stats
    running = sum(1 for s in agent_states.values() if s["status"] == "running")
    idle = sum(1 for s in agent_states.values() if s["status"] == "idle")
    error = sum(1 for s in agent_states.values() if s["status"] == "error")

    return {
        "total_tasks": task_count,
        "agents_running": running,
        "agents_idle": idle,
        "agents_error": error,
        "total_tokens": token_usage["total"],
        "log_count": len(log_buffer),
    }


# Demo data generation for testing
@app.post("/api/demo/generate")
async def generate_demo_data():
    """Generate demo data for testing the dashboard."""
    global log_buffer, token_usage, agent_states

    # Simulate a workflow
    now = datetime.now()

    # Update agent states
    agent_states["orca"]["status"] = "running"
    agent_states["orca"]["last_active"] = now
    agent_states["orca"]["current_task"] = "Create email validation function"

    agent_states["design"]["status"] = "completed"
    agent_states["design"]["last_active"] = now - timedelta(minutes=5)

    agent_states["code"]["status"] = "running"
    agent_states["code"]["last_active"] = now - timedelta(minutes=2)
    agent_states["code"]["current_task"] = "Implementing validation logic"

    agent_states["test"]["status"] = "idle"
    agent_states["test"]["last_active"] = now - timedelta(minutes=30)

    # Generate logs
    demo_logs = [
        {"agent": "orca", "message": "Received task: Create email validation function", "level": "info"},
        {"agent": "orca", "message": "task_id = 20240214-153042", "level": "info"},
        {"agent": "orca", "message": "Calling DesignBot: ./bin/agent-cli.py --agent design api-spec ...", "level": "info"},
        {"agent": "design", "message": "Analyzing requirements...", "level": "info"},
        {"agent": "design", "message": "Output saved to artifacts/20240214-153042/design.md", "level": "success"},
        {"agent": "orca", "message": "Quality gate passed -> Calling CodeBot ...", "level": "info"},
        {"agent": "code", "message": "Implementing email validation with regex pattern", "level": "info"},
        {"agent": "code", "message": "Adding type hints and docstrings", "level": "info"},
    ]

    log_buffer = []
    for i, log in enumerate(demo_logs):
        log_buffer.append({
            "timestamp": (now - timedelta(minutes=len(demo_logs)-i)).isoformat(),
            **log,
        })

    # Generate token usage
    token_usage = {
        "total": 15420,
        "by_agent": {"orca": 4200, "design": 3800, "code": 5120, "test": 2300},
        "history": [
            {"timestamp": (now - timedelta(minutes=i*5)).isoformat(), "agent": random.choice(["orca", "design", "code", "test"]), "tokens": random.randint(100, 500)}
            for i in range(20)
        ],
    }

    return {"success": True, "message": "Demo data generated"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
