"""
Sidebar Component
Collapsible navigation sidebar with modern Linear/Vercel-style design.
"""

import reflex as rx
from ..theme import COLORS, GRADIENT_PRIMARY
from ..state import DashboardState


def nav_item(icon: str, label: str, page: str) -> rx.Component:
    """Navigation menu item with pill-shaped active indicator."""
    is_active = DashboardState.current_page == page

    return rx.el.button(
        rx.hstack(
            rx.el.div(
                icon,
                style={
                    "font_size": "1.1rem",
                    "width": "24px",
                    "text_align": "center",
                }
            ),
            rx.cond(
                ~DashboardState.sidebar_collapsed,
                rx.text(
                    label,
                    font_size="0.9rem",
                    font_weight=rx.cond(is_active, "600", "400"),
                ),
                rx.fragment(),
            ),
            spacing="3",
            width="100%",
            align="center",
        ),
        style={
            "width": "100%",
            "padding": "10px 14px",
            "border_radius": "10px",
            "background": rx.cond(
                is_active,
                f"linear-gradient(135deg, {COLORS['primary']}20, {COLORS['secondary']}12)",
                "transparent",
            ),
            "border": rx.cond(
                is_active,
                f"1px solid {COLORS['border_accent']}",
                "1px solid transparent",
            ),
            "color": rx.cond(
                is_active,
                COLORS["text_primary"],
                COLORS["text_secondary"],
            ),
            "cursor": "pointer",
            "transition": "all 0.2s ease",
            "text_align": "left",
            "_hover": {
                "background": rx.cond(
                    is_active,
                    f"linear-gradient(135deg, {COLORS['primary']}25, {COLORS['secondary']}15)",
                    "rgba(124, 58, 237, 0.08)",
                ),
                "color": COLORS["text_primary"],
            },
        },
        on_click=lambda: DashboardState.navigate(page),
    )


def mini_sparkline(data: list, color: str) -> rx.Component:
    """Mini sparkline chart for agent activity."""
    # Simple SVG sparkline
    width = 40
    height = 16

    return rx.el.svg(
        # Simple line approximation
        rx.el.path(
            d="M 0 12 L 8 8 L 16 10 L 24 6 L 32 8 L 40 4",
            fill="none",
            stroke=color,
            stroke_width="1.5",
            stroke_linecap="round",
            stroke_linejoin="round",
            opacity="0.7",
        ),
        width=str(width),
        height=str(height),
        viewBox=f"0 0 {width} {height}",
        style={"opacity": "0.8"},
    )


def agent_list_item(agent) -> rx.Component:
    """Compact agent status in sidebar with activity sparkline."""
    status_color = rx.match(
        agent.status,
        ("online", COLORS["status_online"]),
        ("working", COLORS["status_working"]),
        ("away", COLORS["status_away"]),
        ("error", COLORS["status_error"]),
        COLORS["status_offline"],
    )

    return rx.hstack(
        # Avatar
        rx.el.div(
            agent.emoji,
            style={
                "font_size": "1rem",
                "width": "32px",
                "height": "32px",
                "display": "flex",
                "align_items": "center",
                "justify_content": "center",
                "background": f"{agent.color}15",
                "border_radius": "8px",
                "flex_shrink": "0",
            }
        ),
        rx.cond(
            ~DashboardState.sidebar_collapsed,
            rx.fragment(
                rx.vstack(
                    rx.text(
                        agent.name,
                        font_size="0.85rem",
                        font_weight="500",
                        color=COLORS["text_primary"],
                    ),
                    rx.hstack(
                        # Status dot
                        rx.el.div(
                            style={
                                "width": "6px",
                                "height": "6px",
                                "border_radius": "50%",
                                "background": status_color,
                                "box_shadow": rx.cond(
                                    agent.status == "working",
                                    f"0 0 6px {COLORS['status_working']}",
                                    "none",
                                ),
                            }
                        ),
                        rx.text(
                            agent.status.to(str).title(),
                            font_size="0.7rem",
                            color=COLORS["text_muted"],
                        ),
                        spacing="1",
                        align="center",
                    ),
                    spacing="0",
                    align="start",
                    flex="1",
                ),
                # Sparkline
                mini_sparkline(agent.token_history, agent.color),
            ),
            rx.fragment(),
        ),
        spacing="3",
        width="100%",
        padding="8px 10px",
        border_radius="10px",
        cursor="pointer",
        align="center",
        style={
            "transition": "all 0.15s ease",
            "_hover": {
                "background": "rgba(255, 255, 255, 0.04)",
            },
        },
        on_click=lambda: DashboardState.open_agent_drawer(agent.id),
    )


def sidebar() -> rx.Component:
    """
    Collapsible sidebar with navigation and agent list.
    Linear/Vercel-style design with modern aesthetics.
    """
    return rx.el.aside(
        rx.vstack(
            # Logo section
            rx.hstack(
                rx.el.div(
                    "🦞",
                    style={
                        "font_size": "1.8rem",
                        "width": "44px",
                        "height": "44px",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "background": f"linear-gradient(135deg, {COLORS['primary']}25, {COLORS['secondary']}15)",
                        "border_radius": "12px",
                        "border": f"1px solid {COLORS['border_accent']}",
                    }
                ),
                rx.cond(
                    ~DashboardState.sidebar_collapsed,
                    rx.vstack(
                        rx.text(
                            "ClawCrew",
                            font_size="1.15rem",
                            font_weight="700",
                            color=COLORS["text_primary"],
                            letter_spacing="0.3px",
                        ),
                        rx.text(
                            "AI Agent Dashboard",
                            font_size="0.7rem",
                            color=COLORS["text_muted"],
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.fragment(),
                ),
                spacing="3",
                align="center",
                width="100%",
                padding="4px",
            ),

            # Collapse toggle button
            rx.el.button(
                rx.cond(
                    DashboardState.sidebar_collapsed,
                    rx.text("»", font_size="1rem", font_weight="bold"),
                    rx.text("«", font_size="1rem", font_weight="bold"),
                ),
                style={
                    "position": "absolute",
                    "right": "-14px",
                    "top": "60px",
                    "width": "28px",
                    "height": "28px",
                    "border_radius": "50%",
                    "background": COLORS["bg_dark"],
                    "border": f"1px solid {COLORS['border_muted']}",
                    "color": COLORS["text_secondary"],
                    "cursor": "pointer",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "z_index": "110",
                    "transition": "all 0.2s ease",
                    "_hover": {
                        "background": COLORS["primary"],
                        "border_color": COLORS["primary"],
                        "color": "white",
                        "transform": "scale(1.1)",
                    },
                },
                on_click=DashboardState.toggle_sidebar,
            ),

            # Spacer
            rx.el.div(style={"height": "20px"}),

            # Navigation section
            rx.el.div(
                rx.cond(
                    ~DashboardState.sidebar_collapsed,
                    rx.text(
                        "NAVIGATION",
                        font_size="0.65rem",
                        font_weight="600",
                        color=COLORS["text_dim"],
                        letter_spacing="1.2px",
                        margin_bottom="8px",
                        padding_left="6px",
                    ),
                    rx.fragment(),
                ),
                rx.vstack(
                    nav_item("🏠", "Home", "home"),
                    nav_item("🤖", "Agents", "agents"),
                    nav_item("📁", "Artifacts", "artifacts"),
                    nav_item("📋", "Logs", "logs"),
                    nav_item("⚙️", "Settings", "settings"),
                    spacing="2",
                    width="100%",
                ),
                width="100%",
                margin_bottom="20px",
            ),

            # Divider
            rx.el.div(
                style={
                    "height": "1px",
                    "width": "100%",
                    "background": f"linear-gradient(90deg, transparent, {COLORS['border_subtle']}, transparent)",
                    "margin": "8px 0",
                }
            ),

            # Agents section
            rx.el.div(
                rx.cond(
                    ~DashboardState.sidebar_collapsed,
                    rx.hstack(
                        rx.text(
                            "AGENTS",
                            font_size="0.65rem",
                            font_weight="600",
                            color=COLORS["text_dim"],
                            letter_spacing="1.2px",
                        ),
                        rx.spacer(),
                        rx.el.div(
                            rx.text(
                                DashboardState.active_agents_count,
                                font_size="0.65rem",
                                font_weight="600",
                                color=COLORS["status_online"],
                            ),
                            style={
                                "padding": "2px 8px",
                                "background": f"{COLORS['status_online']}15",
                                "border_radius": "10px",
                            }
                        ),
                        width="100%",
                        margin_bottom="8px",
                        padding_left="6px",
                        padding_right="6px",
                    ),
                    rx.fragment(),
                ),
                rx.el.div(
                    rx.foreach(
                        DashboardState.agents,
                        agent_list_item,
                    ),
                    style={
                        "display": "flex",
                        "flex_direction": "column",
                        "gap": "4px",
                        "width": "100%",
                    }
                ),
                width="100%",
                flex="1",
                overflow_y="auto",
                overflow_x="hidden",
                padding_right="4px",
            ),

            rx.spacer(),

            # Footer controls
            rx.el.div(
                # Theme toggle (Dark/Light mode)
                rx.el.button(
                    rx.hstack(
                        rx.cond(
                            DashboardState.dark_mode,
                            rx.text("🌙", font_size="1rem"),
                            rx.text("☀️", font_size="1rem"),
                        ),
                        rx.cond(
                            ~DashboardState.sidebar_collapsed,
                            rx.text(
                                rx.cond(
                                    DashboardState.dark_mode,
                                    "Dark Mode",
                                    "Light Mode",
                                ),
                                font_size="0.8rem",
                                font_weight="500",
                            ),
                            rx.fragment(),
                        ),
                        spacing="2",
                        align="center",
                        justify="center",
                    ),
                    style={
                        "width": "100%",
                        "padding": "10px 14px",
                        "background": rx.cond(
                            DashboardState.dark_mode,
                            "rgba(255, 255, 255, 0.05)",
                            "rgba(0, 0, 0, 0.05)",
                        ),
                        "border": rx.cond(
                            DashboardState.dark_mode,
                            f"1px solid {COLORS['border_subtle']}",
                            "1px solid rgba(0, 0, 0, 0.1)",
                        ),
                        "border_radius": "10px",
                        "color": rx.cond(
                            DashboardState.dark_mode,
                            COLORS["text_secondary"],
                            "#475569",
                        ),
                        "cursor": "pointer",
                        "transition": "all 0.2s ease",
                        "margin_bottom": "12px",
                        "_hover": {
                            "background": rx.cond(
                                DashboardState.dark_mode,
                                "rgba(255, 255, 255, 0.1)",
                                "rgba(0, 0, 0, 0.08)",
                            ),
                        },
                    },
                    on_click=DashboardState.toggle_dark_mode,
                ),

                # Auto-refresh toggle
                rx.hstack(
                    rx.cond(
                        ~DashboardState.sidebar_collapsed,
                        rx.hstack(
                            rx.el.div(
                                style={
                                    "width": "6px",
                                    "height": "6px",
                                    "border_radius": "50%",
                                    "background": rx.cond(
                                        DashboardState.auto_refresh,
                                        COLORS["status_online"],
                                        COLORS["status_offline"],
                                    ),
                                }
                            ),
                            rx.text(
                                "Auto-refresh",
                                font_size="0.8rem",
                                color=COLORS["text_secondary"],
                            ),
                            spacing="2",
                            align="center",
                        ),
                        rx.fragment(),
                    ),
                    rx.spacer(),
                    rx.switch(
                        checked=DashboardState.auto_refresh,
                        on_change=DashboardState.toggle_auto_refresh,
                        color_scheme="purple",
                        size="1",
                    ),
                    justify="between",
                    width="100%",
                    padding="8px 4px",
                ),

                # Refresh button
                rx.el.button(
                    rx.hstack(
                        rx.cond(
                            DashboardState.is_loading,
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
                            rx.text("↻", font_size="1rem"),
                        ),
                        rx.cond(
                            ~DashboardState.sidebar_collapsed,
                            rx.text(
                                rx.cond(
                                    DashboardState.is_loading,
                                    "Refreshing...",
                                    "Refresh Data",
                                ),
                                font_size="0.85rem",
                                font_weight="500",
                            ),
                            rx.fragment(),
                        ),
                        spacing="2",
                        justify="center",
                        align="center",
                    ),
                    style={
                        "width": "100%",
                        "padding": "10px 16px",
                        "margin_top": "8px",
                        "background": GRADIENT_PRIMARY,
                        "border": "none",
                        "border_radius": "10px",
                        "color": "white",
                        "cursor": "pointer",
                        "transition": "all 0.2s ease",
                        "_hover": {
                            "opacity": "0.9",
                            "transform": "translateY(-1px)",
                            "box_shadow": f"0 4px 16px {COLORS['primary']}40",
                        },
                        "_disabled": {
                            "opacity": "0.6",
                            "cursor": "not-allowed",
                        },
                    },
                    on_click=DashboardState.refresh_data,
                    disabled=DashboardState.is_loading,
                ),

                # Last refresh time
                rx.cond(
                    ~DashboardState.sidebar_collapsed,
                    rx.cond(
                        DashboardState.last_refresh != "",
                        rx.text(
                            f"Last: {DashboardState.last_refresh}",
                            font_size="0.7rem",
                            color=COLORS["text_dim"],
                            text_align="center",
                            margin_top="6px",
                        ),
                        rx.fragment(),
                    ),
                    rx.fragment(),
                ),

                width="100%",
                padding_top="12px",
                border_top=f"1px solid {COLORS['border_subtle']}",
            ),

            spacing="0",
            width="100%",
            height="100vh",
            position="relative",
            padding="16px 12px",
        ),

        style={
            "width": rx.cond(DashboardState.sidebar_collapsed, "72px", "260px"),
            "min_height": "100vh",
            "background": rx.cond(
                DashboardState.dark_mode,
                "linear-gradient(180deg, rgba(10, 10, 26, 0.96) 0%, rgba(5, 5, 15, 0.98) 100%)",
                "linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.98) 100%)",
            ),
            "border_right": rx.cond(
                DashboardState.dark_mode,
                f"1px solid {COLORS['border_subtle']}",
                "1px solid rgba(0, 0, 0, 0.08)",
            ),
            "position": "fixed",
            "left": "0",
            "top": "0",
            "z_index": "100",
            "backdrop_filter": "blur(20px)",
            "transition": "width 0.3s cubic-bezier(0.4, 0, 0.2, 1), background 0.3s ease",
            "overflow": "hidden",
        }
    )
