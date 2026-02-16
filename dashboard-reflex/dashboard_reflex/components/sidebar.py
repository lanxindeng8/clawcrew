"""
Sidebar Component
Responsive navigation sidebar with collapse support.
"""

import reflex as rx
from ..theme import COLORS
from ..state import DashboardState


def nav_item(icon: str, label: str, page: str) -> rx.Component:
    """Navigation menu item."""
    is_active = DashboardState.current_page == page

    return rx.el.button(
        rx.hstack(
            rx.text(icon, font_size="1.1rem"),
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
        ),
        style={
            "width": "100%",
            "padding": "0.875rem 1rem",
            "border_radius": "12px",
            "background": rx.cond(
                is_active,
                f"linear-gradient(135deg, {COLORS['primary']}30, {COLORS['primary']}10)",
                "transparent",
            ),
            "border": rx.cond(
                is_active,
                f"1px solid {COLORS['primary']}40",
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
                    f"linear-gradient(135deg, {COLORS['primary']}35, {COLORS['primary']}15)",
                    "rgba(255, 255, 255, 0.05)",
                ),
            },
        },
        on_click=lambda: DashboardState.navigate(page),
    )


def agent_list_item(agent) -> rx.Component:
    """Compact agent status in sidebar."""
    status_color = rx.match(
        agent.status,
        ("online", COLORS["status_online"]),
        ("working", COLORS["status_working"]),
        ("away", COLORS["status_away"]),
        ("error", COLORS["status_error"]),
        COLORS["status_offline"],
    )

    return rx.hstack(
        rx.text(agent.emoji, font_size="1rem"),
        rx.cond(
            ~DashboardState.sidebar_collapsed,
            rx.fragment(
                rx.vstack(
                    rx.text(
                        agent.name,
                        font_size="0.8rem",
                        font_weight="500",
                        color=COLORS["text_primary"],
                    ),
                    rx.text(
                        agent.role,
                        font_size="0.65rem",
                        color=COLORS["text_muted"],
                    ),
                    spacing="0",
                    align="start",
                    flex="1",
                ),
                rx.el.div(
                    style={
                        "width": "8px",
                        "height": "8px",
                        "border_radius": "50%",
                        "background": status_color,
                        "box_shadow": rx.cond(
                            agent.status == "working",
                            f"0 0 8px {COLORS['status_working']}",
                            "none",
                        ),
                    }
                ),
            ),
            rx.fragment(),
        ),
        spacing="2",
        width="100%",
        padding="0.5rem 0.75rem",
        border_radius="8px",
        cursor="pointer",
        _hover={"background": "rgba(255, 255, 255, 0.03)"},
        on_click=lambda: DashboardState.open_agent_drawer(agent.id),
    )


def sidebar() -> rx.Component:
    """
    Responsive sidebar with navigation and agent list.
    """
    return rx.el.aside(
        rx.vstack(
            # Logo section
            rx.hstack(
                rx.el.div(
                    "🦞",
                    style={
                        "font_size": "2rem",
                        "width": "48px",
                        "height": "48px",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "background": f"linear-gradient(135deg, {COLORS['primary']}30, {COLORS['primary']}10)",
                        "border_radius": "14px",
                        "border": f"1px solid {COLORS['primary']}30",
                    }
                ),
                rx.cond(
                    ~DashboardState.sidebar_collapsed,
                    rx.vstack(
                        rx.text(
                            "ClawCrew",
                            font_size="1.2rem",
                            font_weight="700",
                            color=COLORS["text_primary"],
                            letter_spacing="0.5px",
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
                padding="0.5rem",
                margin_bottom="1rem",
            ),

            # Collapse button
            rx.el.button(
                rx.cond(
                    DashboardState.sidebar_collapsed,
                    rx.text("→", font_size="1rem"),
                    rx.text("←", font_size="1rem"),
                ),
                style={
                    "position": "absolute",
                    "right": "-12px",
                    "top": "70px",
                    "width": "24px",
                    "height": "24px",
                    "border_radius": "50%",
                    "background": COLORS["bg_dark"],
                    "border": f"1px solid {COLORS['border_subtle']}",
                    "color": COLORS["text_secondary"],
                    "cursor": "pointer",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "z_index": "10",
                    "_hover": {
                        "background": COLORS["primary"],
                        "color": "white",
                    },
                },
                on_click=DashboardState.toggle_sidebar,
            ),

            # Navigation
            rx.el.div(
                rx.cond(
                    ~DashboardState.sidebar_collapsed,
                    rx.text(
                        "NAVIGATION",
                        font_size="0.65rem",
                        font_weight="600",
                        color=COLORS["text_muted"],
                        letter_spacing="1px",
                        margin_bottom="0.5rem",
                        padding_left="0.5rem",
                    ),
                    rx.fragment(),
                ),
                rx.vstack(
                    nav_item("🏠", "Home", "home"),
                    nav_item("🤖", "Agents", "agents"),
                    nav_item("📁", "Artifacts", "artifacts"),
                    nav_item("📋", "Logs", "logs"),
                    nav_item("⚙️", "Settings", "settings"),
                    spacing="1",
                    width="100%",
                ),
                width="100%",
                margin_bottom="1.5rem",
            ),

            rx.el.div(
                style={
                    "height": "1px",
                    "width": "100%",
                    "background": COLORS["border_subtle"],
                    "margin": "0.5rem 0",
                }
            ),

            # Agents section
            rx.el.div(
                rx.cond(
                    ~DashboardState.sidebar_collapsed,
                    rx.text(
                        "AGENTS",
                        font_size="0.65rem",
                        font_weight="600",
                        color=COLORS["text_muted"],
                        letter_spacing="1px",
                        margin_bottom="0.5rem",
                        padding_left="0.5rem",
                    ),
                    rx.fragment(),
                ),
                rx.vstack(
                    rx.foreach(
                        DashboardState.agents,
                        agent_list_item,
                    ),
                    spacing="1",
                    width="100%",
                ),
                width="100%",
                flex="1",
                overflow_y="auto",
            ),

            rx.spacer(),

            # Footer controls
            rx.el.div(
                rx.hstack(
                    rx.cond(
                        ~DashboardState.sidebar_collapsed,
                        rx.text(
                            "Auto-refresh",
                            font_size="0.8rem",
                            color=COLORS["text_secondary"],
                        ),
                        rx.fragment(),
                    ),
                    rx.switch(
                        checked=DashboardState.auto_refresh,
                        on_change=DashboardState.toggle_auto_refresh,
                        color_scheme="purple",
                    ),
                    justify="between",
                    width="100%",
                ),
                rx.el.button(
                    rx.hstack(
                        rx.text("🔄", font_size="0.9rem"),
                        rx.cond(
                            ~DashboardState.sidebar_collapsed,
                            rx.text("Refresh Now", font_size="0.85rem"),
                            rx.fragment(),
                        ),
                        spacing="2",
                        justify="center",
                    ),
                    style={
                        "width": "100%",
                        "padding": "0.75rem",
                        "margin_top": "0.75rem",
                        "background": f"linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_dark']})",
                        "border": "none",
                        "border_radius": "12px",
                        "color": "white",
                        "cursor": "pointer",
                        "font_weight": "500",
                        "_hover": {
                            "opacity": "0.9",
                        },
                    },
                    on_click=DashboardState.refresh_data,
                ),
                width="100%",
                padding="1rem 0",
                border_top=f"1px solid {COLORS['border_subtle']}",
            ),

            spacing="0",
            width="100%",
            height="100vh",
            position="relative",
        ),

        style={
            "width": rx.cond(DashboardState.sidebar_collapsed, "80px", "280px"),
            "min_height": "100vh",
            "background": "linear-gradient(180deg, rgba(12,12,20,0.98) 0%, rgba(8,8,14,0.98) 100%)",
            "border_right": f"1px solid {COLORS['border_subtle']}",
            "padding": "1rem",
            "position": "fixed",
            "left": "0",
            "top": "0",
            "z_index": "100",
            "backdrop_filter": "blur(20px)",
            "transition": "width 0.3s ease",
        }
    )
