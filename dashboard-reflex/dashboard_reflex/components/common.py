"""
Common UI Components
Shared components: stat cards, buttons, skeletons, etc.
Linear/Vercel-style design with trend indicators.
"""

import reflex as rx
from ..theme import COLORS
from ..state import DashboardState


def stat_card(
    icon: str,
    label: str,
    value,
    color: str = COLORS["primary"],
    trend: str = "",
    trend_up: bool = True,
) -> rx.Component:
    """
    Modern stat card with trend indicator and subtle icon background.
    Linear/Vercel-style design.
    """
    trend_color = COLORS["status_online"] if trend_up else COLORS["status_error"]
    trend_icon = "↑" if trend_up else "↓"

    return rx.el.div(
        # Large faded icon background
        rx.el.div(
            icon,
            style={
                "position": "absolute",
                "right": "12px",
                "top": "50%",
                "transform": "translateY(-50%)",
                "font_size": "3.5rem",
                "opacity": "0.06",
                "pointer_events": "none",
            }
        ),

        # Main content
        rx.vstack(
            # Label
            rx.text(
                label.upper(),
                font_size="0.65rem",
                font_weight="600",
                color=rx.cond(
                    DashboardState.dark_mode,
                    "#94a3b8",  # Brighter for dark mode contrast
                    "#64748b",
                ),
                letter_spacing="1px",
            ),

            # Value row with trend
            rx.hstack(
                rx.text(
                    value,
                    font_size="1.75rem",
                    font_weight="700",
                    color=rx.cond(
                        DashboardState.dark_mode,
                        COLORS["text_primary"],
                        "#0f172a",
                    ),
                    line_height="1",
                ),
                rx.cond(
                    trend != "",
                    rx.el.div(
                        rx.hstack(
                            rx.text(trend_icon, font_size="0.65rem"),
                            rx.text(trend, font_size="0.7rem", font_weight="600"),
                            spacing="0",
                            align="center",
                        ),
                        style={
                            "padding": "3px 8px",
                            "background": f"{trend_color}15",
                            "border_radius": "6px",
                            "color": trend_color,
                        }
                    ),
                    rx.fragment(),
                ),
                spacing="3",
                align="center",
            ),

            # Icon badge
            rx.el.div(
                rx.text(icon, font_size="1rem"),
                style={
                    "width": "32px",
                    "height": "32px",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "background": f"{color}15",
                    "border_radius": "8px",
                    "margin_top": "8px",
                }
            ),

            spacing="1",
            align="start",
            width="100%",
        ),

        # Left accent bar
        rx.el.div(
            style={
                "position": "absolute",
                "left": "0",
                "top": "0",
                "bottom": "0",
                "width": "4px",
                "background": color,
                "border_radius": "16px 0 0 16px",
            }
        ),

        style={
            "position": "relative",
            "background": rx.cond(
                DashboardState.dark_mode,
                "rgba(15, 15, 28, 0.7)",
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
            "padding": "1rem 1.25rem 1rem 1.5rem",
            "min_width": "180px",
            "flex": "1",
            "overflow": "hidden",
            "transition": "all 0.25s ease",
            "_hover": {
                "border_color": f"{color}40",
                "transform": "translateY(-2px)",
                "box_shadow": f"0 8px 24px {color}15",
            },
        }
    )


def stat_card_mini(icon: str, label: str, value, color: str = COLORS["primary"]) -> rx.Component:
    """
    Compact stat card for smaller displays.
    """
    return rx.el.div(
        rx.hstack(
            rx.el.div(
                rx.text(icon, font_size="1rem"),
                style={
                    "width": "36px",
                    "height": "36px",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "background": f"{color}15",
                    "border_radius": "10px",
                }
            ),
            rx.vstack(
                rx.text(
                    value,
                    font_size="1.1rem",
                    font_weight="700",
                    color=rx.cond(
                        DashboardState.dark_mode,
                        COLORS["text_primary"],
                        "#0f172a",
                    ),
                    line_height="1",
                ),
                rx.text(
                    label,
                    font_size="0.65rem",
                    color=rx.cond(
                        DashboardState.dark_mode,
                        COLORS["text_muted"],
                        "#64748b",
                    ),
                ),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        style={
            "background": rx.cond(
                DashboardState.dark_mode,
                "rgba(15, 15, 28, 0.6)",
                "white",
            ),
            "border_radius": "12px",
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
            "padding": "0.75rem 1rem",
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
            "background": rx.cond(
                DashboardState.dark_mode,
                "rgba(18, 18, 28, 0.6)",
                "rgba(255, 255, 255, 0.9)",
            ),
            "border_radius": "20px",
            "border": rx.cond(
                DashboardState.dark_mode,
                f"1px solid {COLORS['border_subtle']}",
                "1px solid rgba(0, 0, 0, 0.08)",
            ),
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
                    "background": rx.cond(
                        DashboardState.dark_mode,
                        "rgba(255, 255, 255, 0.05)",
                        "rgba(0, 0, 0, 0.03)",
                    ),
                    "border": rx.cond(
                        DashboardState.dark_mode,
                        f"1px solid {COLORS['border_subtle']}",
                        "1px solid rgba(0, 0, 0, 0.1)",
                    ),
                    "border_radius": "14px",
                    "color": rx.cond(
                        DashboardState.dark_mode,
                        COLORS["text_primary"],
                        "#0f172a",
                    ),
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
            "background": rx.cond(
                DashboardState.dark_mode,
                "rgba(18, 18, 28, 0.8)",
                "white",
            ),
            "backdrop_filter": "blur(20px)",
            "border_radius": "18px",
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
            color=rx.cond(
                DashboardState.dark_mode,
                COLORS["text_primary"],
                "#0f172a",
            ),
        ),
        spacing="2",
        margin_bottom="1rem",
    )


def top_stats_bar() -> rx.Component:
    """Top statistics bar with trend indicators."""
    return rx.el.div(
        rx.hstack(
            stat_card(
                "📋",
                "Total Tasks",
                DashboardState.total_tasks,
                COLORS["primary"],
                trend="+12%",
                trend_up=True,
            ),
            stat_card(
                "⚡",
                "Active Now",
                DashboardState.active_tasks,
                COLORS["status_working"],
                trend="",
                trend_up=True,
            ),
            stat_card(
                "🔥",
                "Tokens Used",
                DashboardState.total_tokens_formatted,
                COLORS["accent_cyan"],
                trend="+8%",
                trend_up=True,
            ),
            stat_card(
                "✓",
                "Success Rate",
                f"{DashboardState.success_rate}%",
                COLORS["status_online"],
                trend="+2%",
                trend_up=True,
            ),
            spacing="4",
            width="100%",
        ),
        style={
            "display": "grid",
            "grid_template_columns": "repeat(4, 1fr)",
            "gap": "1rem",
            "width": "100%",
        }
    )
