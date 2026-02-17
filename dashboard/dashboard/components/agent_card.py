"""
Agent Card Component
Modern Linear/Vercel-style card with horizontal layout and subtle hover effects.
"""

import reflex as rx
from ..theme import COLORS, AGENT_COLORS
from ..state import DashboardState


def status_dot(status) -> rx.Component:
    """Small status indicator dot."""
    color = rx.match(
        status,
        ("online", COLORS["status_online"]),
        ("working", COLORS["status_working"]),
        ("away", COLORS["status_away"]),
        ("error", COLORS["status_error"]),
        COLORS["status_offline"],
    )

    return rx.el.div(
        style={
            "width": "8px",
            "height": "8px",
            "border_radius": "50%",
            "background": color,
            "box_shadow": rx.cond(
                status == "working",
                f"0 0 8px {COLORS['status_working']}",
                "none",
            ),
            "flex_shrink": "0",
        },
        class_name=rx.cond(status == "working", "pulse-glow", ""),
    )


def status_text(status) -> rx.Component:
    """Status label text."""
    color = rx.match(
        status,
        ("online", COLORS["status_online"]),
        ("working", COLORS["status_working"]),
        ("away", COLORS["status_away"]),
        ("error", COLORS["status_error"]),
        COLORS["status_offline"],
    )

    label = rx.match(
        status,
        ("online", "Online"),
        ("working", "Working"),
        ("away", "Away"),
        ("error", "Error"),
        "Offline",
    )

    return rx.text(
        label,
        font_size="0.7rem",
        font_weight="500",
        color=color,
    )


def agent_card(agent) -> rx.Component:
    """
    Modern agent card with horizontal layout.
    Avatar on left, info on right. Compact and info-dense.
    """
    agent_color = agent.color

    return rx.el.div(
        rx.hstack(
            # Left: Avatar
            rx.el.div(
                rx.el.div(
                    agent.emoji,
                    style={
                        "font_size": "1.8rem",
                    }
                ),
                style={
                    "width": "56px",
                    "height": "56px",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "background": f"linear-gradient(145deg, {agent_color}20, {agent_color}08)",
                    "border_radius": "14px",
                    "border": f"1px solid {agent_color}30",
                    "flex_shrink": "0",
                }
            ),

            # Right: Info
            rx.vstack(
                # Name + Status row
                rx.hstack(
                    rx.text(
                        agent.name,
                        font_size="1rem",
                        font_weight="600",
                        color=rx.cond(
                            DashboardState.dark_mode,
                            COLORS["text_primary"],
                            "#0f172a",
                        ),
                    ),
                    rx.spacer(),
                    rx.hstack(
                        status_dot(agent.status),
                        status_text(agent.status),
                        spacing="1",
                        align="center",
                    ),
                    width="100%",
                    align="center",
                ),

                # Role
                rx.text(
                    agent.role,
                    font_size="0.75rem",
                    color=COLORS["text_muted"],
                ),

                # Stats row
                rx.hstack(
                    # Tokens
                    rx.hstack(
                        rx.text("⚡", font_size="0.7rem"),
                        rx.text(
                            agent.tokens,
                            font_size="0.8rem",
                            font_weight="600",
                            color=rx.cond(
                                DashboardState.dark_mode,
                                "#e2e8f0",  # Brighter for dark mode
                                "#475569",
                            ),
                        ),
                        spacing="1",
                        align="center",
                    ),
                    # Tasks
                    rx.hstack(
                        rx.text("✓", font_size="0.7rem", color=COLORS["status_online"]),
                        rx.text(
                            agent.tasks_completed,
                            font_size="0.8rem",
                            font_weight="600",
                            color=rx.cond(
                                DashboardState.dark_mode,
                                "#e2e8f0",  # Brighter for dark mode
                                "#475569",
                            ),
                        ),
                        spacing="1",
                        align="center",
                    ),
                    # Model badge
                    rx.el.div(
                        rx.text(
                            agent.model.to(str).split("/")[-1][:12],
                            font_size="0.65rem",
                            color=rx.cond(
                                DashboardState.dark_mode,
                                "#94a3b8",  # Brighter for dark mode
                                "#64748b",
                            ),
                        ),
                        style={
                            "padding": "2px 8px",
                            "background": rx.cond(
                                DashboardState.dark_mode,
                                "rgba(255,255,255,0.1)",  # Slightly more visible
                                "rgba(0,0,0,0.05)",
                            ),
                            "border_radius": "6px",
                        }
                    ),
                    spacing="4",
                    margin_top="4px",
                ),

                spacing="1",
                align="start",
                flex="1",
                width="100%",
            ),

            spacing="4",
            align="center",
            width="100%",
        ),

        # Current task (if any)
        rx.cond(
            agent.current_task != "",
            rx.el.div(
                rx.text(
                    agent.current_task,
                    font_size="0.75rem",
                    color=rx.cond(
                        DashboardState.dark_mode,
                        COLORS["text_secondary"],
                        "#475569",
                    ),
                    style={
                        "overflow": "hidden",
                        "text_overflow": "ellipsis",
                        "white_space": "nowrap",
                    }
                ),
                style={
                    "margin_top": "12px",
                    "padding": "8px 12px",
                    "background": f"linear-gradient(90deg, {agent_color}10, transparent)",
                    "border_radius": "8px",
                    "border_left": f"2px solid {agent_color}",
                }
            ),
            rx.fragment(),
        ),

        style={
            "padding": "16px",
            "background": rx.cond(
                DashboardState.dark_mode,
                "rgba(15, 15, 30, 0.6)",
                "white",
            ),
            "backdrop_filter": "blur(20px)",
            "border_radius": "16px",
            "border": rx.cond(
                DashboardState.dark_mode,
                "1px solid rgba(255, 255, 255, 0.15)",
                "1px solid #e2e8f0",
            ),
            "box_shadow": rx.cond(
                DashboardState.dark_mode,
                "0 2px 8px rgba(0, 0, 0, 0.3)",
                "0 1px 3px rgba(0, 0, 0, 0.08)",
            ),
            "cursor": "pointer",
            "transition": "all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
            "width": "100%",
            "height": "140px",
            "min_height": "140px",
            "max_height": "140px",
            "box_sizing": "border-box",
            "overflow": "hidden",
            "_hover": {
                "transform": "translateY(-4px)",
                "border_color": f"{agent_color}50",
                "box_shadow": f"0 0 30px {agent_color}15, 0 8px 32px rgba(0, 0, 0, 0.12)",
            },
        },
        on_click=lambda: DashboardState.open_agent_drawer(agent.id),
        class_name="agent-card",
    )


def agent_card_compact(agent) -> rx.Component:
    """
    Compact agent card for grid layout (Virtual Office view).
    Vertical layout, smaller footprint.
    """
    agent_color = agent.color

    return rx.el.div(
        # Status indicator (top-left)
        rx.el.div(
            status_dot(agent.status),
            style={
                "position": "absolute",
                "top": "12px",
                "left": "12px",
            }
        ),

        # Main content
        rx.vstack(
            # Avatar
            rx.el.div(
                agent.emoji,
                style={
                    "font_size": "2rem",
                    "width": "52px",
                    "height": "52px",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "background": f"linear-gradient(145deg, {agent_color}20, {agent_color}08)",
                    "border_radius": "14px",
                    "border": f"1px solid {agent_color}30",
                }
            ),

            # Name
            rx.text(
                agent.name,
                font_size="0.95rem",
                font_weight="600",
                color=rx.cond(
                    DashboardState.dark_mode,
                    COLORS["text_primary"],
                    "#0f172a",
                ),
            ),

            # Role
            rx.text(
                agent.role,
                font_size="0.7rem",
                color=COLORS["text_muted"],
            ),

            # Status badge
            rx.hstack(
                status_dot(agent.status),
                status_text(agent.status),
                spacing="1",
                align="center",
                style={
                    "padding": "4px 10px",
                    "background": rx.cond(
                        DashboardState.dark_mode,
                        "rgba(255,255,255,0.03)",
                        "#f1f5f9",
                    ),
                    "border_radius": "8px",
                    "margin_top": "4px",
                }
            ),

            # Stats
            rx.hstack(
                rx.vstack(
                    rx.text(
                        agent.tokens,
                        font_size="0.85rem",
                        font_weight="600",
                        color=rx.cond(
                            DashboardState.dark_mode,
                            COLORS["text_primary"],
                            "#0f172a",
                        ),
                    ),
                    rx.text(
                        "tokens",
                        font_size="0.6rem",
                        color=rx.cond(
                            DashboardState.dark_mode,
                            "#94a3b8",  # Brighter for dark mode
                            "#64748b",
                        ),
                    ),
                    spacing="0",
                    align="center",
                ),
                rx.el.div(
                    style={
                        "width": "1px",
                        "height": "24px",
                        "background": rx.cond(
                            DashboardState.dark_mode,
                            COLORS["border_subtle"],
                            "rgba(0,0,0,0.08)",
                        ),
                    }
                ),
                rx.vstack(
                    rx.text(
                        agent.tasks_completed,
                        font_size="0.85rem",
                        font_weight="600",
                        color=rx.cond(
                            DashboardState.dark_mode,
                            COLORS["text_primary"],
                            "#0f172a",
                        ),
                    ),
                    rx.text(
                        "tasks",
                        font_size="0.6rem",
                        color=rx.cond(
                            DashboardState.dark_mode,
                            "#94a3b8",  # Brighter for dark mode
                            "#64748b",
                        ),
                    ),
                    spacing="0",
                    align="center",
                ),
                justify="center",
                spacing="4",
                margin_top="8px",
                padding="8px",
                background=rx.cond(
                    DashboardState.dark_mode,
                    "rgba(255,255,255,0.02)",
                    "rgba(0,0,0,0.02)",
                ),
                border_radius="8px",
                width="100%",
            ),

            spacing="2",
            align="center",
            padding="16px 12px",
        ),

        style={
            "position": "relative",
            "width": "160px",
            "background": rx.cond(
                DashboardState.dark_mode,
                "rgba(15, 15, 30, 0.6)",
                "white",
            ),
            "backdrop_filter": "blur(20px)",
            "border_radius": "16px",
            "border": rx.cond(
                DashboardState.dark_mode,
                f"1px solid {COLORS['border_subtle']}",
                "1px solid #e2e8f0",
            ),
            "box_shadow": rx.cond(
                DashboardState.dark_mode,
                "none",
                "0 1px 3px rgba(0, 0, 0, 0.08)",
            ),
            "cursor": "pointer",
            "transition": "all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
            "_hover": {
                "transform": "translateY(-4px) scale(1.02)",
                "border_color": f"{agent_color}40",
                "box_shadow": f"0 0 30px {agent_color}15, 0 8px 32px rgba(0, 0, 0, 0.12)",
            },
        },
        on_click=lambda: DashboardState.open_agent_drawer(agent.id),
        class_name="agent-card",
    )
