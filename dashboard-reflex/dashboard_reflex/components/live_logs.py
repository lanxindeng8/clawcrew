"""
Live Logs Component
Real-time log viewer with filtering, search, and syntax highlighting.
"""

import reflex as rx
from ..theme import COLORS, AGENT_COLORS
from ..state import DashboardState


def filter_chip(agent: str, emoji: str) -> rx.Component:
    """Toggleable filter chip for agent selection."""
    is_selected = DashboardState.log_filter_agents.contains(agent)

    return rx.el.button(
        rx.hstack(
            rx.text(emoji, font_size="0.8rem"),
            rx.text(agent.title(), font_size="0.75rem"),
            spacing="1",
            align="center",
        ),
        style={
            "padding": "6px 12px",
            "border_radius": "20px",
            "background": rx.cond(
                is_selected,
                f"{AGENT_COLORS.get(agent.title(), COLORS['primary'])}30",
                rx.cond(
                    DashboardState.dark_mode,
                    "rgba(255, 255, 255, 0.05)",
                    "rgba(0, 0, 0, 0.05)",
                ),
            ),
            "border": rx.cond(
                is_selected,
                f"1px solid {AGENT_COLORS.get(agent.title(), COLORS['primary'])}60",
                rx.cond(
                    DashboardState.dark_mode,
                    f"1px solid {COLORS['border_subtle']}",
                    "1px solid rgba(0, 0, 0, 0.1)",
                ),
            ),
            "color": rx.cond(
                is_selected,
                rx.cond(DashboardState.dark_mode, COLORS["text_primary"], "#0f172a"),
                rx.cond(DashboardState.dark_mode, COLORS["text_secondary"], "#475569"),
            ),
            "cursor": "pointer",
            "transition": "all 0.2s ease",
            "_hover": {
                "background": rx.cond(
                    DashboardState.dark_mode,
                    "rgba(255, 255, 255, 0.1)",
                    "rgba(0, 0, 0, 0.08)",
                ),
            }
        },
        on_click=lambda: DashboardState.toggle_log_filter(agent),
    )


def log_entry(log) -> rx.Component:
    """Individual log entry with syntax highlighting."""
    agent_color = rx.match(
        log.agent,
        ("orca", AGENT_COLORS["Orca"]),
        ("design", AGENT_COLORS["Design"]),
        ("code", AGENT_COLORS["Code"]),
        ("test", AGENT_COLORS["Test"]),
        ("github", AGENT_COLORS["GitHub"]),
        ("audit", AGENT_COLORS["Audit"]),
        ("user", COLORS["accent_cyan"]),
        COLORS["text_muted"],
    )

    level_icon = rx.match(
        log.level,
        ("success", "✓"),
        ("warning", "⚠"),
        ("error", "✕"),
        "•",
    )

    level_color = rx.match(
        log.level,
        ("success", COLORS["status_online"]),
        ("warning", COLORS["status_away"]),
        ("error", COLORS["status_error"]),
        COLORS["text_muted"],
    )

    return rx.el.div(
        rx.hstack(
            # Timestamp
            rx.text(
                log.timestamp,
                font_size="0.75rem",
                color=COLORS["text_muted"],
                font_family="monospace",
                min_width="60px",
            ),
            # Level icon
            rx.text(
                level_icon,
                font_size="0.7rem",
                color=level_color,
                min_width="16px",
            ),
            # Agent badge
            rx.el.span(
                log.agent.to(str).upper(),
                style={
                    "background": f"{agent_color}20",
                    "color": agent_color,
                    "padding": "2px 8px",
                    "border_radius": "6px",
                    "font_size": "0.65rem",
                    "font_weight": "600",
                    "letter_spacing": "0.5px",
                    "min_width": "60px",
                    "text_align": "center",
                }
            ),
            # Message
            rx.text(
                log.message,
                font_size="0.8rem",
                color=rx.cond(
                    DashboardState.dark_mode,
                    COLORS["text_secondary"],
                    "#475569",
                ),
                flex="1",
            ),
            spacing="3",
            width="100%",
            align="center",
        ),
        style={
            "padding": "10px 12px",
            "border_bottom": rx.cond(
                DashboardState.dark_mode,
                f"1px solid {COLORS['border_subtle']}",
                "1px solid rgba(0, 0, 0, 0.06)",
            ),
            "transition": "background 0.2s ease",
            "_hover": {
                "background": rx.cond(
                    DashboardState.dark_mode,
                    "rgba(255, 255, 255, 0.02)",
                    "rgba(0, 0, 0, 0.02)",
                ),
            },
        },
        class_name="log-entry",
    )


def live_logs() -> rx.Component:
    """
    Live logs component with filtering, search, and auto-scroll.
    """
    return rx.el.div(
        # Header
        rx.hstack(
            rx.hstack(
                rx.text("📜", font_size="1.1rem"),
                rx.text(
                    "Live Logs",
                    font_size="1.1rem",
                    font_weight="600",
                    color=rx.cond(
                        DashboardState.dark_mode,
                        COLORS["text_primary"],
                        "#0f172a",
                    ),
                ),
                spacing="2",
            ),
            rx.spacer(),
            # Auto-scroll toggle
            rx.hstack(
                rx.text(
                    "Auto-scroll",
                    font_size="0.75rem",
                    color=COLORS["text_muted"],
                ),
                rx.el.button(
                    rx.cond(
                        DashboardState.log_auto_scroll,
                        rx.text("ON", font_size="0.7rem", font_weight="600"),
                        rx.text("OFF", font_size="0.7rem", font_weight="600"),
                    ),
                    style={
                        "padding": "4px 10px",
                        "border_radius": "8px",
                        "background": rx.cond(
                            DashboardState.log_auto_scroll,
                            f"{COLORS['status_online']}20",
                            rx.cond(
                                DashboardState.dark_mode,
                                "rgba(255, 255, 255, 0.05)",
                                "rgba(0, 0, 0, 0.05)",
                            ),
                        ),
                        "border": rx.cond(
                            DashboardState.log_auto_scroll,
                            f"1px solid {COLORS['status_online']}40",
                            rx.cond(
                                DashboardState.dark_mode,
                                f"1px solid {COLORS['border_subtle']}",
                                "1px solid rgba(0, 0, 0, 0.1)",
                            ),
                        ),
                        "color": rx.cond(
                            DashboardState.log_auto_scroll,
                            COLORS["status_online"],
                            COLORS["text_muted"],
                        ),
                        "cursor": "pointer",
                    },
                    on_click=DashboardState.toggle_auto_scroll,
                ),
                spacing="2",
                align="center",
            ),
            width="100%",
            margin_bottom="1rem",
        ),

        # Search and filters
        rx.el.div(
            # Search input
            rx.el.div(
                rx.el.input(
                    placeholder="Search logs...",
                    value=DashboardState.log_search_query,
                    on_change=DashboardState.set_log_search,
                    style={
                        "width": "100%",
                        "padding": "10px 14px 10px 36px",
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
                        "border_radius": "10px",
                        "color": rx.cond(
                            DashboardState.dark_mode,
                            COLORS["text_primary"],
                            "#0f172a",
                        ),
                        "font_size": "0.85rem",
                        "outline": "none",
                        "_focus": {
                            "border_color": COLORS["primary"],
                            "box_shadow": f"0 0 0 2px {COLORS['primary']}30",
                        },
                        "_placeholder": {
                            "color": COLORS["text_muted"],
                        },
                    },
                ),
                rx.el.span(
                    "🔍",
                    style={
                        "position": "absolute",
                        "left": "12px",
                        "top": "50%",
                        "transform": "translateY(-50%)",
                        "font_size": "0.9rem",
                        "opacity": "0.5",
                    }
                ),
                style={
                    "position": "relative",
                    "margin_bottom": "0.75rem",
                }
            ),

            # Filter chips
            rx.hstack(
                rx.text("Filter:", font_size="0.75rem", color=COLORS["text_muted"]),
                filter_chip("orca", "🦑"),
                filter_chip("design", "🎨"),
                filter_chip("code", "💻"),
                filter_chip("test", "🧪"),
                filter_chip("github", "🐙"),
                filter_chip("audit", "🔍"),
                rx.cond(
                    DashboardState.log_filter_agents.length() > 0,
                    rx.el.button(
                        "Clear",
                        style={
                            "padding": "4px 10px",
                            "border_radius": "8px",
                            "background": "rgba(239, 68, 68, 0.1)",
                            "border": f"1px solid {COLORS['status_error']}40",
                            "color": COLORS["status_error"],
                            "font_size": "0.7rem",
                            "cursor": "pointer",
                        },
                        on_click=DashboardState.clear_log_filters,
                    ),
                    rx.fragment(),
                ),
                spacing="2",
                wrap="wrap",
            ),

            margin_bottom="1rem",
        ),

        # Log entries
        rx.el.div(
            rx.foreach(
                DashboardState.filtered_logs,
                log_entry,
            ),
            style={
                "background": rx.cond(
                    DashboardState.dark_mode,
                    "rgba(10, 10, 18, 0.8)",
                    "rgba(255, 255, 255, 0.95)",
                ),
                "border_radius": "14px",
                "max_height": "350px",
                "overflow_y": "auto",
                "border": rx.cond(
                    DashboardState.dark_mode,
                    f"1px solid {COLORS['border_subtle']}",
                    "1px solid rgba(0, 0, 0, 0.08)",
                ),
            }
        ),

        # Footer stats
        rx.hstack(
            rx.text(
                f"Showing {DashboardState.filtered_logs.length()} logs",
                font_size="0.75rem",
                color=COLORS["text_muted"],
            ),
            rx.spacer(),
            rx.hstack(
                rx.el.div(
                    style={
                        "width": "8px",
                        "height": "8px",
                        "border_radius": "50%",
                        "background": COLORS["status_online"],
                        "animation": "status-pulse 1.5s infinite",
                    }
                ),
                rx.text(
                    "Live",
                    font_size="0.75rem",
                    color=COLORS["status_online"],
                ),
                spacing="1",
                align="center",
            ),
            width="100%",
            margin_top="0.75rem",
        ),

        style={
            "background": rx.cond(
                DashboardState.dark_mode,
                "rgba(18, 18, 28, 0.6)",
                "rgba(255, 255, 255, 0.9)",
            ),
            "backdrop_filter": "blur(20px)",
            "border_radius": "20px",
            "border": rx.cond(
                DashboardState.dark_mode,
                f"1px solid {COLORS['border_subtle']}",
                "1px solid rgba(0, 0, 0, 0.08)",
            ),
            "padding": "1.5rem",
        }
    )
