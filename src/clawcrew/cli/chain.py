"""Chain command - run multiple agents in sequence with automatic context passing."""

import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from clawcrew.core.config import get_workspace, get_artifacts_dir
from clawcrew.core.memory import load_memory, save_memory
from clawcrew.core.llm import call_llm, extract_output, LLMError

console = Console()


def chain(
    task: str = typer.Argument(..., help="Task description"),
    agents: List[str] = typer.Argument(..., help="Agents to run in sequence (e.g., design code test)"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run a chain of agents with automatic context passing.

    Each agent's output is automatically passed as context to the next agent.

    Examples:
        clawcrew chain "create REST API for users" design code test
        clawcrew chain "fix bug in auth module" design code -o ./fix-auth/
    """
    # Generate task ID
    task_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + str(uuid.uuid4())[:8]

    # Setup output directory
    if output_dir:
        out_dir = Path(output_dir)
    else:
        out_dir = get_artifacts_dir(task_id)

    out_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold]ClawCrew Chain[/bold]")
    console.print(f"Task: {task}")
    console.print(f"Agents: {' → '.join(agents)}")
    console.print(f"Output: {out_dir}\n")

    context_files: List[Path] = []
    results: List[dict] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        for i, agent in enumerate(agents, 1):
            # Validate agent
            try:
                ws = get_workspace(agent)
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)

            progress_task = progress.add_task(
                f"[{i}/{len(agents)}] Running {agent}...",
                total=None
            )

            # Build context from previous outputs
            context_content = ""
            if context_files:
                context_content = "\n\n## Previous Agent Outputs\n"
                for ctx_file in context_files:
                    content = ctx_file.read_text(encoding="utf-8")
                    context_content += f"\n### {ctx_file.stem}\n```\n{content[:2000]}\n```\n"

            # Load memory
            memory = load_memory(ws)
            memory_section = f"\n## Recent Lessons Learned\n{memory}\n" if memory else ""

            # Build message
            message = f"""## Task
Task ID: {task_id}
Chain Step: {i}/{len(agents)}

{task}
{context_content}
{memory_section}

## Output Instruction
Format your final deliverable between these markers:
---OUTPUT---
[Your complete output here]
---END OUTPUT---
"""

            # Call LLM
            try:
                response = call_llm(message, agent)
                output = extract_output(response)
            except LLMError as e:
                progress.update(progress_task, description=f"[red]✗[/red] {agent} failed")
                console.print(f"\n[red]Error in {agent}:[/red] {e}")
                raise typer.Exit(1)

            # Save output
            output_file = out_dir / f"{i:02d}-{agent}.md"
            output_file.write_text(output, encoding="utf-8")
            context_files.append(output_file)

            # Update memory
            try:
                lesson = call_llm(
                    f"Summarize key lesson in ONE sentence (max 100 chars):\nTask: {task[:100]}\nOutput: {output[:200]}",
                    "main"
                ).strip()[:100]
            except LLMError:
                lesson = "Task completed in chain."

            save_memory(ws, task_id, task, str(output_file), lesson)

            results.append({
                "agent": agent,
                "output_file": output_file,
                "success": True,
            })

            progress.update(progress_task, description=f"[green]✓[/green] {agent} → {output_file.name}")

    # Summary
    console.print("\n[bold green]Chain completed![/bold green]\n")
    console.print("[bold]Outputs:[/bold]")
    for result in results:
        console.print(f"  [green]✓[/green] {result['agent']:10} → {result['output_file']}")

    console.print(f"\n[dim]Task ID: {task_id}[/dim]")
    console.print(f"[dim]All outputs in: {out_dir}[/dim]")

    return out_dir
