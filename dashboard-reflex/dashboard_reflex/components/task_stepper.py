"""
Task Pipeline Component
Animated pipeline flow visualization with modern Linear/Vercel-style design.
"""

import reflex as rx
from ..theme import COLORS, AGENT_COLORS
from ..state import DashboardState


def pipeline_step(
    emoji: str,
    name: str,
    agent: str,
    status: str,  # "completed", "active", "pending", "error"
    duration: str = "--",
    color: str = COLORS["primary"],
) -> rx.Component:
    """
    Pipeline step with status-based styling.
    """
    # Status-based colors
    is_completed = status == "completed"
    is_active = status == "active"
    is_error = status == "error"

    icon_bg = (
        COLORS["status_online"] if is_completed else
        COLORS["status_working"] if is_active else
        COLORS["status_error"] if is_error else
        "rgba(255, 255, 255, 0.05)"
    )

    border_color = (
        f"{COLORS['status_online']}60" if is_completed else
        f"{COLORS['status_working']}60" if is_active else
        f"{COLORS['status_error']}60" if is_error else
        COLORS["border_subtle"]
    )

    text_color = (
        COLORS["text_primary"] if (is_completed or is_active) else
        COLORS["text_muted"]
    )

    return rx.el.div(
        # Step icon
        rx.el.div(
            rx.cond(
                is_completed,
                rx.text("✓", font_size="1.1rem", color="white", font_weight="bold"),
                rx.text(emoji, font_size="1.3rem"),
            ),
            style={
                "width": "52px",
                "height": "52px",
                "border_radius": "16px",
                "display": "flex",
                "align_items": "center",
                "justify_content": "center",
                "background": (
                    f"linear-gradient(135deg, {icon_bg}, {icon_bg}cc)"
                    if (is_completed or is_active or is_error)
                    else "rgba(255, 255, 255, 0.03)"
                ),
                "border": f"2px solid {border_color}",
                "box_shadow": (
                    f"0 0 24px {COLORS['status_working']}50, 0 0 48px {COLORS['status_working']}20"
                    if is_active else "none"
                ),
                "transition": "all 0.3s ease",
            },
            class_name="pulse-glow" if is_active else "",
        ),

        # Step info
        rx.vstack(
            rx.text(
                name,
                font_size="0.85rem",
                font_weight="600",
                color=text_color,
            ),
            rx.text(
                agent,
                font_size="0.7rem",
                color=COLORS["text_muted"],
            ),
            rx.cond(
                duration != "--",
                rx.el.div(
                    rx.text(
                        f"⏱ {duration}",
                        font_size="0.65rem",
                        color=COLORS["status_online"] if is_completed else COLORS["status_working"],
                    ),
                    style={
                        "background": f"{COLORS['status_online']}15" if is_completed else f"{COLORS['status_working']}15",
                        "padding": "2px 8px",
                        "border_radius": "6px",
                        "margin_top": "4px",
                    }
                ),
                rx.cond(
                    is_active,
                    rx.el.div(
                        rx.text(
                            "In progress...",
                            font_size="0.65rem",
                            color=COLORS["status_working"],
                        ),
                        style={
                            "background": f"{COLORS['status_working']}15",
                            "padding": "2px 8px",
                            "border_radius": "6px",
                            "margin_top": "4px",
                        }
                    ),
                    rx.fragment(),
                ),
            ),
            spacing="0",
            align="center",
            margin_top="0.75rem",
        ),

        style={
            "display": "flex",
            "flex_direction": "column",
            "align_items": "center",
            "min_width": "90px",
            "position": "relative",
            "z_index": "2",
        }
    )


def pipeline_connector(is_completed: bool = False, is_active: bool = False) -> rx.Component:
    """
    Animated connector between pipeline steps.
    """
    return rx.el.div(
        # Background line
        rx.el.div(
            style={
                "height": "3px",
                "width": "100%",
                "background": COLORS["border_subtle"],
                "border_radius": "2px",
            }
        ),
        # Progress fill
        rx.el.div(
            style={
                "position": "absolute",
                "top": "0",
                "left": "0",
                "height": "3px",
                "width": "100%" if is_completed else ("50%" if is_active else "0%"),
                "background": f"linear-gradient(90deg, {COLORS['status_online']}, {COLORS['primary']})",
                "border_radius": "2px",
                "transition": "width 0.5s ease",
            }
        ),
        # Animated pulse (when active)
        rx.cond(
            is_active,
            rx.el.div(
                style={
                    "position": "absolute",
                    "top": "-2px",
                    "left": "50%",
                    "width": "8px",
                    "height": "8px",
                    "background": COLORS["status_working"],
                    "border_radius": "50%",
                    "box_shadow": f"0 0 12px {COLORS['status_working']}",
                    "animation": "flow-pulse 1.5s ease-in-out infinite",
                }
            ),
            rx.fragment(),
        ),
        style={
            "position": "relative",
            "flex": "1",
            "margin": "0 12px",
            "margin_bottom": "70px",  # Align with step icons
        }
    )


def task_stepper() -> rx.Component:
    """
    Modern animated task pipeline visualization.
    Shows the flow: Orchestrate → Design → Code → Test → Deploy
    """
    return rx.el.div(
        # Header
        rx.hstack(
            rx.hstack(
                rx.el.div(
                    "📋",
                    style={
                        "width": "32px",
                        "height": "32px",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "background": f"{COLORS['primary']}15",
                        "border_radius": "8px",
                        "font_size": "1rem",
                    }
                ),
                rx.vstack(
                    rx.text(
                        "Task Pipeline",
                        font_size="1rem",
                        font_weight="600",
                        color=COLORS["text_primary"],
                    ),
                    rx.text(
                        "Real-time workflow progress",
                        font_size="0.7rem",
                        color=COLORS["text_muted"],
                    ),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
            ),
            rx.spacer(),
            # Progress indicator
            rx.el.div(
                rx.hstack(
                    rx.el.div(
                        style={
                            "width": "100px",
                            "height": "6px",
                            "background": COLORS["border_subtle"],
                            "border_radius": "3px",
                            "overflow": "hidden",
                        },
                        children=[
                            rx.el.div(
                                style={
                                    "height": "100%",
                                    "width": f"{DashboardState.current_task_progress}%",
                                    "background": f"linear-gradient(90deg, {COLORS['status_online']}, {COLORS['primary']})",
                                    "border_radius": "3px",
                                    "transition": "width 0.5s ease",
                                }
                            )
                        ],
                    ),
                    rx.text(
                        f"{DashboardState.current_task_progress}%",
                        font_size="0.85rem",
                        font_weight="700",
                        color=COLORS["primary"],
                    ),
                    spacing="2",
                    align="center",
                ),
                style={
                    "background": "rgba(255, 255, 255, 0.03)",
                    "padding": "8px 14px",
                    "border_radius": "10px",
                }
            ),
            width="100%",
            margin_bottom="1.5rem",
        ),

        # Current task info card
        rx.el.div(
            rx.hstack(
                rx.el.div(
                    "⚡",
                    style={
                        "width": "36px",
                        "height": "36px",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "background": f"linear-gradient(135deg, {COLORS['primary']}30, {COLORS['secondary']}20)",
                        "border_radius": "10px",
                        "font_size": "1.1rem",
                    }
                ),
                rx.vstack(
                    rx.text(
                        DashboardState.current_task_name,
                        font_size="0.9rem",
                        font_weight="500",
                        color=COLORS["text_primary"],
                    ),
                    rx.hstack(
                        rx.text(
                            f"ID: {DashboardState.current_task_id}",
                            font_size="0.7rem",
                            color=COLORS["text_dim"],
                        ),
                        rx.el.div(
                            style={
                                "width": "4px",
                                "height": "4px",
                                "background": COLORS["text_dim"],
                                "border_radius": "50%",
                            }
                        ),
                        rx.text(
                            f"Started {DashboardState.current_task_started}",
                            font_size="0.7rem",
                            color=COLORS["text_dim"],
                        ),
                        spacing="2",
                        align="center",
                    ),
                    spacing="1",
                    align="start",
                ),
                spacing="3",
                align="center",
            ),
            style={
                "background": f"linear-gradient(135deg, {COLORS['primary']}10, transparent)",
                "border_radius": "14px",
                "padding": "1rem 1.25rem",
                "border_left": f"3px solid {COLORS['primary']}",
                "margin_bottom": "1.5rem",
            }
        ),

        # Pipeline visualization
        rx.el.div(
            rx.hstack(
                # Step 1: Orchestrate (Orca)
                pipeline_step("🦑", "Orchestrate", "Orca", "completed", "0.8s", AGENT_COLORS["Orca"]),
                pipeline_connector(is_completed=True),

                # Step 2: Design
                pipeline_step("🎨", "Design", "Design", "completed", "2.4s", AGENT_COLORS["Design"]),
                pipeline_connector(is_completed=True),

                # Step 3: Code (Active)
                pipeline_step("💻", "Code", "Code", "active", "--", AGENT_COLORS["Code"]),
                pipeline_connector(is_active=True),

                # Step 4: Test (Pending)
                pipeline_step("🧪", "Test", "Test", "pending", "--", AGENT_COLORS["Test"]),
                pipeline_connector(),

                # Step 5: Deploy (Pending)
                pipeline_step("🐙", "Deploy", "GitHub", "pending", "--", AGENT_COLORS["GitHub"]),

                align="start",
                justify="between",
                width="100%",
            ),
            style={
                "background": "rgba(255, 255, 255, 0.02)",
                "border_radius": "18px",
                "padding": "1.75rem 1.5rem",
                "overflow_x": "auto",
            }
        ),

        style={
            "background": "rgba(15, 15, 28, 0.7)",
            "backdrop_filter": "blur(24px)",
            "border_radius": "24px",
            "border": f"1px solid {COLORS['border_subtle']}",
            "padding": "1.5rem",
        }
    )
