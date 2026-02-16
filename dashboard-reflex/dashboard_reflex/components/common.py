"""
Common UI Components
Shared components: stat cards, buttons, skeletons, etc.
"""

import reflex as rx
from ..theme import COLORS
from ..state import DashboardState


def stat_card(icon: str, label: str, value, color: str = COLORS["primary"]) -> rx.Component:
    """
    Glassmorphism stat card with icon, label, and value.
    """
    return rx.el.div(
        rx.hstack(
            rx.el.div(
                rx.text(icon, font_size="1.3rem"),
                style={
                    "width": "44px",
                    "height": "44px",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "background": f"{color}20",
                    "border_radius": "12px",
                    "border": f"1px solid {color}30",
                }
            ),
            rx.vstack(
                rx.text(
                    label,
                    font_size="0.75rem",
                    color=COLORS["text_muted"],
                    font_weight="500",
                ),
                rx.text(
                    value,
                    font_size="1.4rem",
                    font_weight="700",
                    color=COLORS["text_primary"],
                    line_height="1",
                ),
                spacing="1",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        style={
            "background": "rgba(18, 18, 28, 0.7)",
            "backdrop_filter": "blur(20px)",
            "border_radius": "16px",
            "border": f"1px solid {COLORS['border_subtle']}",
            "padding": "1rem 1.25rem",
            "min_width": "160px",
            "box_shadow": "0 4px 20px rgba(0, 0, 0, 0.2)",
        }
    )


def glass_button(
    text: str,
    icon: str = "",
    variant: str = "default",
    on_click=None,
    loading: bool = False,
) -> rx.Component:
    """
    Glassmorphism button with variants: default, primary, danger.
    """
    variants = {
        "default": {
            "background": "rgba(255, 255, 255, 0.05)",
            "border": f"1px solid {COLORS['border_subtle']}",
            "color": COLORS["text_primary"],
            "_hover": {"background": "rgba(255, 255, 255, 0.08)"},
        },
        "primary": {
            "background": f"linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_dark']})",
            "border": "none",
            "color": "white",
            "_hover": {"opacity": "0.9"},
        },
        "danger": {
            "background": f"linear-gradient(135deg, {COLORS['status_error']}, #dc2626)",
            "border": "none",
            "color": "white",
            "_hover": {"opacity": "0.9"},
        },
    }

    style = variants.get(variant, variants["default"])

    return rx.el.button(
        rx.hstack(
            rx.cond(
                loading,
                rx.el.div(
                    style={
                        "width": "14px",
                        "height": "14px",
                        "border": "2px solid rgba(255,255,255,0.3)",
                        "border_top_color": "white",
                        "border_radius": "50%",
                        "animation": "spin 0.8s linear infinite",
                    }
                ),
                rx.fragment(
                    rx.text(icon, font_size="0.9rem") if icon else rx.fragment(),
                ),
            ),
            rx.text(text, font_size="0.85rem", font_weight="500"),
            spacing="2",
            align="center",
            justify="center",
        ),
        style={
            **style,
            "padding": "0.75rem 1.25rem",
            "border_radius": "12px",
            "cursor": "pointer",
            "transition": "all 0.2s ease",
            "font_weight": "500",
        },
        on_click=on_click,
    )


def skeleton_card(width: str = "200px", height: str = "280px") -> rx.Component:
    """
    Skeleton loading placeholder for cards.
    """
    return rx.el.div(
        # Avatar skeleton
        rx.el.div(
            style={
                "width": "72px",
                "height": "72px",
                "border_radius": "50%",
                "margin": "1rem auto",
            },
            class_name="skeleton",
        ),
        # Title skeleton
        rx.el.div(
            style={
                "width": "80px",
                "height": "16px",
                "margin": "0.5rem auto",
            },
            class_name="skeleton",
        ),
        # Subtitle skeleton
        rx.el.div(
            style={
                "width": "60px",
                "height": "12px",
                "margin": "0.25rem auto",
            },
            class_name="skeleton",
        ),
        # Badge skeleton
        rx.el.div(
            style={
                "width": "70px",
                "height": "24px",
                "border_radius": "12px",
                "margin": "1rem auto",
            },
            class_name="skeleton",
        ),
        # Stats skeleton
        rx.el.div(
            style={
                "width": "calc(100% - 2rem)",
                "height": "60px",
                "border_radius": "12px",
                "margin": "0.5rem auto",
            },
            class_name="skeleton",
        ),
        style={
            "width": width,
            "height": height,
            "background": "rgba(18, 18, 28, 0.6)",
            "border_radius": "20px",
            "border": f"1px solid {COLORS['border_subtle']}",
            "padding": "1rem",
        }
    )


def task_input_bar() -> rx.Component:
    """
    Task input bar for sending new tasks to Orca.
    """
    return rx.el.div(
        rx.hstack(
            rx.el.input(
                placeholder="Send a task to Orca...",
                value=DashboardState.new_task_input,
                on_change=DashboardState.set_new_task,
                style={
                    "flex": "1",
                    "padding": "14px 18px",
                    "background": "rgba(255, 255, 255, 0.05)",
                    "border": f"1px solid {COLORS['border_subtle']}",
                    "border_radius": "14px",
                    "color": COLORS["text_primary"],
                    "font_size": "0.9rem",
                    "outline": "none",
                    "_focus": {
                        "border_color": COLORS["primary"],
                        "box_shadow": f"0 0 0 3px {COLORS['primary']}20",
                    },
                    "_placeholder": {
                        "color": COLORS["text_muted"],
                    },
                },
            ),
            rx.el.button(
                rx.hstack(
                    rx.cond(
                        DashboardState.sending_task,
                        rx.el.div(
                            style={
                                "width": "16px",
                                "height": "16px",
                                "border": "2px solid rgba(255,255,255,0.3)",
                                "border_top_color": "white",
                                "border_radius": "50%",
                                "animation": "spin 0.8s linear infinite",
                            }
                        ),
                        rx.text("🚀", font_size="1rem"),
                    ),
                    rx.text("Send", font_size="0.9rem", font_weight="600"),
                    spacing="2",
                ),
                style={
                    "padding": "14px 24px",
                    "background": f"linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_dark']})",
                    "border": "none",
                    "border_radius": "14px",
                    "color": "white",
                    "cursor": "pointer",
                    "font_weight": "600",
                    "_hover": {
                        "opacity": "0.9",
                        "transform": "translateY(-1px)",
                    },
                    "_disabled": {
                        "opacity": "0.5",
                        "cursor": "not-allowed",
                    },
                },
                on_click=DashboardState.send_task,
                disabled=DashboardState.sending_task,
            ),
            spacing="3",
            width="100%",
        ),
        style={
            "background": "rgba(18, 18, 28, 0.8)",
            "backdrop_filter": "blur(20px)",
            "border_radius": "18px",
            "border": f"1px solid {COLORS['border_subtle']}",
            "padding": "0.75rem",
            "margin_bottom": "1.5rem",
        }
    )


def section_header(title: str, icon: str = "") -> rx.Component:
    """Section header with icon and title."""
    return rx.hstack(
        rx.text(icon, font_size="1.1rem") if icon else rx.fragment(),
        rx.text(
            title,
            font_size="1.1rem",
            font_weight="600",
            color=COLORS["text_primary"],
        ),
        spacing="2",
        margin_bottom="1rem",
    )


def top_stats_bar() -> rx.Component:
    """Top statistics bar."""
    return rx.hstack(
        stat_card("📋", "Total Tasks", DashboardState.total_tasks, COLORS["primary"]),
        stat_card("⚡", "Active", DashboardState.active_tasks, COLORS["status_working"]),
        stat_card("📊", "Tokens", DashboardState.total_tokens_formatted, COLORS["accent_cyan"]),
        stat_card("✓", "Success Rate", f"{DashboardState.success_rate}%", COLORS["status_online"]),
        spacing="4",
        width="100%",
        wrap="wrap",
    )
