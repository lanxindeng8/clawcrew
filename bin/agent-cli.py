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
    ./bin/agent-cli.py summarize-repo --url https://github.com/user/repo --task-id task-001
    ./bin/agent-cli.py read-files -r ~/.openclaw/artifacts/task-001/repo -f "src/api.py,tests/test_api.py"

Agents:
    design  - System Architect: API design, data models, specifications
    code    - Software Engineer: Implementation, coding
    test    - QA Engineer: Testing, coverage, bug finding
    orca    - Orchestrator: Coordinates other agents (used by OrcaBot)
    github  - GitHub Integration: Repo analysis, issues, PRs

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
    get_github_token,
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
    "github": "workspace-github",
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
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Specific branch to analyze"),
    pat: Optional[str] = typer.Option(None, "--pat", help="GitHub PAT for private repos (or set GITHUB_PAT env)"),
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

        # Summarize a specific branch
        ./bin/agent-cli.py summarize-repo -u https://github.com/user/repo -b develop

        # Summarize a private repo (PAT via flag)
        ./bin/agent-cli.py summarize-repo -u https://github.com/user/private-repo --pat ghp_xxx

        # Summarize a private repo (PAT via env)
        GITHUB_PAT=ghp_xxx ./bin/agent-cli.py summarize-repo -u https://github.com/user/private-repo

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

            # Get PAT (from --pat flag or environment)
            github_token = get_github_token(pat)

            branch_info = f" (branch: {branch})" if branch else ""
            auth_info = " [authenticated]" if github_token else ""
            if verbose:
                typer.echo(f"[GITHUB] Cloning {owner}/{repo_name}{branch_info}{auth_info}...")

            # Create temp directory
            temp_dir = Path(tempfile.mkdtemp(prefix="clawcrew-repo-"))
            repo_path = temp_dir / repo_name

            # Clone repository
            if not clone_repository(clone_url, repo_path, branch, github_token):
                error_msg = "Error: Failed to clone repository."
                if branch:
                    error_msg += f" Branch '{branch}' may not exist."
                elif not github_token:
                    error_msg += " Is it public? Use --pat for private repos."
                else:
                    error_msg += " Check your PAT permissions."
                typer.echo(error_msg, err=True)
                raise typer.Exit(1)

            if verbose:
                typer.echo(f"[GITHUB] Cloned to: {repo_path}")

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
                typer.echo(f"[GITHUB] Analyzing local directory: {repo_path}")

        # Find key files
        if verbose:
            typer.echo("[GITHUB] Scanning for key files...")

        key_files = find_key_files(repo_path)

        if verbose:
            for category, files in key_files.items():
                if files:
                    typer.echo(f"[GITHUB] Found {len(files)} {category} files")

        # Build context
        if verbose:
            typer.echo("[GITHUB] Building analysis context...")

        context = build_repo_context(repo_path, key_files)

        # Build prompt for repo agent
        source = url if url else str(repo_path)
        branch_line = f"\n**Branch:** {branch}" if branch else ""
        prompt = f"""## Repository Analysis Task

Task ID: {task_id}

Analyze this repository and provide a comprehensive summary.

**Source:** {source}
**Repository Name:** {repo_name}{branch_line}

{context}

## Instructions

Analyze the repository structure, identify the tech stack, key files, and dependencies.
Follow your output format exactly.

Format your analysis between these markers:
---OUTPUT---
[Your complete analysis here]
---END OUTPUT---
"""

        # Call github agent
        if verbose:
            typer.echo("[GITHUB] Calling github agent for analysis...")

        response = call_llm(prompt, "github")
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

        typer.echo(f"[GITHUB] Summary saved to: {out_path}")
        typer.echo(f"[GITHUB] Task {task_id} completed.")

        # Also print summary if no output file specified by user
        if not output:
            typer.echo("\n" + "=" * 60)
            typer.echo(summary)

    finally:
        # Cleanup temp directory (keep clone if task_id is provided, unless explicitly told not to)
        should_keep = keep_clone or (task_id is not None)
        if temp_dir and temp_dir.exists() and not should_keep:
            if verbose:
                typer.echo(f"[GITHUB] Cleaning up: {temp_dir}")
            shutil.rmtree(temp_dir, ignore_errors=True)
        elif temp_dir and should_keep:
            # Move clone to artifacts directory for persistence
            artifacts_dir = Path.home() / ".openclaw" / "artifacts" / task_id
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            clone_dest = artifacts_dir / "repo"
            if not clone_dest.exists() and repo_path and repo_path.exists():
                shutil.move(str(repo_path), str(clone_dest))
                if verbose:
                    typer.echo(f"[GITHUB] Clone saved to: {clone_dest}")


@app.command("read-files")
def read_files(
    repo_path: str = typer.Option(..., "--repo-path", "-r", help="Path to repository root"),
    files: str = typer.Option(..., "--files", "-f", help="Comma-separated file paths (relative to repo root)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    line_numbers: bool = typer.Option(True, "--line-numbers/--no-line-numbers", help="Include line numbers"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Read specific files from a repository and format for agent context.

    Outputs files with line numbers in a format suitable for agents to
    understand exact locations for modifications (Repo Mode).

    Examples:

        # Read specific files
        ./bin/agent-cli.py read-files -r ./repo -f "src/api.py,src/models.py"

        # Read and save to context file
        ./bin/agent-cli.py read-files -r ~/.openclaw/artifacts/task-001/repo \\
            -f "src/api.py,tests/test_api.py" -o repo_context.md

        # Read without line numbers
        ./bin/agent-cli.py read-files -r ./repo -f "README.md" --no-line-numbers
    """
    repo = Path(repo_path).resolve()

    if not repo.exists():
        typer.echo(f"Error: Repository path does not exist: {repo_path}", err=True)
        raise typer.Exit(1)

    if not repo.is_dir():
        typer.echo(f"Error: Path is not a directory: {repo_path}", err=True)
        raise typer.Exit(1)

    # Parse file list
    file_list = [f.strip() for f in files.split(",") if f.strip()]

    if not file_list:
        typer.echo("Error: No files specified", err=True)
        raise typer.Exit(1)

    if verbose:
        typer.echo(f"[READ-FILES] Reading {len(file_list)} files from {repo}")

    content_parts = ["# Repository File Contents\n"]
    content_parts.append(f"**Repository:** `{repo}`\n")
    content_parts.append(f"**Files:** {len(file_list)}\n\n")
    content_parts.append("---\n")

    files_read = 0
    files_missing = 0

    for file_path in file_list:
        full_path = repo / file_path

        if not full_path.exists():
            if verbose:
                typer.echo(f"[READ-FILES] Warning: File not found: {file_path}")
            content_parts.append(f"\n## File: {file_path}\n\n")
            content_parts.append("**Status:** File not found\n\n")
            files_missing += 1
            continue

        if not full_path.is_file():
            if verbose:
                typer.echo(f"[READ-FILES] Warning: Not a file: {file_path}")
            content_parts.append(f"\n## File: {file_path}\n\n")
            content_parts.append("**Status:** Not a regular file\n\n")
            files_missing += 1
            continue

        # Determine language for code fence
        ext = full_path.suffix.lower()
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".jsx": "jsx",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "zsh",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".json": "json",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".sql": "sql",
            ".md": "markdown",
            ".toml": "toml",
            ".ini": "ini",
            ".cfg": "ini",
        }
        lang = lang_map.get(ext, "")

        try:
            file_content = full_path.read_text(encoding="utf-8")
            lines = file_content.splitlines()

            content_parts.append(f"\n## File: {file_path}\n\n")
            content_parts.append(f"**Lines:** {len(lines)}\n\n")
            content_parts.append(f"```{lang}\n")

            if line_numbers:
                # Add line numbers
                width = len(str(len(lines)))
                for i, line in enumerate(lines, 1):
                    content_parts.append(f"{i:>{width}}: {line}\n")
            else:
                content_parts.append(file_content)
                if not file_content.endswith("\n"):
                    content_parts.append("\n")

            content_parts.append("```\n")
            files_read += 1

            if verbose:
                typer.echo(f"[READ-FILES] Read: {file_path} ({len(lines)} lines)")

        except UnicodeDecodeError:
            content_parts.append(f"\n## File: {file_path}\n\n")
            content_parts.append("**Status:** Binary file (cannot display)\n\n")
            files_missing += 1
        except Exception as e:
            content_parts.append(f"\n## File: {file_path}\n\n")
            content_parts.append(f"**Status:** Error reading file: {e}\n\n")
            files_missing += 1

    # Summary
    content_parts.append("\n---\n")
    content_parts.append(f"\n**Summary:** {files_read} files read, {files_missing} files missing/skipped\n")

    final_content = "".join(content_parts)

    # Output
    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(final_content, encoding="utf-8")
        typer.echo(f"[READ-FILES] Saved to: {output}")
    else:
        typer.echo(final_content)

    if files_read > 0:
        typer.echo(f"[READ-FILES] Done: {files_read} files read")
    else:
        typer.echo("[READ-FILES] Warning: No files were read successfully", err=True)


@app.command("read-issue")
def read_issue(
    repo: str = typer.Option(..., "--repo", "-r", help="Repository (owner/repo format)"),
    issue: int = typer.Option(..., "--issue", "-n", help="Issue number"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    with_comments: bool = typer.Option(False, "--comments", "-c", help="Include issue comments"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Read a GitHub issue and format it for agent context.

    Uses the gh CLI to fetch issue details. Requires gh to be installed
    and authenticated.

    Examples:

        # Read an issue
        ./bin/agent-cli.py read-issue -r user/repo -n 123

        # Read with comments
        ./bin/agent-cli.py read-issue -r user/repo -n 123 --comments

        # Save to file for agent context
        ./bin/agent-cli.py read-issue -r user/repo -n 123 -o issue.md
    """
    if verbose:
        typer.echo(f"[ISSUE] Fetching {repo}#{issue}...")

    try:
        # Fetch issue details
        result = subprocess.run(
            ["gh", "issue", "view", str(issue), "--repo", repo, "--json",
             "title,body,state,author,labels,assignees,createdAt,url"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            typer.echo(f"Error: Failed to fetch issue. {result.stderr}", err=True)
            raise typer.Exit(1)

        issue_data = json.loads(result.stdout)

        # Build formatted output
        labels = ", ".join([l["name"] for l in issue_data.get("labels", [])]) or "None"
        assignees = ", ".join([a["login"] for a in issue_data.get("assignees", [])]) or "None"

        content = f"""# Issue #{issue}: {issue_data['title']}

**Repository:** {repo}
**URL:** {issue_data['url']}
**State:** {issue_data['state']}
**Author:** {issue_data['author']['login']}
**Labels:** {labels}
**Assignees:** {assignees}
**Created:** {issue_data['createdAt']}

## Description

{issue_data.get('body', 'No description provided.')}
"""

        # Fetch comments if requested
        if with_comments:
            if verbose:
                typer.echo("[ISSUE] Fetching comments...")

            comments_result = subprocess.run(
                ["gh", "issue", "view", str(issue), "--repo", repo, "--json", "comments"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if comments_result.returncode == 0:
                comments_data = json.loads(comments_result.stdout)
                comments = comments_data.get("comments", [])

                if comments:
                    content += "\n## Comments\n\n"
                    for i, comment in enumerate(comments, 1):
                        content += f"### Comment {i} by {comment['author']['login']} ({comment['createdAt']})\n\n"
                        content += f"{comment['body']}\n\n"

        # Output
        if output:
            out_path = Path(output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
            typer.echo(f"[ISSUE] Saved to: {output}")
        else:
            typer.echo(content)

    except subprocess.TimeoutExpired:
        typer.echo("Error: Request timed out", err=True)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("Error: gh CLI not found. Install it from https://cli.github.com/", err=True)
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        typer.echo(f"Error: Failed to parse response: {e}", err=True)
        raise typer.Exit(1)


@app.command("list-issues")
def list_issues(
    repo: str = typer.Option(..., "--repo", "-r", help="Repository (owner/repo format)"),
    state: str = typer.Option("open", "--state", "-s", help="Filter by state: open, closed, all"),
    label: Optional[str] = typer.Option(None, "--label", "-l", help="Filter by label"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of issues to list"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    List GitHub issues from a repository.

    Uses the gh CLI to fetch issues. Requires gh to be installed
    and authenticated.

    Examples:

        # List open issues
        ./bin/agent-cli.py list-issues -r user/repo

        # List closed issues
        ./bin/agent-cli.py list-issues -r user/repo -s closed

        # Filter by label
        ./bin/agent-cli.py list-issues -r user/repo -l bug
    """
    if verbose:
        typer.echo(f"[ISSUE] Listing issues from {repo}...")

    try:
        cmd = ["gh", "issue", "list", "--repo", repo, "--state", state,
               "--limit", str(limit), "--json", "number,title,state,author,labels,createdAt"]

        if label:
            cmd.extend(["--label", label])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            typer.echo(f"Error: Failed to list issues. {result.stderr}", err=True)
            raise typer.Exit(1)

        issues = json.loads(result.stdout)

        if not issues:
            typer.echo(f"No {state} issues found in {repo}")
            return

        typer.echo(f"\n{'#':<6} {'State':<8} {'Title':<50} {'Labels':<20}")
        typer.echo("-" * 90)

        for issue in issues:
            labels = ", ".join([l["name"] for l in issue.get("labels", [])])[:20]
            title = issue["title"][:48] + ".." if len(issue["title"]) > 50 else issue["title"]
            typer.echo(f"{issue['number']:<6} {issue['state']:<8} {title:<50} {labels:<20}")

        typer.echo(f"\nTotal: {len(issues)} issues")

    except subprocess.TimeoutExpired:
        typer.echo("Error: Request timed out", err=True)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("Error: gh CLI not found. Install it from https://cli.github.com/", err=True)
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        typer.echo(f"Error: Failed to parse response: {e}", err=True)
        raise typer.Exit(1)


@app.command("create-pr")
def create_pr(
    repo: str = typer.Option(..., "--repo", "-r", help="Repository (owner/repo format)"),
    title: str = typer.Option(..., "--title", "-t", help="PR title"),
    body: Optional[str] = typer.Option(None, "--body", "-b", help="PR body/description"),
    body_file: Optional[str] = typer.Option(None, "--body-file", "-f", help="File containing PR body"),
    head: str = typer.Option(..., "--head", "-H", help="Branch containing changes"),
    base: str = typer.Option("main", "--base", "-B", help="Branch to merge into (default: main)"),
    draft: bool = typer.Option(False, "--draft", "-d", help="Create as draft PR"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Create a GitHub Pull Request.

    Uses the gh CLI to create PRs. Requires gh to be installed
    and authenticated with push access.

    Examples:

        # Create a PR
        ./bin/agent-cli.py create-pr -r user/repo -t "Add feature X" -H feature-branch

        # Create with description
        ./bin/agent-cli.py create-pr -r user/repo -t "Fix bug" -b "Fixes #123" -H fix-branch

        # Create from body file
        ./bin/agent-cli.py create-pr -r user/repo -t "Big feature" -f pr_description.md -H feature-branch

        # Create draft PR
        ./bin/agent-cli.py create-pr -r user/repo -t "WIP: Feature" -H wip-branch --draft
    """
    if verbose:
        typer.echo(f"[PR] Creating PR: {head} -> {base} in {repo}...")

    # Get body content
    pr_body = body or ""
    if body_file:
        body_path = Path(body_file)
        if body_path.exists():
            pr_body = body_path.read_text(encoding="utf-8")
        else:
            typer.echo(f"Error: Body file not found: {body_file}", err=True)
            raise typer.Exit(1)

    try:
        cmd = [
            "gh", "pr", "create",
            "--repo", repo,
            "--title", title,
            "--head", head,
            "--base", base,
        ]

        if pr_body:
            cmd.extend(["--body", pr_body])

        if draft:
            cmd.append("--draft")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            typer.echo(f"Error: Failed to create PR. {result.stderr}", err=True)
            raise typer.Exit(1)

        # gh pr create outputs the PR URL
        pr_url = result.stdout.strip()
        typer.echo(f"[PR] Created: {pr_url}")

    except subprocess.TimeoutExpired:
        typer.echo("Error: Request timed out", err=True)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("Error: gh CLI not found. Install it from https://cli.github.com/", err=True)
        raise typer.Exit(1)


@app.command("list-prs")
def list_prs(
    repo: str = typer.Option(..., "--repo", "-r", help="Repository (owner/repo format)"),
    state: str = typer.Option("open", "--state", "-s", help="Filter by state: open, closed, merged, all"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of PRs to list"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    List GitHub Pull Requests from a repository.

    Uses the gh CLI to fetch PRs. Requires gh to be installed
    and authenticated.

    Examples:

        # List open PRs
        ./bin/agent-cli.py list-prs -r user/repo

        # List merged PRs
        ./bin/agent-cli.py list-prs -r user/repo -s merged
    """
    if verbose:
        typer.echo(f"[PR] Listing PRs from {repo}...")

    try:
        cmd = ["gh", "pr", "list", "--repo", repo, "--state", state,
               "--limit", str(limit), "--json", "number,title,state,author,headRefName,baseRefName,createdAt"]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            typer.echo(f"Error: Failed to list PRs. {result.stderr}", err=True)
            raise typer.Exit(1)

        prs = json.loads(result.stdout)

        if not prs:
            typer.echo(f"No {state} PRs found in {repo}")
            return

        typer.echo(f"\n{'#':<6} {'State':<8} {'Title':<40} {'Branch':<25}")
        typer.echo("-" * 85)

        for pr in prs:
            title = pr["title"][:38] + ".." if len(pr["title"]) > 40 else pr["title"]
            branch = pr["headRefName"][:23] + ".." if len(pr["headRefName"]) > 25 else pr["headRefName"]
            typer.echo(f"{pr['number']:<6} {pr['state']:<8} {title:<40} {branch:<25}")

        typer.echo(f"\nTotal: {len(prs)} PRs")

    except subprocess.TimeoutExpired:
        typer.echo("Error: Request timed out", err=True)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("Error: gh CLI not found. Install it from https://cli.github.com/", err=True)
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        typer.echo(f"Error: Failed to parse response: {e}", err=True)
        raise typer.Exit(1)


@app.command("read-pr")
def read_pr(
    repo: str = typer.Option(..., "--repo", "-r", help="Repository (owner/repo format)"),
    pr_number: int = typer.Option(..., "--pr", "-n", help="PR number"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    with_comments: bool = typer.Option(False, "--comments", "-c", help="Include PR comments"),
    with_diff: bool = typer.Option(False, "--diff", "-d", help="Include PR diff"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Read a GitHub Pull Request and format it for agent context.

    Uses the gh CLI to fetch PR details. Requires gh to be installed
    and authenticated.

    Examples:

        # Read a PR
        ./bin/agent-cli.py read-pr -r user/repo -n 123

        # Read with comments and diff
        ./bin/agent-cli.py read-pr -r user/repo -n 123 --comments --diff

        # Save to file for agent context
        ./bin/agent-cli.py read-pr -r user/repo -n 123 -o pr.md
    """
    if verbose:
        typer.echo(f"[PR] Fetching {repo}#{pr_number}...")

    try:
        # Fetch PR details
        result = subprocess.run(
            ["gh", "pr", "view", str(pr_number), "--repo", repo, "--json",
             "title,body,state,author,labels,assignees,headRefName,baseRefName,createdAt,url,mergeable,additions,deletions,changedFiles"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            typer.echo(f"Error: Failed to fetch PR. {result.stderr}", err=True)
            raise typer.Exit(1)

        pr_data = json.loads(result.stdout)

        # Build formatted output
        labels = ", ".join([l["name"] for l in pr_data.get("labels", [])]) or "None"
        assignees = ", ".join([a["login"] for a in pr_data.get("assignees", [])]) or "None"

        content = f"""# PR #{pr_number}: {pr_data['title']}

**Repository:** {repo}
**URL:** {pr_data['url']}
**State:** {pr_data['state']}
**Author:** {pr_data['author']['login']}
**Branch:** {pr_data['headRefName']} → {pr_data['baseRefName']}
**Labels:** {labels}
**Assignees:** {assignees}
**Created:** {pr_data['createdAt']}
**Mergeable:** {pr_data.get('mergeable', 'Unknown')}
**Changes:** +{pr_data.get('additions', 0)} -{pr_data.get('deletions', 0)} ({pr_data.get('changedFiles', 0)} files)

## Description

{pr_data.get('body', 'No description provided.')}
"""

        # Fetch comments if requested
        if with_comments:
            if verbose:
                typer.echo("[PR] Fetching comments...")

            comments_result = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--repo", repo, "--json", "comments"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if comments_result.returncode == 0:
                comments_data = json.loads(comments_result.stdout)
                comments = comments_data.get("comments", [])

                if comments:
                    content += "\n## Comments\n\n"
                    for i, comment in enumerate(comments, 1):
                        content += f"### Comment {i} by {comment['author']['login']} ({comment['createdAt']})\n\n"
                        content += f"{comment['body']}\n\n"

        # Fetch diff if requested
        if with_diff:
            if verbose:
                typer.echo("[PR] Fetching diff...")

            diff_result = subprocess.run(
                ["gh", "pr", "diff", str(pr_number), "--repo", repo],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if diff_result.returncode == 0:
                diff = diff_result.stdout
                # Truncate very large diffs
                if len(diff) > 50000:
                    diff = diff[:50000] + "\n\n[Diff truncated due to size]"
                content += f"\n## Diff\n\n```diff\n{diff}\n```\n"

        # Output
        if output:
            out_path = Path(output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
            typer.echo(f"[PR] Saved to: {output}")
        else:
            typer.echo(content)

    except subprocess.TimeoutExpired:
        typer.echo("Error: Request timed out", err=True)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("Error: gh CLI not found. Install it from https://cli.github.com/", err=True)
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        typer.echo(f"Error: Failed to parse response: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
