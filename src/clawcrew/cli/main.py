"""
ClawCrew CLI - Main entry point.

Usage:
    clawcrew init              # Interactive setup wizard
    clawcrew start             # Start the system
    clawcrew run <agent> -t "task"  # Run an agent
    clawcrew agents            # List available agents
    clawcrew status            # Show system status
"""

import typer
from rich.console import Console

from clawcrew import __version__

# Create main app
app = typer.Typer(
    name="clawcrew",
    help="Multi-agent AI team framework for OpenClaw",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

console = Console()


def version_callback(value: bool):
    if value:
        console.print(f"ClawCrew version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-V", callback=version_callback, is_eager=True,
        help="Show version and exit"
    ),
):
    """ClawCrew - Multi-agent AI team framework for OpenClaw."""
    pass


# Import and register commands
from clawcrew.cli.run import run
from clawcrew.cli.agents import agents, show_memory, clear_memory
from clawcrew.cli.init import init
from clawcrew.cli.system import start, stop, status

app.command()(run)
app.command()(agents)
app.command("show-memory")(show_memory)
app.command("clear-memory")(clear_memory)
app.command()(init)
app.command()(start)
app.command()(stop)
app.command()(status)

# GitHub subcommand group
from clawcrew.cli.github import github_app
app.add_typer(github_app, name="github")


if __name__ == "__main__":
    app()
