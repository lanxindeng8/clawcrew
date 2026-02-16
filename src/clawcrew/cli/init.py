"""Interactive setup wizard."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def init(
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", "-i/-n"),
):
    """Initialize ClawCrew configuration interactively."""
    console.print(Panel.fit(
        "[bold blue]Welcome to ClawCrew![/bold blue]\n\n"
        "Let's set up your multi-agent AI team.",
        title="ClawCrew Setup Wizard"
    ))

    if not interactive:
        console.print("[yellow]Non-interactive mode. Please set environment variables.[/yellow]")
        console.print("\nRequired environment variables:")
        console.print("  TELEGRAM_BOT_TOKEN")
        console.print("  TELEGRAM_CHAT_ID")
        console.print("  TELEGRAM_ALLOWED_USERS")
        return

    try:
        import questionary
    except ImportError:
        console.print("[red]Error:[/red] questionary not installed. Run: pip install questionary")
        raise typer.Exit(1)

    config = {}

    # Step 1: Telegram Bot Token
    console.print("\n[bold]Step 1/4: Telegram Bot Setup[/bold]\n")
    console.print(Markdown("""
To create a Telegram bot:
1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the prompts to name your bot
4. Copy the API token (looks like: `123456:ABC-DEF...`)
    """))

    token = questionary.password("Enter your bot token:").ask()
    if not token:
        console.print("[red]Setup cancelled.[/red]")
        raise typer.Exit(1)

    if verify_bot_token(token):
        config['bot_token'] = token
        console.print("[green]✓ Bot token verified![/green]")
    else:
        console.print("[red]✗ Invalid token. Please check and try again.[/red]")
        raise typer.Exit(1)

    # Step 2: Group Chat ID
    console.print("\n[bold]Step 2/4: Telegram Group Setup[/bold]\n")
    console.print(Markdown("""
To get your group chat ID:
1. Add **@userinfobot** to your group
2. It will show the chat ID (starts with `-100`)
    """))

    chat_id = questionary.text(
        "Enter your group chat ID:",
    ).ask()
    if not chat_id:
        console.print("[red]Setup cancelled.[/red]")
        raise typer.Exit(1)
    config['chat_id'] = chat_id

    # Step 3: Allowed Users
    console.print("\n[bold]Step 3/4: User Access Control[/bold]\n")

    user_ids = questionary.text(
        "Enter allowed user IDs (comma-separated):",
    ).ask()
    if not user_ids:
        console.print("[red]Setup cancelled.[/red]")
        raise typer.Exit(1)
    config['allowed_users'] = [x.strip() for x in user_ids.split(",")]

    # Step 4: GitHub Integration
    console.print("\n[bold]Step 4/4: GitHub Integration (Optional)[/bold]\n")

    enable_github = questionary.confirm(
        "Enable GitHub integration?",
        default=False
    ).ask()

    if enable_github:
        github_token = questionary.password("Enter your GitHub Personal Access Token:").ask()
        if github_token:
            config['github_token'] = github_token

    # Save configuration
    save_config(config)

    # Show summary
    console.print("\n[bold green]Setup Complete![/bold green]\n")
    console.print(f"  ✓ Telegram Bot configured")
    console.print(f"  ✓ Group Chat: {config['chat_id']}")
    console.print(f"  ✓ Allowed Users: {len(config['allowed_users'])}")
    if 'github_token' in config:
        console.print(f"  ✓ GitHub: Enabled")

    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Run: clawcrew start")
    console.print("  2. Open your Telegram group")
    console.print("  3. Send a message to your bot")


def verify_bot_token(token: str) -> bool:
    """Verify Telegram bot token by calling getMe API."""
    try:
        import httpx
        resp = httpx.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        return resp.json().get("ok", False)
    except Exception:
        return False


def save_config(config: dict):
    """Save configuration to ~/.clawcrew/config.toml"""
    from pathlib import Path

    config_dir = Path.home() / ".clawcrew"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "config.toml"

    # Build TOML content
    lines = ["[telegram]"]
    lines.append(f'bot_token = "{config["bot_token"]}"')
    lines.append(f'chat_id = "{config["chat_id"]}"')
    lines.append(f'allowed_users = {config["allowed_users"]}')

    if 'github_token' in config:
        lines.append("\n[github]")
        lines.append(f'token = "{config["github_token"]}"')

    config_file.write_text("\n".join(lines), encoding="utf-8")
    config_file.chmod(0o600)

    console.print(f"\n[dim]Config saved to: {config_file}[/dim]")
