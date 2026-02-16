"""
Task Stepper Component
Modern step-by-step task pipeline visualization.
"""

import reflex as rx
from ..theme import COLORS
from ..state import DashboardState


def step_icon(step) -> rx.Component:
    """Step icon with status-based styling."""
    bg_color = rx.match(
        step.status,
        ("completed", COLORS["status_online"]),
        ("active", COLORS["status_working"]),
        ("error", COLORS["status_error"]),
        "rgba(255, 255, 255, 0.1)",
    )

    border_color = rx.match(
        step.status,
        ("completed", f"{COLORS['status_online']}60"),
        ("active", f"{COLORS['status_working']}60"),
        ("error", f"{COLORS['status_error']}60"),
        COLORS["border_subtle"],
    )

    return rx.el.div(
        rx.cond(
            step.status == "completed",
            rx.text("✓", font_size="1rem", color="white"),
            rx.cond(
                step.status == "error",
                rx.text("✕", font_size="1rem", color="white"),
                rx.text(step.emoji, font_size="1.2rem"),
            ),
        ),
        style={
            "width": "48px",
            "height": "48px",
            "border_radius": "14px",
            "display": "flex",
            "align_items": "center",
            "justify_content": "center",
            "background": rx.cond(
                step.status == "pending",
                "rgba(255, 255, 255, 0.05)",
                f"linear-gradient(135deg, {bg_color}, {bg_color}dd)",
            ),
            "border": f"2px solid {border_color}",
            "box_shadow": rx.cond(
                step.status == "active",
                f"0 0 20px {COLORS['status_working']}40",
                "none",
            ),
            "animation": rx.cond(
                step.status == "active",
                "pulse-glow 2s infinite",
                "none",
            ),
        }
    )


def step_connector(is_completed: bool = False) -> rx.Component:
    """Connector line between steps."""
    return rx.el.div(
        rx.el.div(
            style={
                "height": "3px",
                "width": "100%",
                "background": rx.cond(
                    is_completed,
                    f"linear-gradient(90deg, {COLORS['status_online']}, {COLORS['status_online']}80)",
                    "rgba(255, 255, 255, 0.1)",
                ),
                "border_radius": "2px",
            }
        ),
        style={
            "flex": "1",
            "padding": "0 8px",
            "display": "flex",
            "align_items": "center",
        },
        class_name="stepper-connector",
    )


def stepper_step(step, index: int, total: int) -> rx.Component:
    """Individual step in the stepper."""
    text_color = rx.match(
        step.status,
        ("completed", COLORS["status_online"]),
        ("active", COLORS["status_working"]),
        ("error", COLORS["status_error"]),
        COLORS["text_muted"],
    )

    return rx.fragment(
        # Step content
        rx.el.div(
            # Icon
            step_icon(step),

            # Label and meta
            rx.vstack(
                rx.text(
                    step.name,
                    font_size="0.9rem",
                    font_weight="600",
                    color=rx.match(
                        step.status,
                        ("pending", COLORS["text_muted"]),
                        COLORS["text_primary"],
                    ),
                ),
                rx.text(
                    step.agent,
                    font_size="0.7rem",
                    color=COLORS["text_muted"],
                ),
                # Duration and tokens (if available)
                rx.cond(
                    step.duration != "--",
                    rx.hstack(
                        rx.text(
                            f"⏱ {step.duration}",
                            font_size="0.65rem",
                            color=text_color,
                        ),
                        rx.text(
                            f"📊 {step.tokens_used}",
                            font_size="0.65rem",
                            color=COLORS["text_muted"],
                        ),
                        spacing="2",
                    ),
                    rx.fragment(),
                ),
                spacing="0",
                align="center",
                margin_top="0.5rem",
            ),

            style={
                "display": "flex",
                "flex_direction": "column",
                "align_items": "center",
                "min_width": "80px",
            }
        ),
    )


def task_stepper() -> rx.Component:
    """
    Modern task pipeline stepper with icons, connectors, and status.
    """
    return rx.el.div(
        # Header
        rx.hstack(
            rx.hstack(
                rx.text("📋", font_size="1.1rem"),
                rx.text(
                    "Task Pipeline",
                    font_size="1.1rem",
                    font_weight="600",
                    color=COLORS["text_primary"],
                ),
                spacing="2",
            ),
            rx.spacer(),
            # Progress percentage
            rx.hstack(
                rx.text(
                    f"{DashboardState.current_task_progress}%",
                    font_size="0.9rem",
                    font_weight="700",
                    color=COLORS["primary"],
                ),
                rx.text(
                    "Complete",
                    font_size="0.8rem",
                    color=COLORS["text_muted"],
                ),
                spacing="1",
            ),
            width="100%",
            margin_bottom="1.5rem",
        ),

        # Task info
        rx.el.div(
            rx.hstack(
                rx.text("⚡", font_size="0.9rem"),
                rx.text(
                    "Create email validation function",
                    font_size="0.9rem",
                    font_weight="500",
                    color=COLORS["text_primary"],
                ),
                spacing="2",
            ),
            rx.text(
                "ID: 20240214-153042",
                font_size="0.75rem",
                color=COLORS["text_muted"],
                margin_top="4px",
            ),
            style={
                "background": "rgba(123, 76, 255, 0.1)",
                "border_radius": "12px",
                "padding": "0.875rem 1rem",
                "border_left": f"3px solid {COLORS['primary']}",
                "margin_bottom": "1.5rem",
            }
        ),

        # Stepper
        rx.el.div(
            rx.hstack(
                # Step 1: Orchestrate
                rx.el.div(
                    step_icon(DashboardState.task_steps[0]),
                    rx.vstack(
                        rx.text("Orchestrate", font_size="0.85rem", font_weight="600", color=COLORS["text_primary"]),
                        rx.text("Orca", font_size="0.7rem", color=COLORS["text_muted"]),
                        rx.text("⏱ 0.8s", font_size="0.65rem", color=COLORS["status_online"]),
                        spacing="0", align="center", margin_top="0.5rem",
                    ),
                    style={"display": "flex", "flex_direction": "column", "align_items": "center", "min_width": "80px"},
                ),
                # Connector 1 (completed)
                rx.el.div(
                    rx.el.div(style={"height": "3px", "width": "100%", "background": f"linear-gradient(90deg, {COLORS['status_online']}, {COLORS['status_online']}80)", "border_radius": "2px"}),
                    style={"flex": "1", "padding": "0 8px", "display": "flex", "align_items": "center", "margin_bottom": "60px"},
                ),
                # Step 2: Design
                rx.el.div(
                    step_icon(DashboardState.task_steps[1]),
                    rx.vstack(
                        rx.text("Design", font_size="0.85rem", font_weight="600", color=COLORS["text_primary"]),
                        rx.text("Design", font_size="0.7rem", color=COLORS["text_muted"]),
                        rx.text("⏱ 2.4s", font_size="0.65rem", color=COLORS["status_online"]),
                        spacing="0", align="center", margin_top="0.5rem",
                    ),
                    style={"display": "flex", "flex_direction": "column", "align_items": "center", "min_width": "80px"},
                ),
                # Connector 2 (completed)
                rx.el.div(
                    rx.el.div(style={"height": "3px", "width": "100%", "background": f"linear-gradient(90deg, {COLORS['status_online']}, {COLORS['status_online']}80)", "border_radius": "2px"}),
                    style={"flex": "1", "padding": "0 8px", "display": "flex", "align_items": "center", "margin_bottom": "60px"},
                ),
                # Step 3: Code (active)
                rx.el.div(
                    rx.el.div(
                        rx.text("💻", font_size="1.2rem"),
                        style={
                            "width": "48px", "height": "48px", "border_radius": "14px",
                            "display": "flex", "align_items": "center", "justify_content": "center",
                            "background": f"linear-gradient(135deg, {COLORS['status_working']}, {COLORS['status_working']}dd)",
                            "border": f"2px solid {COLORS['status_working']}60",
                            "box_shadow": f"0 0 20px {COLORS['status_working']}40",
                            "animation": "pulse-glow 2s infinite",
                        }
                    ),
                    rx.vstack(
                        rx.text("Code", font_size="0.85rem", font_weight="600", color=COLORS["text_primary"]),
                        rx.text("Code", font_size="0.7rem", color=COLORS["text_muted"]),
                        rx.text("⏱ --", font_size="0.65rem", color=COLORS["status_working"]),
                        spacing="0", align="center", margin_top="0.5rem",
                    ),
                    style={"display": "flex", "flex_direction": "column", "align_items": "center", "min_width": "80px"},
                ),
                # Connector 3 (pending)
                rx.el.div(
                    rx.el.div(style={"height": "3px", "width": "100%", "background": "rgba(255, 255, 255, 0.1)", "border_radius": "2px"}),
                    style={"flex": "1", "padding": "0 8px", "display": "flex", "align_items": "center", "margin_bottom": "60px"},
                ),
                # Step 4: Test (pending)
                rx.el.div(
                    rx.el.div(
                        rx.text("🧪", font_size="1.2rem"),
                        style={
                            "width": "48px", "height": "48px", "border_radius": "14px",
                            "display": "flex", "align_items": "center", "justify_content": "center",
                            "background": "rgba(255, 255, 255, 0.05)",
                            "border": f"2px solid {COLORS['border_subtle']}",
                        }
                    ),
                    rx.vstack(
                        rx.text("Test", font_size="0.85rem", font_weight="600", color=COLORS["text_muted"]),
                        rx.text("Test", font_size="0.7rem", color=COLORS["text_muted"]),
                        spacing="0", align="center", margin_top="0.5rem",
                    ),
                    style={"display": "flex", "flex_direction": "column", "align_items": "center", "min_width": "80px"},
                ),
                # Connector 4 (pending)
                rx.el.div(
                    rx.el.div(style={"height": "3px", "width": "100%", "background": "rgba(255, 255, 255, 0.1)", "border_radius": "2px"}),
                    style={"flex": "1", "padding": "0 8px", "display": "flex", "align_items": "center", "margin_bottom": "60px"},
                ),
                # Step 5: Deploy (pending)
                rx.el.div(
                    rx.el.div(
                        rx.text("🐙", font_size="1.2rem"),
                        style={
                            "width": "48px", "height": "48px", "border_radius": "14px",
                            "display": "flex", "align_items": "center", "justify_content": "center",
                            "background": "rgba(255, 255, 255, 0.05)",
                            "border": f"2px solid {COLORS['border_subtle']}",
                        }
                    ),
                    rx.vstack(
                        rx.text("Deploy", font_size="0.85rem", font_weight="600", color=COLORS["text_muted"]),
                        rx.text("GitHub", font_size="0.7rem", color=COLORS["text_muted"]),
                        spacing="0", align="center", margin_top="0.5rem",
                    ),
                    style={"display": "flex", "flex_direction": "column", "align_items": "center", "min_width": "80px"},
                ),
                align="start",
                justify="between",
                width="100%",
            ),
            style={
                "background": "rgba(255, 255, 255, 0.02)",
                "border_radius": "16px",
                "padding": "1.5rem",
                "overflow_x": "auto",
            }
        ),

        style={
            "background": "rgba(18, 18, 28, 0.6)",
            "backdrop_filter": "blur(20px)",
            "border_radius": "20px",
            "border": f"1px solid {COLORS['border_subtle']}",
            "padding": "1.5rem",
        }
    )
