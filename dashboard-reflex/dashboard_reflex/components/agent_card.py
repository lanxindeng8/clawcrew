"""
Agent Card Component
Modern glassmorphism card with hover animations and status indicators.
"""

import reflex as rx
from ..theme import COLORS, GLASS_CARD
from ..state import DashboardState


def status_indicator(status) -> rx.Component:
    """Animated status indicator dot."""
    color = rx.match(
        status,
        ("online", COLORS["status_online"]),
        ("working", COLORS["status_working"]),
        ("away", COLORS["status_away"]),
        ("error", COLORS["status_error"]),
        COLORS["status_offline"],
    )

    return rx.el.div(
        rx.el.div(
            style={
                "width": "8px",
                "height": "8px",
                "border_radius": "50%",
                "background": color,
            }
        ),
        # Outer pulse ring for working status
        rx.cond(
            status == "working",
            rx.el.div(
                style={
                    "position": "absolute",
                    "top": "-4px",
                    "left": "-4px",
                    "width": "16px",
                    "height": "16px",
                    "border_radius": "50%",
                    "border": f"2px solid {COLORS['status_working']}",
                    "animation": "pulse-glow 2s infinite",
                    "opacity": "0.6",
                }
            ),
            rx.fragment(),
        ),
        style={
            "position": "relative",
            "width": "8px",
            "height": "8px",
        }
    )


def status_badge(status) -> rx.Component:
    """Status badge with icon and label."""
    icon = rx.match(
        status,
        ("online", "●"),
        ("working", "◉"),
        ("away", "○"),
        ("error", "✕"),
        "○",
    )

    label = rx.match(
        status,
        ("online", "Online"),
        ("working", "Working"),
        ("away", "Away"),
        ("error", "Error"),
        "Offline",
    )

    bg_color = rx.match(
        status,
        ("online", "rgba(34, 197, 94, 0.15)"),
        ("working", "rgba(249, 115, 22, 0.15)"),
        ("away", "rgba(251, 191, 36, 0.15)"),
        ("error", "rgba(239, 68, 68, 0.15)"),
        "rgba(107, 114, 128, 0.15)",
    )

    text_color = rx.match(
        status,
        ("online", COLORS["status_online"]),
        ("working", COLORS["status_working"]),
        ("away", COLORS["status_away"]),
        ("error", COLORS["status_error"]),
        COLORS["status_offline"],
    )

    border_color = rx.match(
        status,
        ("online", f"{COLORS['status_online']}40"),
        ("working", f"{COLORS['status_working']}40"),
        ("away", f"{COLORS['status_away']}40"),
        ("error", f"{COLORS['status_error']}40"),
        f"{COLORS['status_offline']}40",
    )

    return rx.el.div(
        rx.hstack(
            rx.text(icon, font_size="0.6rem"),
            rx.text(label, font_size="0.7rem", font_weight="600"),
            spacing="1",
            align="center",
        ),
        style={
            "padding": "4px 10px",
            "border_radius": "12px",
            "background": bg_color,
            "color": text_color,
            "border": rx.cond(
                status == "working",
                f"1px solid {COLORS['status_working']}40",
                f"1px solid {border_color}",
            ),
            "animation": rx.cond(status == "working", "status-pulse 1.5s infinite", "none"),
        }
    )


def agent_card(agent) -> rx.Component:
    """
    Modern glassmorphism agent card with hover effects.
    Clickable to open detail drawer.
    """
    return rx.el.div(
        # Gradient border overlay (visible on hover)
        rx.el.div(
            style={
                "position": "absolute",
                "inset": "-1px",
                "border_radius": "22px",
                "background": f"linear-gradient(135deg, {agent.color}40, transparent 50%, {COLORS['accent_cyan']}30)",
                "opacity": "0",
                "transition": "opacity 0.4s ease",
                "pointer_events": "none",
                "z_index": "0",
            },
            class_name="gradient-border",
        ),

        # Card content
        rx.el.div(
            # Top row: Status + Desktop icon
            rx.hstack(
                status_indicator(agent.status),
                rx.spacer(),
                rx.el.div(
                    "🖥️",
                    style={
                        "font_size": "1rem",
                        "opacity": "0.6",
                    }
                ),
                width="100%",
                padding_x="0.5rem",
            ),

            # Avatar with glow
            rx.el.div(
                rx.el.div(
                    agent.emoji,
                    style={
                        "font_size": "2.5rem",
                        "filter": "drop-shadow(0 4px 8px rgba(0,0,0,0.3))",
                    }
                ),
                style={
                    "width": "72px",
                    "height": "72px",
                    "margin": "0.75rem auto",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "background": f"linear-gradient(145deg, {agent.color}20, transparent)",
                    "border_radius": "50%",
                    "border": f"2px solid {agent.color}50",
                    "box_shadow": f"0 0 30px {agent.color}20",
                }
            ),

            # Name
            rx.el.h4(
                agent.name,
                style={
                    "text_align": "center",
                    "margin": "0.25rem 0",
                    "font_size": "1.1rem",
                    "font_weight": "700",
                    "color": COLORS["text_primary"],
                    "letter_spacing": "0.5px",
                }
            ),

            # Role
            rx.el.p(
                agent.role,
                style={
                    "text_align": "center",
                    "color": COLORS["text_secondary"],
                    "font_size": "0.75rem",
                    "margin": "0 0 0.75rem",
                }
            ),

            # Status badge
            rx.center(
                status_badge(agent.status),
                margin_bottom="0.75rem",
            ),

            # Stats section
            rx.el.div(
                rx.hstack(
                    rx.vstack(
                        rx.text("📊", font_size="0.8rem"),
                        rx.text(
                            agent.tokens,
                            font_weight="700",
                            font_size="0.9rem",
                            color=COLORS["text_primary"],
                        ),
                        rx.text("tokens", font_size="0.6rem", color=COLORS["text_muted"]),
                        spacing="0",
                        align="center",
                    ),
                    rx.el.div(
                        style={
                            "width": "1px",
                            "height": "40px",
                            "background": COLORS["border_subtle"],
                        }
                    ),
                    rx.vstack(
                        rx.text("✓", font_size="0.8rem"),
                        rx.text(
                            agent.tasks_completed,
                            font_weight="700",
                            font_size="0.9rem",
                            color=COLORS["text_primary"],
                        ),
                        rx.text("tasks", font_size="0.6rem", color=COLORS["text_muted"]),
                        spacing="0",
                        align="center",
                    ),
                    justify="center",
                    spacing="5",
                    width="100%",
                ),
                style={
                    "background": "rgba(255, 255, 255, 0.03)",
                    "border_radius": "12px",
                    "padding": "0.75rem",
                    "border": f"1px solid {COLORS['border_subtle']}",
                }
            ),

            # Current task (if any)
            rx.cond(
                agent.current_task != "",
                rx.el.div(
                    rx.hstack(
                        rx.text("💬", font_size="0.7rem"),
                        rx.text(
                            agent.current_task,
                            font_size="0.7rem",
                            color=COLORS["text_secondary"],
                            style={
                                "overflow": "hidden",
                                "text_overflow": "ellipsis",
                                "white_space": "nowrap",
                            }
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    style={
                        "background": f"linear-gradient(90deg, {agent.color}10, transparent)",
                        "border_radius": "8px",
                        "padding": "8px 10px",
                        "margin_top": "0.75rem",
                        "border_left": f"3px solid {agent.color}",
                    }
                ),
                rx.fragment(),
            ),

            # Inner card styling
            style={
                "position": "relative",
                "z_index": "1",
                "padding": "1rem",
            }
        ),

        # Outer card container
        style={
            "position": "relative",
            "width": "200px",
            "background": "rgba(18, 18, 28, 0.8)",
            "backdrop_filter": "blur(20px)",
            "border_radius": "20px",
            "border": f"1px solid {COLORS['border_subtle']}",
            "box_shadow": """
                0 8px 32px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.05)
            """,
            "cursor": "pointer",
            "transition": "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
            "overflow": "hidden",
            "_hover": {
                "transform": "translateY(-8px) scale(1.02)",
                "border": f"1px solid {agent.color}50",
                "box_shadow": f"""
                    0 20px 50px rgba(0, 0, 0, 0.4),
                    0 0 40px {agent.color}20
                """,
            },
        },
        on_click=lambda: DashboardState.open_agent_drawer(agent.id),
        class_name="agent-card",
    )
