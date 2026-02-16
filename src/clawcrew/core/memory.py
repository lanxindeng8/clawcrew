"""Agent memory management."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


def load_soul(workspace: Path) -> str:
    """
    Load SOUL.md from workspace.

    SOUL.md defines the agent's personality, responsibilities, and output format.
    Creates a default SOUL if not exists.

    Args:
        workspace: Workspace path

    Returns:
        Content of SOUL.md
    """
    soul_path = workspace / "SOUL.md"
    if soul_path.exists():
        return soul_path.read_text(encoding="utf-8")

    # Create default SOUL if not exists
    default_soul = f"# {workspace.name}\n\nYou are a helpful specialist agent."
    soul_path.write_text(default_soul, encoding="utf-8")
    return default_soul


def load_memory(workspace: Path, days: int = 7) -> str:
    """
    Load recent memories from memory/YYYY-MM-DD.md files.

    Memories contain lessons learned from past tasks, helping agents improve over time.

    Args:
        workspace: Workspace path
        days: Number of days to look back

    Returns:
        Combined memory content as markdown string
    """
    memory_dir = workspace / "memory"
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


def save_memory(
    workspace: Path,
    task_id: str,
    task: str,
    output_file: Optional[str],
    lesson: str,
):
    """
    Append a memory entry to today's memory file.

    Memory format:
        ### HH:MM:SS - task_id
        **Task:** ...
        **Output:** ...
        **Lesson:** ...

    Args:
        workspace: Workspace path
        task_id: Unique task identifier
        task: Task description
        output_file: Output file path (or None)
        lesson: Lesson learned from this task
    """
    memory_dir = workspace / "memory"
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


def clear_memory(workspace: Path, all_days: bool = False) -> bool:
    """
    Clear memories for an agent.

    Args:
        workspace: Workspace path
        all_days: If True, clear all memory files; otherwise just today's

    Returns:
        True if any memories were cleared
    """
    import shutil

    memory_dir = workspace / "memory"

    if not memory_dir.exists():
        return False

    if all_days:
        shutil.rmtree(memory_dir)
        return True
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        today_file = memory_dir / f"{today}.md"
        if today_file.exists():
            today_file.unlink()
            return True

    return False
