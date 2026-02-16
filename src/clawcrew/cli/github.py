"""GitHub integration commands."""

import json
import shutil
import subprocess
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from clawcrew.core.config import get_artifacts_dir
from clawcrew.core.llm import call_llm, extract_output, LLMError
from clawcrew.utils.github import (
    parse_github_url,
    clone_repository,
    find_key_files,
    build_repo_context,
    get_github_token,
)

console = Console()

github_app = typer.Typer(
    name="github",
    help="GitHub integration commands",
    add_completion=False,
)


@github_app.command("analyze")
def analyze_repo(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="GitHub repository URL"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Local repository path"),
    branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Specific branch"),
    pat: Optional[str] = typer.Option(None, "--pat", help="GitHub PAT for private repos"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    task_id: Optional[str] = typer.Option(None, "--task-id", help="Task ID for tracking"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Analyze a GitHub repository or local directory.

    Examples:
        clawcrew github analyze --url https://github.com/user/repo
        clawcrew github analyze --path ./my-project
    """
    if not url and not path:
        console.print("[red]Error:[/red] Must specify either --url or --path")
        raise typer.Exit(1)

    if url and path:
        console.print("[red]Error:[/red] Cannot specify both --url and --path")
        raise typer.Exit(1)

    if not task_id:
        task_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + str(uuid.uuid4())[:8]

    temp_dir = None
    repo_path = None
    repo_name = "local-repo"

    try:
        if url:
            try:
                owner, repo_name, clone_url = parse_github_url(url)
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)

            github_token = get_github_token(pat)
            if verbose:
                console.print(f"[dim]Cloning {owner}/{repo_name}...[/dim]")

            temp_dir = Path(tempfile.mkdtemp(prefix="clawcrew-repo-"))
            repo_path = temp_dir / repo_name

            if not clone_repository(clone_url, repo_path, branch, github_token):
                console.print("[red]Error:[/red] Failed to clone repository")
                raise typer.Exit(1)

        else:
            repo_path = Path(path).resolve()
            if not repo_path.exists() or not repo_path.is_dir():
                console.print(f"[red]Error:[/red] Invalid path: {path}")
                raise typer.Exit(1)
            repo_name = repo_path.name

        if verbose:
            console.print("[dim]Scanning for key files...[/dim]")

        key_files = find_key_files(repo_path)
        context = build_repo_context(repo_path, key_files)

        source = url if url else str(repo_path)
        prompt = f"""## Repository Analysis Task

Task ID: {task_id}

Analyze this repository and provide a comprehensive summary.

**Source:** {source}
**Repository Name:** {repo_name}

{context}

## Instructions

Analyze the repository structure, identify the tech stack, key files, and dependencies.
Follow your output format exactly.

Format your analysis between these markers:
---OUTPUT---
[Your complete analysis here]
---END OUTPUT---
"""

        if verbose:
            console.print("[dim]Calling github agent...[/dim]")

        try:
            response = call_llm(prompt, "github")
            summary = extract_output(response)
        except LLMError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

        if output:
            out_path = Path(output)
        else:
            artifacts_dir = get_artifacts_dir(task_id)
            out_path = artifacts_dir / "repo_summary.md"

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(summary, encoding="utf-8")

        console.print(f"[green]Summary saved to:[/green] {out_path}")

        if not output:
            console.print("\n" + "=" * 60)
            console.print(summary)

    finally:
        if temp_dir and temp_dir.exists():
            artifacts_dir = get_artifacts_dir(task_id)
            clone_dest = artifacts_dir / "repo"
            if not clone_dest.exists() and repo_path and repo_path.exists():
                shutil.move(str(repo_path), str(clone_dest))


@github_app.command("issues")
def list_issues(
    repo: str = typer.Option(..., "--repo", "-r", help="Repository (owner/repo)"),
    state: str = typer.Option("open", "--state", "-s", help="Filter: open, closed, all"),
    label: Optional[str] = typer.Option(None, "--label", "-l", help="Filter by label"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of issues"),
):
    """List GitHub issues from a repository."""
    try:
        cmd = ["gh", "issue", "list", "--repo", repo, "--state", state,
               "--limit", str(limit), "--json", "number,title,state,labels"]

        if label:
            cmd.extend(["--label", label])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            console.print(f"[red]Error:[/red] {result.stderr}")
            raise typer.Exit(1)

        issues = json.loads(result.stdout)

        if not issues:
            console.print(f"No {state} issues found")
            return

        console.print(f"\n[bold]{repo} Issues ({state}):[/bold]\n")
        for issue in issues:
            labels = ", ".join([l["name"] for l in issue.get("labels", [])])
            console.print(f"  #{issue['number']:4} {issue['title'][:60]}")
            if labels:
                console.print(f"       [dim]{labels}[/dim]")

    except FileNotFoundError:
        console.print("[red]Error:[/red] gh CLI not found. Install from https://cli.github.com/")
        raise typer.Exit(1)


@github_app.command("read-issue")
def read_issue(
    repo: str = typer.Option(..., "--repo", "-r", help="Repository (owner/repo)"),
    number: int = typer.Option(..., "--number", "-n", help="Issue number"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
):
    """Read a GitHub issue."""
    try:
        result = subprocess.run(
            ["gh", "issue", "view", str(number), "--repo", repo, "--json",
             "title,body,state,author,labels,assignees,createdAt,url"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            console.print(f"[red]Error:[/red] {result.stderr}")
            raise typer.Exit(1)

        issue = json.loads(result.stdout)

        labels = ", ".join([l["name"] for l in issue.get("labels", [])]) or "None"
        assignees = ", ".join([a["login"] for a in issue.get("assignees", [])]) or "None"

        content = f"""# Issue #{number}: {issue['title']}

**Repository:** {repo}
**URL:** {issue['url']}
**State:** {issue['state']}
**Author:** {issue['author']['login']}
**Labels:** {labels}
**Assignees:** {assignees}
**Created:** {issue['createdAt']}

## Description

{issue.get('body', 'No description provided.')}
"""

        if output:
            Path(output).write_text(content, encoding="utf-8")
            console.print(f"[green]Saved to:[/green] {output}")
        else:
            console.print(content)

    except FileNotFoundError:
        console.print("[red]Error:[/red] gh CLI not found")
        raise typer.Exit(1)


@github_app.command("create-pr")
def create_pr(
    repo: str = typer.Option(..., "--repo", "-r", help="Repository (owner/repo)"),
    title: str = typer.Option(..., "--title", "-t", help="PR title"),
    body: Optional[str] = typer.Option(None, "--body", "-b", help="PR description"),
    head: str = typer.Option(..., "--head", "-H", help="Branch with changes"),
    base: str = typer.Option("main", "--base", "-B", help="Target branch"),
    draft: bool = typer.Option(False, "--draft", "-d", help="Create as draft"),
):
    """Create a GitHub Pull Request."""
    try:
        cmd = ["gh", "pr", "create", "--repo", repo, "--title", title,
               "--head", head, "--base", base]

        if body:
            cmd.extend(["--body", body])
        if draft:
            cmd.append("--draft")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            console.print(f"[red]Error:[/red] {result.stderr}")
            raise typer.Exit(1)

        console.print(f"[green]PR created:[/green] {result.stdout.strip()}")

    except FileNotFoundError:
        console.print("[red]Error:[/red] gh CLI not found")
        raise typer.Exit(1)
