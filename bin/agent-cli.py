#!/usr/bin/env python3
"""
ClawCrew Agent CLI - Unified entry point for all sub-agents.

Usage:
    ./bin/agent-cli.py --agent design --task "Design a REST API for user auth"
    ./bin/agent-cli.py -a code -t "Implement the auth module" -o artifacts/task-123/auth.py
    ./bin/agent-cli.py -a test -t "Write tests for auth.py" --context artifacts/task-123/auth.py
"""

import typer
import json
import os
import sys
import uuid
import httpx
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

app = typer.Typer(add_completion=False, help="ClawCrew Agent CLI - Run specialized agents")

# Project root (parent of bin/)
BASE_DIR = Path(__file__).parent.parent

# Agent → workspace mapping
AGENT_WORKSPACES = {
    "orca": "workspace-orca",
    "design": "workspace-design",
    "code": "workspace-code",
    "test": "workspace-test",
    # Future agents can be added here
}

# OpenClaw Gateway config
OPENCLAW_CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"


def get_gateway_config() -> tuple[str, str]:
    """Get gateway URL and auth token from openclaw.json"""
    if not OPENCLAW_CONFIG_PATH.exists():
        raise typer.Exit("OpenClaw config not found. Please install OpenClaw first.")

    config = json.loads(OPENCLAW_CONFIG_PATH.read_text())
    port = config.get("gateway", {}).get("port", 18789)
    token = config.get("gateway", {}).get("auth", {}).get("token", "")

    return f"http://127.0.0.1:{port}", token


def get_workspace(agent_name: str) -> Path:
    """Get workspace path for an agent"""
    if agent_name not in AGENT_WORKSPACES:
        available = ", ".join(AGENT_WORKSPACES.keys())
        raise typer.BadParameter(f"Unknown agent: {agent_name}. Available: {available}")

    # Check in BASE_DIR first (dev mode), then in ~/.openclaw (installed mode)
    ws_path = BASE_DIR / AGENT_WORKSPACES[agent_name]
    if not ws_path.exists():
        ws_path = Path.home() / ".openclaw" / AGENT_WORKSPACES[agent_name]

    if not ws_path.exists():
        raise typer.BadParameter(f"Workspace not found: {ws_path}")

    return ws_path


def load_soul(ws: Path) -> str:
    """Load SOUL.md from workspace"""
    soul_path = ws / "SOUL.md"
    if soul_path.exists():
        return soul_path.read_text(encoding="utf-8")

    # Create default SOUL if not exists
    default_soul = f"# {ws.name}\n\nYou are a helpful specialist agent."
    soul_path.write_text(default_soul, encoding="utf-8")
    return default_soul


def load_memory(ws: Path, days: int = 7) -> str:
    """Load recent memories from memory/YYYY-MM-DD.md files"""
    memory_dir = ws / "memory"
    if not memory_dir.exists():
        return ""

    memories = []
    today = datetime.now().date()

    # Load memories from recent days
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        memory_file = memory_dir / f"{date_str}.md"

        if memory_file.exists():
            content = memory_file.read_text(encoding="utf-8").strip()
            if content:
                memories.append(f"## {date_str}\n{content}")

    if not memories:
        return ""

    return "\n\n".join(memories)


def save_memory(ws: Path, task_id: str, task: str, output_file: Optional[str], lesson: str):
    """Append a memory entry to memory/YYYY-MM-DD.md"""
    memory_dir = ws / "memory"
    memory_dir.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = memory_dir / f"{today}.md"

    timestamp = datetime.now().strftime("%H:%M:%S")

    entry = f"""
### {timestamp} - {task_id}

**Task:** {task[:200]}

**Output:** {output_file or 'stdout'}

**Lesson:** {lesson}

---
"""

    # Append to today's file
    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(entry)


def call_llm(prompt: str, model: str = "anthropic/claude-sonnet-4-5") -> str:
    """Call LLM via OpenClaw gateway"""
    gateway_url, token = get_gateway_config()

    try:
        response = httpx.post(
            f"{gateway_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 8192,
            },
            timeout=300.0,
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except httpx.HTTPError as e:
        typer.echo(f"Error calling LLM: {e}", err=True)
        raise typer.Exit(1)


def extract_output(response: str) -> str:
    """Extract content between ---OUTPUT--- markers if present"""
    if "---OUTPUT---" in response and "---END OUTPUT---" in response:
        return response.split("---OUTPUT---")[1].split("---END OUTPUT---")[0].strip()
    return response


@app.command()
def run(
    agent: str = typer.Option(..., "--agent", "-a", help="Agent name: design, code, test"),
    task: str = typer.Option(..., "--task", "-t", help="Task description"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Context file to read"),
    task_id: Optional[str] = typer.Option(None, "--task-id", help="Task ID for tracking"),
    model: str = typer.Option("anthropic/claude-sonnet-4-5", "--model", "-m", help="Model to use"),
    no_memory: bool = typer.Option(False, "--no-memory", help="Skip memory loading/saving"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run a specialized agent with a task.

    Examples:
        ./bin/agent-cli.py -a design -t "Design REST API for user auth"
        ./bin/agent-cli.py -a code -t "Implement auth module" -c design.md -o auth.py
        ./bin/agent-cli.py -a test -t "Write tests" -c auth.py -o test_auth.py
    """
    # Generate task ID if not provided
    if not task_id:
        task_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + str(uuid.uuid4())[:8]

    # Get workspace
    ws = get_workspace(agent)

    if verbose:
        typer.echo(f"[{agent.upper()}] Workspace: {ws}")
        typer.echo(f"[{agent.upper()}] Task ID: {task_id}")

    # Load SOUL
    soul = load_soul(ws)

    # Load memory
    memory = "" if no_memory else load_memory(ws)

    # Load context file if provided
    context_content = ""
    if context:
        context_path = Path(context)
        if context_path.exists():
            context_content = f"\n\n## Context File: {context}\n```\n{context_path.read_text(encoding='utf-8')}\n```"
        else:
            typer.echo(f"Warning: Context file not found: {context}", err=True)

    # Build prompt
    memory_section = ""
    if memory:
        memory_section = f"""
## Recent Memories (lessons learned from past tasks)

{memory}
"""

    output_instruction = ""
    if output:
        output_instruction = f"""
## Output Instruction
Save your output to: {output}
Format your final deliverable between these markers:
---OUTPUT---
[Your complete output here - this will be saved to the file]
---END OUTPUT---
"""

    prompt = f"""{soul}

{memory_section}

## Current Task
Task ID: {task_id}
{task}
{context_content}
{output_instruction}

Respond professionally and concisely. Focus on delivering high-quality work.
"""

    if verbose:
        typer.echo(f"[{agent.upper()}] Calling LLM...")

    # Call LLM
    response = call_llm(prompt, model)

    # Extract and save output
    final_output = extract_output(response)

    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(final_output, encoding="utf-8")
        typer.echo(f"[{agent.upper()}] Output saved to: {output}")
    else:
        # Print response to stdout
        typer.echo(response)

    # Auto-reflection and memory update
    if not no_memory:
        lesson_prompt = f"""You just completed a task. Briefly summarize the key lesson or improvement for future similar tasks.

Task: {task[:500]}
Output summary: {final_output[:500]}...

Respond with ONE short sentence (max 100 chars) capturing the key lesson."""

        try:
            lesson = call_llm(lesson_prompt, "anthropic/claude-haiku-3")
            lesson = lesson.strip()[:100]
        except Exception:
            lesson = "Task completed successfully."

        save_memory(ws, task_id, task, output, lesson)

        if verbose:
            typer.echo(f"[{agent.upper()}] Memory updated: {lesson}")

    typer.echo(f"[{agent.upper()}] Task {task_id} completed.")


@app.command()
def list_agents():
    """List available agents and their workspaces"""
    typer.echo("Available agents:")
    for agent, ws_name in AGENT_WORKSPACES.items():
        ws = BASE_DIR / ws_name
        status = "✓" if ws.exists() else "✗"
        typer.echo(f"  {status} {agent:10} → {ws_name}")


@app.command()
def show_memory(
    agent: str = typer.Option(..., "--agent", "-a", help="Agent name"),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to show"),
):
    """Show recent memories for an agent"""
    ws = get_workspace(agent)
    memory = load_memory(ws, days)

    if not memory:
        typer.echo(f"No memories found for {agent} in the last {days} days")
        return

    typer.echo(f"Recent memories for {agent}:\n")
    typer.echo(memory)


@app.command()
def clear_memory(
    agent: str = typer.Option(..., "--agent", "-a", help="Agent name"),
    all_days: bool = typer.Option(False, "--all", help="Clear all memory files"),
):
    """Clear memories for an agent"""
    ws = get_workspace(agent)
    memory_dir = ws / "memory"

    if not memory_dir.exists():
        typer.echo(f"No memories to clear for {agent}")
        return

    if all_days:
        # Remove all memory files
        import shutil
        shutil.rmtree(memory_dir)
        typer.echo(f"Cleared all memories for {agent}")
    else:
        # Remove only today's file
        today = datetime.now().strftime("%Y-%m-%d")
        today_file = memory_dir / f"{today}.md"
        if today_file.exists():
            today_file.unlink()
            typer.echo(f"Cleared today's memories for {agent}")
        else:
            typer.echo(f"No memories to clear for {agent} today")


if __name__ == "__main__":
    app()
