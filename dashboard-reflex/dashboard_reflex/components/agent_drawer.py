"""
Agent Drawer Component
Slide-in panel showing detailed agent information.
"""

import reflex as rx
from ..theme import COLORS
from ..state import DashboardState


def mini_trend_chart(data: list, color: str) -> rx.Component:
    """
    Mini SVG trend line chart for token history.
    """
    # Calculate SVG path from data points
    # We'll use a simple line chart approach
    width = 120
    height = 40
    padding = 4

    return rx.el.div(
        rx.el.svg(
            # Grid lines
            rx.el.line(
                x1="0", y1=str(height // 2),
                x2=str(width), y2=str(height // 2),
                stroke="rgba(255,255,255,0.1)",
                stroke_width="1",
                stroke_dasharray="4,4",
            ),
            # Fill area (solid color with opacity)
            rx.el.path(
                d="M 4 30 L 16 28 L 28 22 L 40 25 L 52 20 L 64 18 L 76 22 L 88 15 L 100 18 L 112 12 L 112 40 L 4 40 Z",
                fill=f"{color}25",
            ),
            # Trend line
            rx.el.path(
                d="M 4 30 L 16 28 L 28 22 L 40 25 L 52 20 L 64 18 L 76 22 L 88 15 L 100 18 L 112 12",
                fill="none",
                stroke=color,
                stroke_width="2",
                stroke_linecap="round",
                stroke_linejoin="round",
            ),
            width=str(width),
            height=str(height),
            viewBox=f"0 0 {width} {height}",
        ),
        style={
            "width": f"{width}px",
            "height": f"{height}px",
        }
    )


def recent_output_item(output: str, index: int) -> rx.Component:
    """Single recent output item."""
    return rx.el.div(
        rx.hstack(
            rx.text(
                f"{index + 1}.",
                font_size="0.7rem",
                color=COLORS["text_muted"],
                min_width="20px",
            ),
            rx.text(
                output,
                font_size="0.8rem",
                color=COLORS["text_secondary"],
            ),
            spacing="2",
            width="100%",
        ),
        style={
            "padding": "8px 12px",
            "background": "rgba(255, 255, 255, 0.02)",
            "border_radius": "8px",
            "border_left": f"2px solid {COLORS['primary']}40",
            "margin_bottom": "6px",
        }
    )


def agent_drawer() -> rx.Component:
    """
    Slide-in drawer showing detailed agent information.
    Includes SOUL summary, current task, recent outputs, token trend.
    """
    agent = DashboardState.selected_agent

    return rx.drawer.root(
        rx.drawer.trigger(rx.fragment()),  # Triggered programmatically
        rx.drawer.overlay(
            style={
                "background": "rgba(0, 0, 0, 0.6)",
                "backdrop_filter": "blur(4px)",
            }
        ),
        rx.drawer.portal(
            rx.drawer.content(
                rx.cond(
                    agent,
                    rx.el.div(
                        # Header
                        rx.hstack(
                            rx.hstack(
                                rx.el.div(
                                    agent.emoji,
                                    style={
                                        "font_size": "2rem",
                                        "width": "56px",
                                        "height": "56px",
                                        "display": "flex",
                                        "align_items": "center",
                                        "justify_content": "center",
                                        "background": f"linear-gradient(145deg, {agent.color}30, transparent)",
                                        "border_radius": "14px",
                                        "border": f"1px solid {agent.color}40",
                                    }
                                ),
                                rx.vstack(
                                    rx.text(
                                        agent.name,
                                        font_size="1.5rem",
                                        font_weight="700",
                                        color=COLORS["text_primary"],
                                    ),
                                    rx.text(
                                        agent.role,
                                        font_size="0.85rem",
                                        color=COLORS["text_secondary"],
                                    ),
                                    spacing="1",
                                    align="start",
                                ),
                                spacing="4",
                                align="center",
                            ),
                            rx.spacer(),
                            rx.el.button(
                                "✕",
                                style={
                                    "background": "rgba(255,255,255,0.05)",
                                    "border": "none",
                                    "border_radius": "8px",
                                    "width": "36px",
                                    "height": "36px",
                                    "cursor": "pointer",
                                    "color": COLORS["text_secondary"],
                                    "font_size": "1.2rem",
                                    "_hover": {
                                        "background": "rgba(255,255,255,0.1)",
                                    }
                                },
                                on_click=DashboardState.close_drawer,
                            ),
                            width="100%",
                            padding="1.5rem",
                            border_bottom=f"1px solid {COLORS['border_subtle']}",
                        ),

                        # Content
                        rx.el.div(
                            # SOUL Summary Section
                            rx.el.div(
                                rx.hstack(
                                    rx.text("🧠", font_size="1rem"),
                                    rx.text(
                                        "SOUL Summary",
                                        font_weight="600",
                                        color=COLORS["text_primary"],
                                    ),
                                    spacing="2",
                                ),
                                rx.el.p(
                                    agent.soul_summary,
                                    style={
                                        "color": COLORS["text_secondary"],
                                        "font_size": "0.85rem",
                                        "line_height": "1.6",
                                        "margin_top": "0.75rem",
                                    }
                                ),
                                style={
                                    "background": "rgba(123, 76, 255, 0.08)",
                                    "border_radius": "14px",
                                    "padding": "1rem",
                                    "border": f"1px solid {COLORS['primary']}20",
                                    "margin_bottom": "1.25rem",
                                }
                            ),

                            # Stats Row
                            rx.hstack(
                                # Model
                                rx.el.div(
                                    rx.text("Model", font_size="0.7rem", color=COLORS["text_muted"]),
                                    rx.text(
                                        agent.model,
                                        font_size="0.85rem",
                                        font_weight="600",
                                        color=COLORS["text_primary"],
                                    ),
                                    style={
                                        "background": "rgba(255,255,255,0.03)",
                                        "border_radius": "10px",
                                        "padding": "0.75rem 1rem",
                                        "flex": "1",
                                    }
                                ),
                                # Status
                                rx.el.div(
                                    rx.text("Status", font_size="0.7rem", color=COLORS["text_muted"]),
                                    rx.text(
                                        agent.status.to(str).upper(),
                                        font_size="0.85rem",
                                        font_weight="600",
                                        color=rx.match(
                                            agent.status,
                                            ("online", COLORS["status_online"]),
                                            ("working", COLORS["status_working"]),
                                            COLORS["text_primary"],
                                        ),
                                    ),
                                    style={
                                        "background": "rgba(255,255,255,0.03)",
                                        "border_radius": "10px",
                                        "padding": "0.75rem 1rem",
                                        "flex": "1",
                                    }
                                ),
                                spacing="3",
                                width="100%",
                                margin_bottom="1.25rem",
                            ),

                            # Token Usage with Trend
                            rx.el.div(
                                rx.hstack(
                                    rx.vstack(
                                        rx.text("📊 Token Usage", font_size="0.8rem", color=COLORS["text_muted"]),
                                        rx.text(
                                            agent.tokens,
                                            font_size="1.8rem",
                                            font_weight="700",
                                            color=COLORS["text_primary"],
                                        ),
                                        spacing="1",
                                        align="start",
                                    ),
                                    rx.spacer(),
                                    mini_trend_chart(agent.token_history, agent.color),
                                    width="100%",
                                    align="center",
                                ),
                                style={
                                    "background": "rgba(255,255,255,0.03)",
                                    "border_radius": "14px",
                                    "padding": "1rem",
                                    "margin_bottom": "1.25rem",
                                }
                            ),

                            # Current Task
                            rx.cond(
                                agent.current_task != "",
                                rx.el.div(
                                    rx.text("⚡ Current Task", font_size="0.8rem", color=COLORS["text_muted"], margin_bottom="0.5rem"),
                                    rx.el.p(
                                        agent.current_task,
                                        style={
                                            "color": COLORS["text_primary"],
                                            "font_size": "0.9rem",
                                            "background": f"linear-gradient(90deg, {agent.color}15, transparent)",
                                            "padding": "0.75rem 1rem",
                                            "border_radius": "10px",
                                            "border_left": f"3px solid {agent.color}",
                                        }
                                    ),
                                    margin_bottom="1.25rem",
                                ),
                                rx.fragment(),
                            ),

                            # Recent Outputs
                            rx.el.div(
                                rx.text("📝 Recent Outputs", font_size="0.8rem", color=COLORS["text_muted"], margin_bottom="0.75rem"),
                                rx.foreach(
                                    agent.recent_outputs[:5],
                                    lambda output, idx: recent_output_item(output, idx),
                                ),
                            ),

                            style={
                                "padding": "1.5rem",
                                "overflow_y": "auto",
                                "flex": "1",
                            }
                        ),

                        # Footer Actions
                        rx.hstack(
                            rx.el.button(
                                rx.hstack(
                                    rx.text("📋"),
                                    rx.text("View Full Logs"),
                                    spacing="2",
                                ),
                                style={
                                    "flex": "1",
                                    "padding": "0.875rem",
                                    "background": "rgba(255,255,255,0.05)",
                                    "border": f"1px solid {COLORS['border_subtle']}",
                                    "border_radius": "12px",
                                    "color": COLORS["text_primary"],
                                    "cursor": "pointer",
                                    "font_size": "0.85rem",
                                    "_hover": {
                                        "background": "rgba(255,255,255,0.08)",
                                    }
                                },
                            ),
                            rx.el.button(
                                rx.hstack(
                                    rx.text("⏸️"),
                                    rx.text("Pause Agent"),
                                    spacing="2",
                                ),
                                style={
                                    "flex": "1",
                                    "padding": "0.875rem",
                                    "background": f"linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_dark']})",
                                    "border": "none",
                                    "border_radius": "12px",
                                    "color": "white",
                                    "cursor": "pointer",
                                    "font_size": "0.85rem",
                                    "_hover": {
                                        "opacity": "0.9",
                                    }
                                },
                            ),
                            spacing="3",
                            width="100%",
                            padding="1.5rem",
                            border_top=f"1px solid {COLORS['border_subtle']}",
                        ),

                        style={
                            "display": "flex",
                            "flex_direction": "column",
                            "height": "100%",
                        }
                    ),
                    # Fallback when no agent selected
                    rx.center(
                        rx.text("No agent selected", color=COLORS["text_muted"]),
                        height="100%",
                    ),
                ),
                style={
                    "width": "420px",
                    "height": "100vh",
                    "background": "linear-gradient(180deg, rgba(12,12,20,0.98) 0%, rgba(8,8,14,0.98) 100%)",
                    "border_left": f"1px solid {COLORS['border_subtle']}",
                    "backdrop_filter": "blur(30px)",
                },
                class_name="drawer-content",
            ),
        ),
        direction="right",
        open=DashboardState.drawer_open,
        on_open_change=lambda open: DashboardState.close_drawer() if not open else None,
    )
