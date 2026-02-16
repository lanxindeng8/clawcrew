"""Run agent command."""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console

from clawcrew.core.config import get_workspace
from clawcrew.core.memory import load_memory, save_memory
from clawcrew.core.llm import call_llm, extract_output, LLMError

console = Console()


def run(
    agent: str = typer.Argument(..., help="Agent name: design, code, test, orca, github"),
    task: str = typer.Option(..., "--task", "-t", help="Task description"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    context: Optional[List[str]] = typer.Option(None, "--context", "-c", help="Context file(s) to read"),
    task_id: Optional[str] = typer.Option(None, "--task-id", help="Task ID for tracking"),
    no_memory: bool = typer.Option(False, "--no-memory", help="Skip memory loading/saving"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run a specialized agent with a task.

    The agent loads its SOUL.md (personality) and recent memories,
    executes the task, saves output, and updates its memory.

    Examples:
        clawcrew run design -t "Design REST API for user auth"
        clawcrew run code -t "Implement auth" -c design.md -o auth.py
        clawcrew run test -t "Write tests" -c auth.py -o test_auth.py
    """
    # Generate task ID if not provided
    if not task_id:
        task_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + str(uuid.uuid4())[:8]

    try:
        ws = get_workspace(agent)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if verbose:
        console.print(f"[dim][{agent.upper()}] Workspace: {ws}[/dim]")
        console.print(f"[dim][{agent.upper()}] Task ID: {task_id}[/dim]")

    # Load memory
    memory = "" if no_memory else load_memory(ws)

    # Load context files if provided
    context_content = ""
    if context:
        for ctx_file in context:
            ctx_path = Path(ctx_file)
            if ctx_path.exists():
                content = ctx_path.read_text(encoding="utf-8")
                context_content += f"\n\n## Context File: {ctx_file}\n```\n{content}\n```"
            else:
                console.print(f"[yellow]Warning:[/yellow] Context file not found: {ctx_file}")

    # Build message
    memory_section = f"\n## Recent Lessons Learned\n{memory}\n" if memory else ""
    output_instruction = ""
    if output:
        output_instruction = """

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
        console.print(f"[dim][{agent.upper()}] Calling OpenClaw agent...[/dim]")

    # Call LLM
    try:
        response = call_llm(message, agent)
        final_output = extract_output(response)
    except LLMError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Save output
    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(final_output, encoding="utf-8")
        console.print(f"[green][{agent.upper()}][/green] Output saved to: {output}")
    else:
        console.print(response)

    # Auto-reflection and memory update
    if not no_memory:
        lesson_prompt = f"""Briefly summarize the key lesson from this task in ONE sentence (max 100 chars).

Task: {task[:200]}
Output: {final_output[:200]}..."""

        try:
            lesson = call_llm(lesson_prompt, "main")
            lesson = lesson.strip()[:100]
        except LLMError:
            lesson = "Task completed successfully."

        save_memory(ws, task_id, task, output, lesson)

        if verbose:
            console.print(f"[dim][{agent.upper()}] Memory updated: {lesson}[/dim]")

    console.print(f"[green][{agent.upper()}][/green] Task {task_id} completed.")
