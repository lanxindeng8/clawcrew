"""
ClawCrew Dashboard - Reflex Implementation
Virtual Office style monitoring dashboard for AI agent teams.
"""

import reflex as rx
from typing import List, Dict, Any
from datetime import datetime
import asyncio


# ============================================================
# STATE: Application state management
# ============================================================

class Agent(rx.Base):
    """Agent data model."""
    name: str
    emoji: str
    role: str
    status: str  # online, working, away, offline, error
    model: str
    tokens: int
    tasks: int
    current_task: str = ""
    color: str = "#6366f1"
    position_top: str = "50%"
    position_left: str = "50%"


class LogEntry(rx.Base):
    """Log entry model."""
    timestamp: str
    agent: str
    message: str
    level: str = "info"


class State(rx.State):
    """Main application state."""

    # Navigation
    current_page: str = "home"

    # Stats
    total_tasks: int = 3
    agents_running: int = 2
    total_tokens: int = 15420
    success_rate: str = "94%"

    # Agents data - ordered: Supervisors first (Orca, Audit), then Workers
    agents: List[Agent] = [
        # === SUPERVISORS (left side) ===
        Agent(
            name="Orca",
            emoji="🦑",
            role="Orchestrator",
            status="working",
            model="claude-3-opus",
            tokens=4200,
            tasks=12,
            current_task="Coordinating email validation task",
            color="#6366f1",
            position_top="20%",
            position_left="38%",
        ),
        Agent(
            name="Audit",
            emoji="🔍",
            role="Token & Loop Monitor",
            status="online",
            model="claude-3-haiku",
            tokens=980,
            tasks=3,
            current_task="Monitoring agent runtime",
            color="#dc2626",
            position_top="70%",
            position_left="50%",
        ),
        # === WORKERS (right side, 2x2 grid) ===
        Agent(
            name="Design",
            emoji="🎨",
            role="Architect",
            status="online",
            model="claude-3-sonnet",
            tokens=3800,
            tasks=8,
            current_task="",
            color="#8b5cf6",
            position_top="15%",
            position_left="10%",
        ),
        Agent(
            name="Code",
            emoji="💻",
            role="Engineer",
            status="working",
            model="claude-3-opus",
            tokens=5120,
            tasks=15,
            current_task="Implementing email validation",
            color="#3b82f6",
            position_top="55%",
            position_left="65%",
        ),
        Agent(
            name="Test",
            emoji="🧪",
            role="QA Engineer",
            status="online",
            model="claude-3-sonnet",
            tokens=2300,
            tasks=6,
            current_task="",
            color="#10b981",
            position_top="60%",
            position_left="15%",
        ),
        Agent(
            name="GitHub",
            emoji="🐙",
            role="PR & Issue Manager",
            status="online",
            model="claude-3-haiku",
            tokens=1850,
            tasks=24,
            current_task="",
            color="#24292f",
            position_top="30%",
            position_left="80%",
        ),
    ]

    # Logs
    logs: List[Dict[str, str]] = [
        {"timestamp": "15:33:10", "agent": "code", "message": "Adding type hints and docstrings"},
        {"timestamp": "15:32:45", "agent": "code", "message": "Implementing email validation with regex"},
        {"timestamp": "15:32:18", "agent": "orca", "message": "Quality gate passed → Calling CodeBot"},
        {"timestamp": "15:32:15", "agent": "design", "message": "Output saved to artifacts/design.md"},
        {"timestamp": "15:31:02", "agent": "design", "message": "Analyzing requirements..."},
        {"timestamp": "15:30:45", "agent": "orca", "message": "Calling DesignBot..."},
        {"timestamp": "15:30:42", "agent": "orca", "message": "Received task: Create email validation"},
    ]

    # Token usage per agent
    token_usage: Dict[str, int] = {
        "Orca": 4200,
        "Design": 3800,
        "Code": 5120,
        "Test": 2300,
        "GitHub": 1850,
        "Audit": 980,
    }

    # Auto refresh
    auto_refresh: bool = True
    last_refresh: str = ""

    def navigate(self, page: str):
        """Navigate to a page."""
        self.current_page = page

    def toggle_refresh(self):
        """Toggle auto-refresh."""
        self.auto_refresh = not self.auto_refresh

    def refresh_data(self):
        """Refresh dashboard data."""
        self.last_refresh = datetime.now().strftime("%H:%M:%S")
        # In production: fetch from API

    def format_tokens(self, n: int) -> str:
        """Format token count."""
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        elif n >= 1_000:
            return f"{n/1_000:.1f}K"
        return str(n)


# ============================================================
# STYLES: CSS and Tailwind classes
# ============================================================

# Color scheme
COLORS = {
    "bg": "#f8fafc",
    "card": "#ffffff",
    "border": "#e2e8f0",
    "text": "#1e293b",
    "text_secondary": "#64748b",
    "accent_indigo": "#6366f1",
    "accent_purple": "#8b5cf6",
    "accent_blue": "#3b82f6",
    "accent_green": "#10b981",
    "accent_orange": "#f97316",
    "accent_red": "#ef4444",
}

# Status colors
STATUS_COLORS = {
    "online": "#22c55e",
    "working": "#f97316",
    "away": "#eab308",
    "offline": "#94a3b8",
    "error": "#ef4444",
}


# ============================================================
# COMPONENTS: Reusable UI components
# ============================================================

def status_dot(status, size: str = "12px") -> rx.Component:
    """Render a status indicator dot."""
    # Use rx.match for reactive status color mapping
    color = rx.match(
        status,
        ("online", STATUS_COLORS["online"]),
        ("working", STATUS_COLORS["working"]),
        ("away", STATUS_COLORS["away"]),
        ("error", STATUS_COLORS["error"]),
        STATUS_COLORS["offline"],  # default
    )
    return rx.el.div(
        style={
            "width": size,
            "height": size,
            "border_radius": "50%",
            "background": color,
            "box_shadow": rx.cond(status == "working", f"0 0 10px {STATUS_COLORS['working']}80", f"0 0 10px {STATUS_COLORS['offline']}80"),
            "animation": rx.cond(status == "working", "pulse 1.5s infinite", "none"),
        }
    )


def stat_item(label: str, value: str) -> rx.Component:
    """Render a stat item."""
    return rx.hstack(
        rx.text(f"{label}:", color=COLORS["text_secondary"], font_size="0.85rem"),
        rx.text(value, font_weight="bold", font_size="0.95rem"),
        spacing="1",
    )


def nav_button(icon: str, label: str, page: str, is_active) -> rx.Component:
    """Render a navigation button."""
    return rx.button(
        rx.hstack(
            rx.text(icon, font_size="1.1rem"),
            rx.text(label),
            spacing="2",
            width="100%",
        ),
        width="100%",
        padding="0.75rem 1rem",
        border_radius="8px",
        background=rx.cond(is_active, COLORS["accent_indigo"], "transparent"),
        color=rx.cond(is_active, "white", COLORS["text"]),
        _hover={"background": COLORS["accent_indigo"] + "20"},
        on_click=State.navigate(page),
        cursor="pointer",
    )


# ============================================================
# AGENT CARD: Virtual Office workstation card
# ============================================================

def agent_card(agent) -> rx.Component:
    """Render an agent workstation card with absolute positioning.

    Note: agent is a Var when used inside rx.foreach, so we must use
    rx.match/rx.cond instead of Python dict operations.
    """
    # Use rx.match for status-based color
    status_color = rx.match(
        agent["status"],
        ("online", STATUS_COLORS["online"]),
        ("working", STATUS_COLORS["working"]),
        ("away", STATUS_COLORS["away"]),
        ("error", STATUS_COLORS["error"]),
        STATUS_COLORS["offline"],
    )

    # Status icon via rx.match
    status_icon = rx.match(
        agent["status"],
        ("online", "🟢"),
        ("working", "🟠"),
        ("away", "🟡"),
        ("error", "🔴"),
        "⚪",
    )

    # Status label via rx.match
    status_label = rx.match(
        agent["status"],
        ("online", "Online"),
        ("working", "Working"),
        ("away", "Away"),
        ("error", "Error"),
        "Offline",
    )

    return rx.el.div(
        # Desktop icon (top-right)
        rx.el.div(
            "🖥️",
            style={
                "position": "absolute",
                "top": "-10px",
                "right": "10px",
                "font_size": "1.3rem",
                "background": "white",
                "padding": "2px 6px",
                "border_radius": "8px",
                "box_shadow": "0 2px 8px rgba(0,0,0,0.1)",
            }
        ),
        # Lead badge (if Orca)
        rx.cond(
            agent["name"] == "Orca",
            rx.el.div(
                "👑 LEAD",
                style={
                    "position": "absolute",
                    "top": "-10px",
                    "left": "10px",
                    "background": "linear-gradient(135deg, #fbbf24, #f59e0b)",
                    "color": "white",
                    "padding": "3px 10px",
                    "border_radius": "10px",
                    "font_size": "0.65rem",
                    "font_weight": "700",
                }
            ),
            rx.fragment(),
        ),
        # Status light (top-left inside)
        rx.el.div(
            style={
                "position": "absolute",
                "top": "12px",
                "left": "12px",
                "width": "14px",
                "height": "14px",
                "border_radius": "50%",
                "background": status_color,
            }
        ),
        # Avatar
        rx.el.div(
            agent["emoji"],
            style={
                "width": "70px",
                "height": "70px",
                "margin": "0.5rem auto",
                "background": "linear-gradient(145deg, #fff, #f1f5f9)",
                "border_radius": "50%",
                "display": "flex",
                "align_items": "center",
                "justify_content": "center",
                "font_size": "2.2rem",
                "border": "3px solid " + COLORS["accent_indigo"],
                "box_shadow": "0 4px 15px rgba(0,0,0,0.1)",
            }
        ),
        # Name
        rx.el.h4(
            agent["name"],
            style={
                "text_align": "center",
                "margin": "0.4rem 0 0.2rem",
                "font_size": "1rem",
                "color": COLORS["text"],
            }
        ),
        # Role
        rx.el.p(
            agent["role"],
            style={
                "text_align": "center",
                "color": COLORS["text_secondary"],
                "font_size": "0.75rem",
                "margin": "0 0 0.5rem",
            }
        ),
        # Status badge
        rx.el.div(
            rx.hstack(
                rx.text(status_icon),
                rx.text(status_label),
                spacing="1",
            ),
            style={
                "text_align": "center",
                "margin": "0.5rem auto",
                "padding": "4px 12px",
                "border_radius": "15px",
                "font_size": "0.75rem",
                "font_weight": "600",
                "width": "fit-content",
                "background": "#f1f5f9",
            }
        ),
        # Stats
        rx.el.div(
            rx.vstack(
                rx.hstack(
                    rx.text("📊 Tokens", color=COLORS["text_secondary"], font_size="0.7rem"),
                    rx.text(agent["tokens"], font_weight="600", font_size="0.7rem"),
                    justify="between",
                    width="100%",
                ),
                rx.hstack(
                    rx.text("📋 Tasks", color=COLORS["text_secondary"], font_size="0.7rem"),
                    rx.text(agent["tasks"], font_weight="600", font_size="0.7rem"),
                    justify="between",
                    width="100%",
                ),
                spacing="1",
                width="100%",
            ),
            style={
                "background": "#f8fafc",
                "border_radius": "8px",
                "padding": "8px",
                "margin_top": "8px",
            }
        ),
        # Current task (if any)
        rx.cond(
            agent["current_task"] != "",
            rx.el.div(
                rx.text("💬 ", agent["current_task"]),
                style={
                    "background": "#f0f9ff",
                    "border_radius": "8px",
                    "padding": "6px 10px",
                    "margin_top": "8px",
                    "font_size": "0.7rem",
                    "border_left": "3px solid " + COLORS["accent_indigo"],
                    "color": COLORS["text_secondary"],
                }
            ),
            rx.fragment(),
        ),
        # Card container styles
        style={
            "position": "absolute",
            "top": agent.position_top,
            "left": agent.position_left,
            "width": "200px",
            "background": "rgba(255,255,255,0.95)",
            "backdrop_filter": "blur(10px)",
            "border_radius": "16px",
            "padding": "1rem",
            "border": "2px solid " + COLORS["accent_indigo"] + "40",
            "box_shadow": "0 8px 30px rgba(0,0,0,0.12)",
            "transition": "all 0.3s ease",
            "z_index": "10",
        }
    )


def agent_card_grid(agent) -> rx.Component:
    """Render an agent card for grid layout (no absolute positioning)."""
    # Use rx.match for status-based color
    status_color = rx.match(
        agent["status"],
        ("online", STATUS_COLORS["online"]),
        ("working", STATUS_COLORS["working"]),
        ("away", STATUS_COLORS["away"]),
        ("error", STATUS_COLORS["error"]),
        STATUS_COLORS["offline"],
    )

    status_icon = rx.match(
        agent["status"],
        ("online", "🟢"),
        ("working", "🟠"),
        ("away", "🟡"),
        ("error", "🔴"),
        "⚪",
    )

    status_label = rx.match(
        agent["status"],
        ("online", "Online"),
        ("working", "Working"),
        ("away", "Away"),
        ("error", "Error"),
        "Offline",
    )

    return rx.el.div(
        # Desktop icon (top-right)
        rx.el.div(
            "🖥️",
            style={
                "position": "absolute",
                "top": "-8px",
                "right": "8px",
                "font_size": "1.1rem",
                "background": "white",
                "padding": "2px 6px",
                "border_radius": "6px",
                "box_shadow": "0 2px 6px rgba(0,0,0,0.1)",
            }
        ),
        # Lead badge (if Orca)
        rx.cond(
            agent["name"] == "Orca",
            rx.el.div(
                "👑 LEAD",
                style={
                    "position": "absolute",
                    "top": "-8px",
                    "left": "8px",
                    "background": "linear-gradient(135deg, #fbbf24, #f59e0b)",
                    "color": "white",
                    "padding": "2px 8px",
                    "border_radius": "8px",
                    "font_size": "0.6rem",
                    "font_weight": "700",
                }
            ),
            rx.fragment(),
        ),
        # Avatar
        rx.el.div(
            agent["emoji"],
            style={
                "width": "60px",
                "height": "60px",
                "margin": "0.5rem auto",
                "background": "linear-gradient(145deg, #fff, #f1f5f9)",
                "border_radius": "50%",
                "display": "flex",
                "align_items": "center",
                "justify_content": "center",
                "font_size": "2rem",
                "border": "3px solid " + COLORS["accent_indigo"],
            }
        ),
        # Name
        rx.el.h4(
            agent["name"],
            style={
                "text_align": "center",
                "margin": "0.3rem 0 0.1rem",
                "font_size": "0.95rem",
                "color": COLORS["text"],
            }
        ),
        # Role
        rx.el.p(
            agent["role"],
            style={
                "text_align": "center",
                "color": COLORS["text_secondary"],
                "font_size": "0.7rem",
                "margin": "0 0 0.4rem",
            }
        ),
        # Status badge
        rx.el.div(
            rx.hstack(
                rx.text(status_icon, font_size="0.8rem"),
                rx.text(status_label, font_size="0.75rem"),
                spacing="1",
                justify="center",
            ),
            style={
                "text_align": "center",
                "margin": "0.3rem auto",
                "padding": "3px 10px",
                "border_radius": "12px",
                "font_weight": "600",
                "width": "fit-content",
                "background": "#f1f5f9",
            }
        ),
        # Stats
        rx.el.div(
            rx.vstack(
                rx.hstack(
                    rx.text("📊", font_size="0.7rem"),
                    rx.text(agent["tokens"], font_weight="600", font_size="0.7rem"),
                    spacing="1",
                ),
                rx.hstack(
                    rx.text("📋", font_size="0.7rem"),
                    rx.text(agent["tasks"], font_weight="600", font_size="0.7rem"),
                    spacing="1",
                ),
                spacing="1",
            ),
            style={
                "background": "#f8fafc",
                "border_radius": "6px",
                "padding": "6px",
                "margin_top": "6px",
            }
        ),
        # Current task (if any)
        rx.cond(
            agent["current_task"] != "",
            rx.el.div(
                rx.text("💬 ", agent["current_task"], font_size="0.65rem"),
                style={
                    "background": "#f0f9ff",
                    "border_radius": "6px",
                    "padding": "4px 8px",
                    "margin_top": "6px",
                    "border_left": "2px solid " + COLORS["accent_indigo"],
                    "color": COLORS["text_secondary"],
                    "overflow": "hidden",
                    "text_overflow": "ellipsis",
                    "white_space": "nowrap",
                }
            ),
            rx.fragment(),
        ),
        # Card container styles
        style={
            "position": "relative",
            "width": "180px",
            "min_height": "280px",
            "background": "rgba(255,255,255,0.95)",
            "backdrop_filter": "blur(10px)",
            "border_radius": "12px",
            "padding": "0.75rem",
            "border": "2px solid " + COLORS["accent_indigo"] + "30",
            "box_shadow": "0 4px 15px rgba(0,0,0,0.08)",
            "transition": "all 0.2s ease",
        }
    )


# ============================================================
# VIRTUAL OFFICE: Main agents area with office background
# ============================================================

def virtual_office() -> rx.Component:
    """Render the Virtual Office with supervisors on left, workers on right."""
    # Filter agents into supervisors and workers
    supervisor_names = ["Orca", "Audit"]
    worker_names = ["Design", "Code", "Test", "GitHub"]

    return rx.el.div(
        # Office title badge
        rx.el.div(
            rx.hstack(
                rx.text("🏢", font_size="1.1rem"),
                rx.text("VIRTUAL OFFICE", font_weight="700", letter_spacing="1px"),
                spacing="2",
            ),
            style={
                "text_align": "center",
                "background": "linear-gradient(135deg, #6366f1, #8b5cf6)",
                "color": "white",
                "padding": "8px 24px",
                "border_radius": "25px",
                "font_size": "0.8rem",
                "box_shadow": "0 4px 15px rgba(99,102,241,0.4)",
                "width": "fit-content",
                "margin": "0 auto 1rem",
            }
        ),
        # Workflow pipeline
        rx.hstack(
            rx.el.span("🦑 Orca", style={"background": "#6366f1", "color": "white", "padding": "4px 10px", "border_radius": "12px", "font_weight": "600", "font_size": "0.75rem"}),
            rx.text("→", color="#6366f1", font_weight="bold", font_size="1rem"),
            rx.el.span("🎨 Design", style={"background": "#8b5cf6", "color": "white", "padding": "4px 10px", "border_radius": "12px", "font_weight": "600", "font_size": "0.75rem"}),
            rx.text("→", color="#8b5cf6", font_weight="bold", font_size="1rem"),
            rx.el.span("💻 Code", style={"background": "#3b82f6", "color": "white", "padding": "4px 10px", "border_radius": "12px", "font_weight": "600", "font_size": "0.75rem"}),
            rx.text("→", color="#3b82f6", font_weight="bold", font_size="1rem"),
            rx.el.span("🧪 Test", style={"background": "#10b981", "color": "white", "padding": "4px 10px", "border_radius": "12px", "font_weight": "600", "font_size": "0.75rem"}),
            rx.text("→", color="#10b981", font_weight="bold", font_size="1rem"),
            rx.el.span("🐙 GitHub", style={"background": "#24292f", "color": "white", "padding": "4px 10px", "border_radius": "12px", "font_weight": "600", "font_size": "0.75rem"}),
            spacing="2",
            justify="center",
            wrap="wrap",
            margin_bottom="1rem",
        ),
        # Main office layout: Left (supervisors) | Right (workers)
        rx.hstack(
            # LEFT: Supervisor area
            rx.el.div(
                rx.el.div(
                    "👔 Management",
                    style={
                        "text_align": "center",
                        "font_size": "0.7rem",
                        "font_weight": "600",
                        "color": COLORS["text_secondary"],
                        "margin_bottom": "0.75rem",
                        "text_transform": "uppercase",
                        "letter_spacing": "1px",
                    }
                ),
                rx.el.div(
                    rx.foreach(
                        State.agents[:2],  # Orca and Audit
                        agent_card_grid,
                    ),
                    style={
                        "display": "flex",
                        "flex_direction": "column",
                        "gap": "1rem",
                        "align_items": "center",
                    }
                ),
                style={
                    "padding": "1rem",
                    "background": "rgba(99, 102, 241, 0.05)",
                    "border_radius": "16px",
                    "border": "2px dashed rgba(99, 102, 241, 0.2)",
                }
            ),
            # RIGHT: Worker area (2x2 grid)
            rx.el.div(
                rx.el.div(
                    "⚙️ Workers",
                    style={
                        "text_align": "center",
                        "font_size": "0.7rem",
                        "font_weight": "600",
                        "color": COLORS["text_secondary"],
                        "margin_bottom": "0.75rem",
                        "text_transform": "uppercase",
                        "letter_spacing": "1px",
                    }
                ),
                rx.el.div(
                    rx.foreach(
                        State.agents[2:],  # Design, Code, Test, GitHub
                        agent_card_grid,
                    ),
                    style={
                        "display": "grid",
                        "grid_template_columns": "repeat(2, 180px)",
                        "gap": "1rem",
                        "justify_content": "center",
                    }
                ),
                style={
                    "flex": "1",
                    "padding": "1rem",
                    "background": "rgba(59, 130, 246, 0.05)",
                    "border_radius": "16px",
                    "border": "2px dashed rgba(59, 130, 246, 0.2)",
                }
            ),
            spacing="4",
            width="100%",
            align="start",
        ),
        # Container styles with office background
        style={
            "width": "100%",
            "background": """
                linear-gradient(135deg, rgba(248,250,252,0.92) 0%, rgba(241,245,249,0.92) 100%),
                url('https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=80')
            """,
            "background_size": "cover",
            "background_position": "center",
            "border_radius": "20px",
            "border": "1px solid #e2e8f0",
            "box_shadow": "0 10px 40px rgba(0,0,0,0.08)",
            "padding": "1.5rem",
        }
    )


# ============================================================
# SIDEBAR: Navigation sidebar
# ============================================================

def sidebar() -> rx.Component:
    """Render the sidebar."""
    return rx.el.aside(
        rx.vstack(
            # Logo
            rx.hstack(
                rx.text("🦞", font_size="2rem"),
                rx.vstack(
                    rx.heading("ClawCrew", size="5", margin="0"),
                    rx.text("Agent Dashboard", font_size="0.75rem", color=COLORS["text_secondary"]),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                padding="1rem",
            ),
            rx.divider(),
            # Navigation
            rx.vstack(
                rx.text("Navigation", font_size="0.75rem", color=COLORS["text_secondary"], padding_left="1rem"),
                nav_button("🏠", "Home", "home", State.current_page == "home"),
                nav_button("🤖", "Agents", "agents", State.current_page == "agents"),
                nav_button("📁", "Artifacts", "artifacts", State.current_page == "artifacts"),
                nav_button("📋", "Logs", "logs", State.current_page == "logs"),
                nav_button("⚙️", "Settings", "settings", State.current_page == "settings"),
                spacing="1",
                width="100%",
                padding="0.5rem",
            ),
            rx.divider(),
            # Agent list
            rx.vstack(
                rx.text("Agents", font_size="0.75rem", color=COLORS["text_secondary"], padding_left="1rem"),
                rx.foreach(
                    State.agents,
                    lambda a: rx.hstack(
                        rx.text(a["emoji"], font_size="1.2rem"),
                        rx.vstack(
                            rx.text(a["name"], font_weight="600", font_size="0.85rem"),
                            rx.text(a["role"], font_size="0.7rem", color=COLORS["text_secondary"]),
                            spacing="0",
                            align="start",
                        ),
                        status_dot(a["status"]),
                        spacing="2",
                        width="100%",
                        padding="0.5rem 1rem",
                        border_radius="8px",
                        _hover={"background": "#f1f5f9"},
                    ),
                ),
                spacing="1",
                width="100%",
            ),
            rx.spacer(),
            # Refresh controls
            rx.vstack(
                rx.hstack(
                    rx.text("Auto-refresh", font_size="0.85rem"),
                    rx.switch(
                        checked=State.auto_refresh,
                        on_change=State.toggle_refresh,
                    ),
                    justify="between",
                    width="100%",
                    padding="0 1rem",
                ),
                rx.button(
                    rx.hstack(rx.text("🔄"), rx.text("Refresh Now"), spacing="2"),
                    width="90%",
                    on_click=State.refresh_data,
                ),
                spacing="2",
                padding="1rem 0",
            ),
            spacing="2",
            width="100%",
            height="100vh",
        ),
        style={
            "width": "260px",
            "background": COLORS["card"],
            "border_right": f"1px solid {COLORS['border']}",
            "position": "fixed",
            "left": "0",
            "top": "0",
            "height": "100vh",
            "overflow_y": "auto",
        }
    )


# ============================================================
# TOP BAR: Stats and status legend
# ============================================================

def top_bar() -> rx.Component:
    """Render the top stats bar."""
    return rx.hstack(
        # Stats (left)
        rx.hstack(
            stat_item("Tasks", State.total_tasks.to_string()),
            stat_item("Running", State.agents_running.to_string()),
            stat_item("Tokens", "15.4K"),
            stat_item("Success", State.success_rate),
            spacing="6",
        ),
        rx.spacer(),
        # Status legend (right)
        rx.hstack(
            rx.hstack(rx.text("🟢"), rx.text("Online", font_size="0.8rem", color=COLORS["text_secondary"]), spacing="1"),
            rx.hstack(rx.text("🟠"), rx.text("Working", font_size="0.8rem", color=COLORS["text_secondary"]), spacing="1"),
            rx.hstack(rx.text("🟡"), rx.text("Away", font_size="0.8rem", color=COLORS["text_secondary"]), spacing="1"),
            rx.hstack(rx.text("⚪"), rx.text("Offline", font_size="0.8rem", color=COLORS["text_secondary"]), spacing="1"),
            spacing="4",
        ),
        width="100%",
        padding="0.75rem 1.5rem",
        background=COLORS["card"],
        border_radius="12px",
        border=f"1px solid {COLORS['border']}",
        margin_bottom="1rem",
    )


# ============================================================
# LOGS SECTION
# ============================================================

def logs_section() -> rx.Component:
    """Render the logs section."""
    agent_colors = {
        "orca": "#6366f1",
        "design": "#8b5cf6",
        "code": "#3b82f6",
        "test": "#10b981",
    }

    return rx.vstack(
        rx.heading("📜 Live Logs", size="4"),
        rx.el.div(
            rx.foreach(
                State.logs,
                lambda log: rx.hstack(
                    rx.text(log["timestamp"], color="#64748b", font_size="0.8rem", font_family="monospace"),
                    rx.text(f"[{log['agent']}]", color=agent_colors.get(log["agent"], "#64748b"), font_weight="600", font_size="0.8rem"),
                    rx.text(log["message"], font_size="0.8rem"),
                    spacing="2",
                    padding="0.4rem 0",
                    border_bottom="1px solid #334155",
                ),
            ),
            style={
                "background": "#1e293b",
                "border_radius": "12px",
                "padding": "1rem",
                "max_height": "300px",
                "overflow_y": "auto",
                "color": "#e2e8f0",
                "font_family": "monospace",
            }
        ),
        spacing="3",
        width="100%",
        align="start",
    )


# ============================================================
# MAIN PAGE: Home dashboard
# ============================================================

def home_page() -> rx.Component:
    """Render the home page."""
    return rx.vstack(
        # Top stats bar
        top_bar(),
        # Virtual Office (agents area)
        virtual_office(),
        rx.divider(),
        # Tasks section
        rx.vstack(
            rx.heading("📋 Tasks", size="4"),
            rx.el.div(
                rx.hstack(
                    rx.text("Create email validation function", font_weight="600"),
                    rx.text("ID: 20240214-153042 • Code phase", color=COLORS["text_secondary"], font_size="0.85rem"),
                    spacing="3",
                ),
                style={
                    "background": COLORS["card"],
                    "border_radius": "10px",
                    "padding": "0.75rem 1rem",
                    "border": f"1px solid {COLORS['border']}",
                }
            ),
            rx.progress(value=60),
            rx.text("Orca → Design ✓ → Code (working) → Test", font_size="0.85rem", color=COLORS["text_secondary"]),
            spacing="2",
            width="100%",
            align="start",
        ),
        rx.divider(),
        # Token usage & Logs
        rx.hstack(
            # Token chart placeholder
            rx.vstack(
                rx.heading("📊 Token Usage", size="4"),
                rx.el.div(
                    rx.foreach(
                        State.agents,
                        lambda a: rx.hstack(
                            rx.text(a["emoji"]),
                            rx.text(a["name"], width="80px"),
                            rx.el.div(
                                style={
                                    "height": "20px",
                                    "width": f"{a['tokens'] / 60}px",
                                    "background": a["color"],
                                    "border_radius": "4px",
                                }
                            ),
                            rx.text(f"{a['tokens']:,}", font_size="0.8rem"),
                            spacing="2",
                            align="center",
                        ),
                    ),
                    style={
                        "background": "#f8fafc",
                        "border_radius": "10px",
                        "padding": "1rem",
                    }
                ),
                spacing="3",
                width="60%",
                align="start",
            ),
            # Logs
            rx.box(logs_section(), width="40%"),
            spacing="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
        padding="1rem",
    )


# ============================================================
# APP: Main application
# ============================================================

def index() -> rx.Component:
    """Main app layout."""
    return rx.hstack(
        sidebar(),
        rx.el.main(
            rx.cond(
                State.current_page == "home",
                home_page(),
                rx.center(
                    rx.vstack(
                        rx.heading(f"📄 {State.current_page.to(str).upper()}", size="5"),
                        rx.text("Page content coming soon...", color=COLORS["text_secondary"]),
                        spacing="4",
                    ),
                    height="400px",
                ),
            ),
            style={
                "margin_left": "260px",
                "padding": "1.5rem",
                "min_height": "100vh",
                "background": COLORS["bg"],
                "width": "calc(100% - 260px)",
                "max_width": "100%",
            }
        ),
        spacing="0",
        width="100%",
    )


# Custom CSS for animations
custom_css = """
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.progress-gradient > div {
    background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 25%, #3b82f6 50%, #10b981 100%) !important;
}
"""

# App configuration
app = rx.App(
    style={
        "font_family": "Inter, system-ui, sans-serif",
    },
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)
app.add_page(index, title="ClawCrew Dashboard")
