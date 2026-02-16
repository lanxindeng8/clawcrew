"""ClawCrew configuration management."""

from pathlib import Path
from typing import Optional

# Agent name → workspace directory mapping
AGENT_WORKSPACES = {
    "orca": "workspace-orca",
    "design": "workspace-design",
    "code": "workspace-code",
    "test": "workspace-test",
    "github": "workspace-github",
}


def get_base_dir() -> Path:
    """
    Get the base directory for ClawCrew.

    Returns the package source directory for development,
    or ~/.openclaw for installed mode.
    """
    # Try to find package directory (for development)
    pkg_dir = Path(__file__).parent.parent.parent.parent
    if (pkg_dir / "workspace-orca").exists():
        return pkg_dir

    # Fall back to ~/.openclaw (installed mode)
    return Path.home() / ".openclaw"


def get_workspace(agent_name: str) -> Path:
    """
    Get workspace path for an agent.

    Checks package dir first (dev mode), then ~/.openclaw (installed mode).

    Args:
        agent_name: Name of the agent (design, code, test, orca, github)

    Returns:
        Path to the workspace directory

    Raises:
        ValueError: If agent unknown or workspace not found
    """
    if agent_name not in AGENT_WORKSPACES:
        available = ", ".join(AGENT_WORKSPACES.keys())
        raise ValueError(f"Unknown agent: {agent_name}. Available: {available}")

    ws_name = AGENT_WORKSPACES[agent_name]

    # Check package dir first (dev mode)
    base = get_base_dir()
    ws_path = base / ws_name

    if ws_path.exists():
        return ws_path

    # Check ~/.openclaw (installed mode)
    installed_path = Path.home() / ".openclaw" / ws_name
    if installed_path.exists():
        return installed_path

    raise ValueError(f"Workspace not found: {ws_name}")


def get_config_dir() -> Path:
    """Get the ClawCrew configuration directory."""
    config_dir = Path.home() / ".clawcrew"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_artifacts_dir(task_id: Optional[str] = None) -> Path:
    """Get the artifacts directory, optionally for a specific task."""
    artifacts_dir = Path.home() / ".openclaw" / "artifacts"
    if task_id:
        artifacts_dir = artifacts_dir / task_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    return artifacts_dir
