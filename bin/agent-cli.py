#!/usr/bin/env python3
"""
ClawCrew Agent CLI

A unified command-line interface for running specialized AI agents.
Each agent has its own workspace with SOUL.md (personality) and memory/ (lessons learned).

Usage:
    ./bin/agent-cli.py run -a design -t "Design a REST API"
    ./bin/agent-cli.py run -a code -t "Implement module" -c design.md -o main.py
    ./bin/agent-cli.py run -a test -t "Write tests" -c main.py -o test_main.py
    ./bin/agent-cli.py list-agents
    ./bin/agent-cli.py show-memory -a design
    ./bin/agent-cli.py clear-memory -a design --all

Agents:
    design  - System Architect: API design, data models, specifications
    code    - Software Engineer: Implementation, coding
    test    - QA Engineer: Testing, coverage, bug finding
    orca    - Orchestrator: Coordinates other agents (used by OrcaBot)

Memory System:
    Each agent stores lessons learned in memory/YYYY-MM-DD.md files.
    Memories are automatically loaded when running tasks and updated after completion.

More info: https://github.com/lanxindeng8/clawcrew
"""

import typer
import json
import uuid
import subprocess
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# GitHub utilities (separated for clarity)
from github_utils import (
    parse_github_url,
    clone_repository,
    find_key_files,
    build_repo_context,
)

# Enable -h as help shortcut
app = typer.Typer(
    add_completion=False,
    help="ClawCrew Agent CLI - Run specialized AI agents",
    context_settings={"help_option_names": ["-h", "--help"]},
)

# =============================================================================
# Configuration
# =============================================================================

# Project root (parent of bin/)
BASE_DIR = Path(__file__).parent.parent

# Agent name → workspace directory mapping
# To add a new agent, just add a line here and create the workspace folder
AGENT_WORKSPACES = {
    "orca": "workspace-orca",
    "design": "workspace-design",
    "code": "workspace-code",
    "test": "workspace-test",
    "repo": "workspace-repo",
}

# =============================================================================
# Helper Functions
# =============================================================================

def get_workspace(agent_name: str) -> Path:
    """
    Get workspace path for an agent.

    Checks BASE_DIR first (dev mode), then ~/.openclaw (installed mode).

    Args:
        agent_name: Name of the agent (design, code, test, orca)

    Returns:
        Path to the workspace directory

    Raises:
        typer.BadParameter: If agent unknown or workspace not found
    """
    if agent_name not in AGENT_WORKSPACES:
        available = ", ".join(AGENT_WORKSPACES.keys())
        raise typer.BadParameter(f"Unknown agent: {agent_name}. Available: {available}")

    # Check dev mode first, then installed mode
    ws_path = BASE_DIR / AGENT_WORKSPACES[agent_name]
    if not ws_path.exists():
        ws_path = Path.home() / ".openclaw" / AGENT_WORKSPACES[agent_name]

    if not ws_path.exists():
        raise typer.BadParameter(f"Workspace not found: {ws_path}")

    return ws_path


def load_soul(ws: Path) -> str:
    """
    Load SOUL.md from workspace.

    SOUL.md defines the agent's personality, responsibilities, and output format.
    Creates a default SOUL if not exists.

    Args:
        ws: Workspace path

    Returns:
        Content of SOUL.md
    """
    soul_path = ws / "SOUL.md"
    if soul_path.exists():
        return soul_path.read_text(encoding="utf-8")

    # Create default SOUL if not exists
    default_soul = f"# {ws.name}\n\nYou are a helpful specialist agent."
    soul_path.write_text(default_soul, encoding="utf-8")
    return default_soul


def load_memory(ws: Path, days: int = 7) -> str:
    """
    Load recent memories from memory/YYYY-MM-DD.md files.

    Memories contain lessons learned from past tasks, helping agents improve over time.

    Args:
        ws: Workspace path
        days: Number of days to look back

    Returns:
        Combined memory content as markdown string
    """
    memory_dir = ws / "memory"
    if not memory_dir.exists():
        return ""

    memories = []
    today = datetime.now().date()

    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        memory_file = memory_dir / f"{date_str}.md"

        if memory_file.exists():
            content = memory_file.read_text(encoding="utf-8").strip()
            if content:
                memories.append(f"## {date_str}\n{content}")

    return "\n\n".join(memories) if memories else ""


def save_memory(ws: Path, task_id: str, task: str, output_file: Optional[str], lesson: str):
    """
    Append a memory entry to today's memory file.

    Memory format:
        ### HH:MM:SS - task_id
        **Task:** ...
        **Output:** ...
        **Lesson:** ...

    Args:
        ws: Workspace path
        task_id: Unique task identifier
        task: Task description
        output_file: Output file path (or None)
        lesson: Lesson learned from this task
    """
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

    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(entry)


def call_llm(message: str, agent_name: str = "main") -> str:
    """
    Call LLM via OpenClaw agent command.

    Uses `openclaw agent --agent <name>` which:
    - Loads the agent's SOUL.md from its workspace
    - Uses the configured Anthropic OAuth
    - Returns the agent's response

    Args:
        message: The message/task to send
        agent_name: OpenClaw agent ID (orca, design, code, test, or main)

    Returns:
        LLM response content

    Raises:
        typer.Exit: On subprocess errors
    """
    try:
        result = subprocess.run(
            [
                "openclaw", "agent",
                "--agent", agent_name,
                "--local",
                "--message", message,
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            typer.echo(f"Error calling LLM: {result.stderr}", err=True)
            raise typer.Exit(1)

        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        typer.echo("Error: LLM call timed out", err=True)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("Error: openclaw command not found. Please install OpenClaw first.", err=True)
        raise typer.Exit(1)


def extract_output(response: str) -> str:
    """
    Extract content between ---OUTPUT--- and ---END OUTPUT--- markers.

    If markers not found, returns the full response.

    Args:
        response: LLM response text

    Returns:
        Extracted output or full response
    """
    if "---OUTPUT---" in response and "---END OUTPUT---" in response:
        return response.split("---OUTPUT---")[1].split("---END OUTPUT---")[0].strip()
    return response


# =============================================================================
# Commands
# =============================================================================

@app.command()
def run(
    agent: str = typer.Option(..., "--agent", "-a", help="Agent name: design, code, test, orca"),
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

    The agent loads its SOUL.md (personality) and recent memories,
    executes the task, saves output, and updates its memory with lessons learned.

    Examples:

        # Design an API
        ./bin/agent-cli.py run -a design -t "Design REST API for user auth"

        # Implement with context from design
        ./bin/agent-cli.py run -a code -t "Implement auth" -c design.md -o auth.py

        # Write tests
        ./bin/agent-cli.py run -a test -t "Write tests" -c auth.py -o test_auth.py
    """
    # Generate task ID if not provided
    if not task_id:
        task_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + str(uuid.uuid4())[:8]

    ws = get_workspace(agent)

    if verbose:
        typer.echo(f"[{agent.upper()}] Workspace: {ws}")
        typer.echo(f"[{agent.upper()}] Task ID: {task_id}")

    # Load memory (SOUL is loaded by OpenClaw automatically)
    memory = "" if no_memory else load_memory(ws)

    # Load context file if provided
    context_content = ""
    if context:
        context_path = Path(context)
        if context_path.exists():
            context_content = f"\n\n## Context File: {context}\n```\n{context_path.read_text(encoding='utf-8')}\n```"
        else:
            typer.echo(f"Warning: Context file not found: {context}", err=True)

    # Build message (SOUL is handled by OpenClaw, we just send task + context + memory)
    memory_section = f"\n## Recent Lessons Learned\n{memory}\n" if memory else ""
    output_instruction = ""
    if output:
        output_instruction = f"""

## Output Instruction
Format your final deliverable between these markers:
---OUTPUT---
[Your complete output here]
---END OUTPUT---
"""

    message = f"""## Task
Task ID: {task_id}
{task}
{context_content}
{memory_section}
{output_instruction}
"""

    if verbose:
        typer.echo(f"[{agent.upper()}] Calling OpenClaw agent...")

    # Call LLM via OpenClaw agent
    response = call_llm(message, agent)
    final_output = extract_output(response)

    # Save output
    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(final_output, encoding="utf-8")
        typer.echo(f"[{agent.upper()}] Output saved to: {output}")
    else:
        typer.echo(response)

    # Auto-reflection and memory update
    if not no_memory:
        lesson_prompt = f"""Briefly summarize the key lesson from this task in ONE sentence (max 100 chars).

Task: {task[:200]}
Output: {final_output[:200]}..."""

        try:
            lesson = call_llm(lesson_prompt, "main")
            lesson = lesson.strip()[:100]
        except Exception:
            lesson = "Task completed successfully."

        save_memory(ws, task_id, task, output, lesson)

        if verbose:
            typer.echo(f"[{agent.upper()}] Memory updated: {lesson}")

    typer.echo(f"[{agent.upper()}] Task {task_id} completed.")


@app.command("list-agents")
def list_agents():
    """List available agents and their workspace status."""
    typer.echo("Available agents:\n")
    typer.echo("  Agent       Workspace              Status")
    typer.echo("  " + "-" * 50)
    for agent, ws_name in AGENT_WORKSPACES.items():
        ws = BASE_DIR / ws_name
        installed_ws = Path.home() / ".openclaw" / ws_name
        if ws.exists():
            status = "✓ (dev)"
        elif installed_ws.exists():
            status = "✓ (installed)"
        else:
            status = "✗ not found"
        typer.echo(f"  {agent:10}  {ws_name:20}  {status}")


@app.command("show-memory")
def show_memory(
    agent: str = typer.Option(..., "--agent", "-a", help="Agent name"),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to show"),
):
    """Show recent memories for an agent."""
    ws = get_workspace(agent)
    memory = load_memory(ws, days)

    if not memory:
        typer.echo(f"No memories found for {agent} in the last {days} days")
        return

    typer.echo(f"Recent memories for {agent}:\n")
    typer.echo(memory)


@app.command("clear-memory")
def clear_memory(
    agent: str = typer.Option(..., "--agent", "-a", help="Agent name"),
    all_days: bool = typer.Option(False, "--all", help="Clear all memory files"),
):
    """Clear memories for an agent."""
    ws = get_workspace(agent)
    memory_dir = ws / "memory"

    if not memory_dir.exists():
        typer.echo(f"No memories to clear for {agent}")
        return

    if all_days:
        shutil.rmtree(memory_dir)
        typer.echo(f"Cleared all memories for {agent}")
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        today_file = memory_dir / f"{today}.md"
        if today_file.exists():
            today_file.unlink()
            typer.echo(f"Cleared today's memories for {agent}")
        else:
            typer.echo(f"No memories to clear for {agent} today")


@app.command("summarize-repo")
def summarize_repo(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="GitHub repository URL"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Local repository path"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    task_id: Optional[str] = typer.Option(None, "--task-id", help="Task ID for tracking"),
    keep_clone: bool = typer.Option(False, "--keep-clone", help="Don't delete cloned repo (for debugging)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Summarize a GitHub repository or local directory.

    Analyzes repository structure, tech stack, key files, and dependencies.
    Output is saved to artifacts or specified path.

    Examples:

        # Summarize a GitHub repo
        ./bin/agent-cli.py summarize-repo --url https://github.com/user/repo

        # Summarize with specific output
        ./bin/agent-cli.py summarize-repo -u https://github.com/user/repo -o summary.md

        # Summarize local directory
        ./bin/agent-cli.py summarize-repo --path /path/to/repo
    """
    # Validate input
    if not url and not path:
        typer.echo("Error: Must specify either --url or --path", err=True)
        raise typer.Exit(1)

    if url and path:
        typer.echo("Error: Cannot specify both --url and --path", err=True)
        raise typer.Exit(1)

    # Generate task ID
    if not task_id:
        task_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + str(uuid.uuid4())[:8]

    temp_dir = None
    repo_path = None
    repo_name = "local-repo"

    try:
        # Handle GitHub URL
        if url:
            try:
                owner, repo_name, clone_url = parse_github_url(url)
            except ValueError as e:
                typer.echo(f"Error: {e}", err=True)
                raise typer.Exit(1)

            if verbose:
                typer.echo(f"[REPO] Cloning {owner}/{repo_name}...")

            # Create temp directory
            temp_dir = Path(tempfile.mkdtemp(prefix="clawcrew-repo-"))
            repo_path = temp_dir / repo_name

            # Clone repository
            if not clone_repository(clone_url, repo_path):
                typer.echo("Error: Failed to clone repository. Is it public?", err=True)
                raise typer.Exit(1)

            if verbose:
                typer.echo(f"[REPO] Cloned to: {repo_path}")

        # Handle local path
        else:
            repo_path = Path(path).resolve()
            if not repo_path.exists():
                typer.echo(f"Error: Path does not exist: {path}", err=True)
                raise typer.Exit(1)
            if not repo_path.is_dir():
                typer.echo(f"Error: Path is not a directory: {path}", err=True)
                raise typer.Exit(1)
            repo_name = repo_path.name

            if verbose:
                typer.echo(f"[REPO] Analyzing local directory: {repo_path}")

        # Find key files
        if verbose:
            typer.echo("[REPO] Scanning for key files...")

        key_files = find_key_files(repo_path)

        if verbose:
            for category, files in key_files.items():
                if files:
                    typer.echo(f"[REPO] Found {len(files)} {category} files")

        # Build context
        if verbose:
            typer.echo("[REPO] Building analysis context...")

        context = build_repo_context(repo_path, key_files)

        # Build prompt for repo agent
        source = url if url else str(repo_path)
        prompt = f"""## Repository Analysis Task

Task ID: {task_id}

Analyze this repository and provide a comprehensive summary.

**Source:** {source}
**Repository Name:** {repo_name}

{context}

## Instructions

Analyze the repository structure, identify the tech stack, key files, and dependencies.
Follow your output format exactly.

Format your analysis between these markers:
---OUTPUT---
[Your complete analysis here]
---END OUTPUT---
"""

        # Call repo agent
        if verbose:
            typer.echo("[REPO] Calling repo agent for analysis...")

        response = call_llm(prompt, "repo")
        summary = extract_output(response)

        # Determine output path
        if output:
            out_path = Path(output)
        else:
            artifacts_dir = Path.home() / ".openclaw" / "artifacts" / task_id
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            out_path = artifacts_dir / "repo_summary.md"

        # Save output
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(summary, encoding="utf-8")

        typer.echo(f"[REPO] Summary saved to: {out_path}")
        typer.echo(f"[REPO] Task {task_id} completed.")

        # Also print summary if no output file specified by user
        if not output:
            typer.echo("\n" + "=" * 60)
            typer.echo(summary)

    finally:
        # Cleanup temp directory
        if temp_dir and temp_dir.exists() and not keep_clone:
            if verbose:
                typer.echo(f"[REPO] Cleaning up: {temp_dir}")
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    app()
