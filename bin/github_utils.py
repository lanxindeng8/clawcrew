"""
GitHub Repository Analysis Utilities

Functions for cloning, analyzing, and summarizing GitHub repositories.
Used by the summarize-repo command in agent-cli.py.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

# File reading limits
MAX_FILE_SIZE = 100 * 1024  # 100KB per file
MAX_TOTAL_CONTENT = 500 * 1024  # 500KB total
MAX_TREE_DEPTH = 4
MAX_FILES_PER_CATEGORY = 5

# Priority files to always try to read
PRIORITY_FILES = [
    "README.md", "README.rst", "README.txt", "README",
    "CONTRIBUTING.md", "ARCHITECTURE.md", "DESIGN.md",
]

# Entry point patterns by language
ENTRY_POINT_PATTERNS = [
    # Python
    "main.py", "app.py", "run.py", "__main__.py", "cli.py",
    "src/main.py", "src/app.py", "src/__main__.py",
    # JavaScript/TypeScript
    "index.js", "index.ts", "main.js", "main.ts", "app.js", "app.ts",
    "src/index.js", "src/index.ts", "src/main.js", "src/main.ts",
    # Go
    "main.go", "cmd/main.go",
    # Rust
    "src/main.rs", "src/lib.rs",
]

# Config files by language/framework
CONFIG_FILES = [
    # Python
    "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
    "Pipfile", "poetry.lock",
    # JavaScript
    "package.json", "package-lock.json", "yarn.lock", "tsconfig.json",
    # Go
    "go.mod", "go.sum",
    # Rust
    "Cargo.toml", "Cargo.lock",
    # General
    "Makefile", "Dockerfile", "docker-compose.yml", ".env.example",
]

# =============================================================================
# Functions
# =============================================================================

def get_github_token(provided_pat: str = None) -> str:
    """
    Get GitHub PAT from various sources.

    Priority:
        1. Provided PAT (--pat flag)
        2. GITHUB_PAT environment variable
        3. GH_TOKEN environment variable (gh CLI compatible)

    Args:
        provided_pat: PAT explicitly provided via CLI

    Returns:
        PAT string or None if not found
    """
    if provided_pat:
        return provided_pat
    return os.environ.get("GITHUB_PAT") or os.environ.get("GH_TOKEN")


def parse_github_url(url: str) -> tuple:
    """
    Parse GitHub URL into components.

    Supports:
        https://github.com/user/repo
        https://github.com/user/repo.git
        git@github.com:user/repo.git

    Args:
        url: GitHub repository URL

    Returns:
        Tuple of (owner, repo_name, clone_url)

    Raises:
        ValueError: If URL format is not recognized
    """
    # HTTPS format
    https_match = re.match(r'https://github\.com/([^/]+)/([^/.]+)(?:\.git)?/?', url)
    if https_match:
        owner, repo = https_match.groups()
        return owner, repo, f"https://github.com/{owner}/{repo}.git"

    # SSH format
    ssh_match = re.match(r'git@github\.com:([^/]+)/([^/.]+)(?:\.git)?', url)
    if ssh_match:
        owner, repo = ssh_match.groups()
        return owner, repo, f"https://github.com/{owner}/{repo}.git"

    raise ValueError(f"Unrecognized GitHub URL format: {url}")


def clone_repository(clone_url: str, target_dir: Path, branch: str = None, pat: str = None) -> bool:
    """
    Clone a repository with shallow depth.

    Args:
        clone_url: Git clone URL
        target_dir: Directory to clone into
        branch: Specific branch to clone (default: repo's default branch)
        pat: GitHub Personal Access Token for private repos

    Returns:
        True if successful, False otherwise
    """
    try:
        # Insert PAT into URL for authentication
        # https://github.com/... -> https://<pat>@github.com/...
        auth_url = clone_url
        if pat and clone_url.startswith("https://github.com/"):
            auth_url = clone_url.replace("https://github.com/", f"https://{pat}@github.com/")

        cmd = ["git", "clone", "--depth", "1"]
        if branch:
            cmd.extend(["--branch", branch])
        cmd.extend([auth_url, str(target_dir)])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except FileNotFoundError:
        return False


def generate_file_tree(repo_path: Path, max_depth: int = MAX_TREE_DEPTH) -> str:
    """
    Generate a file tree representation of the repository.

    Args:
        repo_path: Path to repository root
        max_depth: Maximum directory depth to traverse

    Returns:
        String representation of file tree
    """
    lines = []

    def walk(path: Path, prefix: str = "", depth: int = 0):
        if depth > max_depth:
            return

        # Skip hidden directories and common noise
        skip_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv',
                     'dist', 'build', '.tox', '.pytest_cache', '.mypy_cache',
                     'target', 'vendor'}

        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return

        # Filter and limit entries
        dirs = [e for e in entries if e.is_dir() and e.name not in skip_dirs and not e.name.startswith('.')]
        files = [e for e in entries if e.is_file() and not e.name.startswith('.')]

        # Limit files shown per directory
        if len(files) > 10:
            files = files[:10]
            truncated_files = True
        else:
            truncated_files = False

        all_entries = dirs + files

        for i, entry in enumerate(all_entries):
            is_last = (i == len(all_entries) - 1) and not truncated_files
            connector = "└── " if is_last else "├── "

            if entry.is_dir():
                lines.append(f"{prefix}{connector}{entry.name}/")
                extension = "    " if is_last else "│   "
                walk(entry, prefix + extension, depth + 1)
            else:
                lines.append(f"{prefix}{connector}{entry.name}")

        if truncated_files:
            lines.append(f"{prefix}└── ... ({len(entries) - len(dirs) - 10} more files)")

    lines.append(f"{repo_path.name}/")
    walk(repo_path)
    return "\n".join(lines)


def find_key_files(repo_path: Path) -> dict:
    """
    Find key files in the repository organized by category.

    Args:
        repo_path: Path to repository root

    Returns:
        Dict mapping category names to lists of file paths
    """
    result = {
        "documentation": [],
        "entry_points": [],
        "config": [],
        "core": [],
    }

    # Find documentation
    for name in PRIORITY_FILES:
        path = repo_path / name
        if path.exists():
            result["documentation"].append(path)

    # Check docs directory
    docs_dir = repo_path / "docs"
    if docs_dir.exists():
        for md_file in list(docs_dir.glob("*.md"))[:3]:
            result["documentation"].append(md_file)

    # Find config files
    for name in CONFIG_FILES:
        path = repo_path / name
        if path.exists():
            result["config"].append(path)

    # Find entry points (simplified - not using glob patterns)
    for name in ENTRY_POINT_PATTERNS:
        if '*' not in name:  # Skip glob patterns for simplicity
            path = repo_path / name
            if path.exists():
                result["entry_points"].append(path)

    # Find core files in src/, lib/, pkg/, internal/
    core_dirs = ["src", "lib", "pkg", "internal", "app"]
    for dir_name in core_dirs:
        dir_path = repo_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            # Get first few Python/JS/Go/Rust files
            for pattern in ["*.py", "*.js", "*.ts", "*.go", "*.rs"]:
                files = list(dir_path.glob(pattern))[:2]
                result["core"].extend(files)

    # Limit each category
    for category in result:
        result[category] = result[category][:MAX_FILES_PER_CATEGORY]

    return result


def read_file_safe(path: Path, max_size: int = MAX_FILE_SIZE) -> str:
    """
    Read a file safely with size limits.

    Args:
        path: Path to file
        max_size: Maximum bytes to read

    Returns:
        File content or error message
    """
    try:
        size = path.stat().st_size
        if size > max_size:
            return f"[File truncated - {size} bytes, showing first {max_size}]\n" + \
                   path.read_text(encoding="utf-8", errors="replace")[:max_size]
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"[Error reading file: {e}]"


def build_repo_context(repo_path: Path, key_files: dict) -> str:
    """
    Build the context string for LLM analysis.

    Args:
        repo_path: Path to repository
        key_files: Dict of categorized file paths

    Returns:
        Formatted context string
    """
    sections = []
    total_size = 0

    # File tree
    tree = generate_file_tree(repo_path)
    sections.append(f"## File Tree\n\n```\n{tree}\n```")
    total_size += len(tree)

    # Read files by category
    for category, files in key_files.items():
        if not files:
            continue

        category_title = category.replace("_", " ").title()
        file_contents = []

        for file_path in files:
            if total_size >= MAX_TOTAL_CONTENT:
                break

            relative_path = file_path.relative_to(repo_path)
            content = read_file_safe(file_path)
            content_size = len(content)

            if total_size + content_size > MAX_TOTAL_CONTENT:
                remaining = MAX_TOTAL_CONTENT - total_size
                content = content[:remaining] + "\n[Content truncated due to size limits]"
                content_size = remaining

            file_contents.append(f"### {relative_path}\n\n```\n{content}\n```")
            total_size += content_size

        if file_contents:
            sections.append(f"## {category_title}\n\n" + "\n\n".join(file_contents))

    return "\n\n".join(sections)
