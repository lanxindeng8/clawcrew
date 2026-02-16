"""Agent management commands."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from clawcrew.core.config import AGENT_WORKSPACES, get_base_dir, get_workspace
from clawcrew.core.memory import load_memory, clear_memory as do_clear_memory

console = Console()


def agents():
    """List available agents and their workspace status."""
    table = Table(title="Available Agents")
    table.add_column("Agent", style="cyan")
    table.add_column("Workspace", style="dim")
    table.add_column("Status")

    base_dir = get_base_dir()

    for agent, ws_name in AGENT_WORKSPACES.items():
        ws = base_dir / ws_name
        installed_ws = Path.home() / ".openclaw" / ws_name

        if ws.exists():
            status = "[green]✓ (dev)[/green]"
        elif installed_ws.exists():
            status = "[green]✓ (installed)[/green]"
        else:
            status = "[red]✗ not found[/red]"

        table.add_row(agent, ws_name, status)

    console.print(table)


def show_memory(
    agent: str = typer.Option(..., "--agent", "-a", help="Agent name"),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to show"),
):
    """Show recent memories for an agent."""
    try:
        ws = get_workspace(agent)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    memory = load_memory(ws, days)

    if not memory:
        console.print(f"No memories found for [cyan]{agent}[/cyan] in the last {days} days")
        return

    console.print(f"\n[bold]Recent memories for {agent}:[/bold]\n")
    console.print(memory)


def clear_memory(
    agent: str = typer.Option(..., "--agent", "-a", help="Agent name"),
    all_days: bool = typer.Option(False, "--all", help="Clear all memory files"),
):
    """Clear memories for an agent."""
    try:
        ws = get_workspace(agent)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if do_clear_memory(ws, all_days):
        if all_days:
            console.print(f"[green]Cleared all memories for {agent}[/green]")
        else:
            console.print(f"[green]Cleared today's memories for {agent}[/green]")
    else:
        console.print(f"No memories to clear for [cyan]{agent}[/cyan]")
