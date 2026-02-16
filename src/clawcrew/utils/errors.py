"""ClawCrew error handling utilities."""

from typing import Optional
from rich.console import Console
from rich.panel import Panel

console = Console()


class ClawCrewError(Exception):
    """Base exception for ClawCrew."""

    def __init__(
        self,
        message: str,
        details: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        self.message = message
        self.details = details
        self.suggestion = suggestion
        super().__init__(message)

    def display(self):
        """Display error in a rich format."""
        content = f"[red bold]{self.message}[/red bold]"

        if self.details:
            content += f"\n\n[dim]{self.details}[/dim]"

        if self.suggestion:
            content += f"\n\n[green]Suggestion:[/green] {self.suggestion}"

        console.print(Panel(
            content,
            title="[red]Error[/red]",
            border_style="red",
        ))


class ConfigurationError(ClawCrewError):
    """Configuration error."""
    pass


class AgentError(ClawCrewError):
    """Error running an agent."""
    pass


class AgentOutputError(ClawCrewError):
    """Error in agent output format."""
    pass


class PatchError(ClawCrewError):
    """Error applying a patch."""
    pass


class GitHubError(ClawCrewError):
    """GitHub integration error."""
    pass
