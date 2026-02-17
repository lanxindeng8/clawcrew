"""Reflex configuration for ClawCrew Dashboard."""

import reflex as rx

config = rx.Config(
    app_name="dashboard",
    title="ClawCrew Dashboard",
    description="Virtual Office monitoring dashboard for AI agent teams",
    # Frontend settings
    frontend_port=3000,
    # Backend settings
    backend_port=8000,
    # Development
    env=rx.Env.DEV,
)
