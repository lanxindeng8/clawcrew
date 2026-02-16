"""System management commands."""

import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def start():
    """Start the ClawCrew system (OpenClaw gateway)."""
    console.print("[bold]Starting ClawCrew...[/bold]")

    # Check if OpenClaw is installed
    if not Path.home().joinpath(".openclaw", "openclaw.json").exists():
        console.print("[red]Error:[/red] OpenClaw not installed.")
        console.print("Install OpenClaw first: https://openclaw.dev")
        raise typer.Exit(1)

    # Start gateway
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "start"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            console.print("[green]✓ OpenClaw gateway started[/green]")
        else:
            console.print(f"[yellow]Warning:[/yellow] {result.stderr or result.stdout}")

    except FileNotFoundError:
        console.print("[red]Error:[/red] openclaw command not found.")
        raise typer.Exit(1)
    except subprocess.TimeoutExpired:
        console.print("[yellow]Gateway start timed out (may still be starting)[/yellow]")

    console.print("\n[bold]ClawCrew is ready![/bold]")
    console.print("Send a message to your Telegram bot to get started.")


def stop():
    """Stop the ClawCrew system."""
    console.print("[bold]Stopping ClawCrew...[/bold]")

    try:
        result = subprocess.run(
            ["openclaw", "gateway", "stop"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            console.print("[green]✓ OpenClaw gateway stopped[/green]")
        else:
            console.print(f"[yellow]{result.stderr or result.stdout}[/yellow]")

    except FileNotFoundError:
        console.print("[red]Error:[/red] openclaw command not found.")
        raise typer.Exit(1)


def status():
    """Show system status."""
    console.print("[bold]ClawCrew Status[/bold]\n")

    # Check OpenClaw config
    openclaw_config = Path.home() / ".openclaw" / "openclaw.json"
    if openclaw_config.exists():
        console.print("[green]✓[/green] OpenClaw: Configured")
    else:
        console.print("[red]✗[/red] OpenClaw: Not configured")

    # Check ClawCrew config
    clawcrew_config = Path.home() / ".clawcrew" / "config.toml"
    if clawcrew_config.exists():
        console.print("[green]✓[/green] ClawCrew: Configured")
    else:
        console.print("[yellow]![/yellow] ClawCrew: Not configured (run: clawcrew init)")

    # Check gateway status
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if "running" in result.stdout.lower():
            console.print("[green]✓[/green] Gateway: Running")
        else:
            console.print("[yellow]![/yellow] Gateway: Not running (run: clawcrew start)")
    except Exception:
        console.print("[yellow]![/yellow] Gateway: Unknown")

    # Show agent workspaces
    console.print("\n[bold]Agent Workspaces:[/bold]")

    from clawcrew.core.config import AGENT_WORKSPACES, get_base_dir

    base_dir = get_base_dir()
    table = Table()
    table.add_column("Agent")
    table.add_column("Status")
    table.add_column("Path")

    for agent, ws_name in AGENT_WORKSPACES.items():
        ws = base_dir / ws_name
        installed_ws = Path.home() / ".openclaw" / ws_name

        if ws.exists():
            table.add_row(agent, "[green]✓[/green]", str(ws))
        elif installed_ws.exists():
            table.add_row(agent, "[green]✓[/green]", str(installed_ws))
        else:
            table.add_row(agent, "[red]✗[/red]", "Not found")

    console.print(table)
