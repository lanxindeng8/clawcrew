"""
ClawCrew Dashboard - Reflex Implementation
2026-style AI Agent monitoring dashboard with glassmorphism design.
Three-column professional layout.
"""

import reflex as rx

from .theme import COLORS, ANIMATIONS_CSS, AGENT_COLORS
from .state import DashboardState
from .components.agent_card import agent_card
from .components.agent_drawer import agent_drawer
from .components.sidebar import sidebar
from .components.token_chart import token_usage_section
from .components.task_stepper import task_stepper
from .components.live_logs import live_logs
from .components.common import stat_card, task_input_bar, top_stats_bar


# ============================================================
# RIGHT PANEL: Token Usage + Live Logs (collapsible)
# ============================================================

def right_panel_toggle() -> rx.Component:
    """Toggle button for right panel collapse/expand."""
    return rx.el.button(
        rx.cond(
            DashboardState.right_panel_collapsed,
            rx.text("◀", font_size="0.8rem"),
            rx.text("▶", font_size="0.8rem"),
        ),
        style={
            "position": "fixed",
            "right": rx.cond(DashboardState.right_panel_collapsed, "10px", "390px"),
            "top": "50%",
            "transform": "translateY(-50%)",
            "z_index": "100",
            "width": "28px",
            "height": "48px",
            "background": f"linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_dark']})",
            "border": "none",
            "border_radius": "8px 0 0 8px",
            "color": "white",
            "cursor": "pointer",
            "box_shadow": f"0 4px 12px {COLORS['primary']}40",
            "transition": "right 0.3s ease",
            "_hover": {
                "opacity": "0.9",
            }
        },
        on_click=DashboardState.toggle_right_panel,
    )


def right_panel() -> rx.Component:
    """Right side panel with Token Usage and Live Logs - modern Linear/Vercel style."""
    return rx.el.div(
        # Panel header with glassmorphism
        rx.el.div(
            rx.hstack(
                rx.el.div(
                    rx.hstack(
                        rx.el.div(
                            "📊",
                            style={
                                "width": "32px",
                                "height": "32px",
                                "display": "flex",
                                "align_items": "center",
                                "justify_content": "center",
                                "background": f"linear-gradient(135deg, {COLORS['primary']}25, {COLORS['secondary']}15)",
                                "border_radius": "10px",
                                "font_size": "0.95rem",
                            }
                        ),
                        rx.vstack(
                            rx.text(
                                "Monitoring",
                                font_size="1rem",
                                font_weight="600",
                                color=rx.cond(
                                    DashboardState.dark_mode,
                                    COLORS["text_primary"],
                                    "#1e293b",
                                ),
                            ),
                            rx.text(
                                "Real-time insights",
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
                ),
                rx.spacer(),
                rx.el.button(
                    "✕",
                    style={
                        "background": rx.cond(
                            DashboardState.dark_mode,
                            "rgba(255,255,255,0.05)",
                            "rgba(0,0,0,0.05)",
                        ),
                        "border": "none",
                        "border_radius": "8px",
                        "width": "28px",
                        "height": "28px",
                        "cursor": "pointer",
                        "color": rx.cond(
                            DashboardState.dark_mode,
                            COLORS["text_muted"],
                            "#64748b",
                        ),
                        "font_size": "0.85rem",
                        "transition": "all 0.2s ease",
                        "_hover": {
                            "background": rx.cond(
                                DashboardState.dark_mode,
                                "rgba(255,255,255,0.1)",
                                "rgba(0,0,0,0.1)",
                            ),
                            "color": rx.cond(
                                DashboardState.dark_mode,
                                COLORS["text_primary"],
                                "#1e293b",
                            ),
                        },
                    },
                    on_click=DashboardState.toggle_right_panel,
                ),
                width="100%",
            ),
            style={
                "padding": "1rem 1.25rem",
                "border_bottom": rx.cond(
                    DashboardState.dark_mode,
                    f"1px solid {COLORS['border_subtle']}",
                    "1px solid #e2e8f0",
                ),
                "background": rx.cond(
                    DashboardState.dark_mode,
                    "rgba(255, 255, 255, 0.02)",
                    "rgba(255, 255, 255, 0.8)",
                ),
            }
        ),

        # Scrollable content
        rx.el.div(
            # Token Usage Section
            token_usage_section(),

            # Divider
            rx.el.div(
                style={
                    "height": "1px",
                    "width": "100%",
                    "background": rx.cond(
                        DashboardState.dark_mode,
                        f"linear-gradient(90deg, transparent, {COLORS['border_subtle']}, transparent)",
                        "linear-gradient(90deg, transparent, #e2e8f0, transparent)",
                    ),
                    "margin": "1.5rem 0",
                }
            ),

            # Live Logs Section
            live_logs(),

            style={
                "padding": "1.25rem",
                "overflow_y": "auto",
                "flex": "1",
            }
        ),

        style={
            "width": "380px",
            "height": "100vh",
            "background": rx.cond(
                DashboardState.dark_mode,
                "linear-gradient(180deg, rgba(10,10,22,0.98) 0%, rgba(6,6,14,0.99) 100%)",
                "#f8fafc",
            ),
            "border_left": rx.cond(
                DashboardState.dark_mode,
                f"1px solid {COLORS['border_subtle']}",
                "1px solid #e2e8f0",
            ),
            "backdrop_filter": "blur(30px)",
            "display": "flex",
            "flex_direction": "column",
            "position": "fixed",
            "right": "0",
            "top": "0",
            "z_index": "50",
            "transition": "transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), background 0.3s ease",
            "transform": rx.cond(
                DashboardState.right_panel_collapsed,
                "translateX(100%)",
                "translateX(0)",
            ),
        }
    )


# ============================================================
# VIRTUAL OFFICE: Main agents area
# ============================================================

def virtual_office() -> rx.Component:
    """
    Virtual Office with management and workers sections.
    Modern Linear/Vercel-style glassmorphism design.
    """
    return rx.el.div(
        # Header section
        rx.hstack(
            rx.hstack(
                rx.el.div(
                    "🏢",
                    style={
                        "width": "40px",
                        "height": "40px",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "background": f"linear-gradient(135deg, {COLORS['primary']}30, {COLORS['secondary']}20)",
                        "border_radius": "12px",
                        "font_size": "1.2rem",
                    }
                ),
                rx.vstack(
                    rx.text(
                        "Virtual Office",
                        font_size="1.15rem",
                        font_weight="600",
                        color=rx.cond(
                            DashboardState.dark_mode,
                            COLORS["text_primary"],
                            "#1e293b",
                        ),
                    ),
                    rx.text(
                        "Agent workspace overview",
                        font_size="0.7rem",
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
            rx.spacer(),
            # Active agent count badge
            rx.el.div(
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
                        f"{DashboardState.active_agents_count} Active",
                        font_size="0.8rem",
                        font_weight="500",
                        color=COLORS["status_online"],
                    ),
                    spacing="2",
                    align="center",
                ),
                style={
                    "padding": "6px 14px",
                    "background": f"{COLORS['status_online']}15",
                    "border_radius": "20px",
                    "border": f"1px solid {COLORS['status_online']}30",
                }
            ),
            width="100%",
            margin_bottom="1.5rem",
        ),

        # Workflow pipeline (compact)
        rx.el.div(
            rx.hstack(
                rx.el.span("🦑 Orca", style={"background": f"{AGENT_COLORS['Orca']}20", "color": AGENT_COLORS["Orca"], "padding": "5px 12px", "border_radius": "10px", "font_weight": "600", "font_size": "0.75rem", "border": f"1px solid {AGENT_COLORS['Orca']}40"}),
                rx.text("→", color=COLORS["text_dim"], font_size="0.9rem"),
                rx.el.span("🎨 Design", style={"background": f"{AGENT_COLORS['Design']}20", "color": AGENT_COLORS["Design"], "padding": "5px 12px", "border_radius": "10px", "font_weight": "600", "font_size": "0.75rem", "border": f"1px solid {AGENT_COLORS['Design']}40"}),
                rx.text("→", color=COLORS["text_dim"], font_size="0.9rem"),
                rx.el.span("💻 Code", style={"background": f"{AGENT_COLORS['Code']}20", "color": AGENT_COLORS["Code"], "padding": "5px 12px", "border_radius": "10px", "font_weight": "600", "font_size": "0.75rem", "border": f"1px solid {AGENT_COLORS['Code']}40"}),
                rx.text("→", color=COLORS["text_dim"], font_size="0.9rem"),
                rx.el.span("🧪 Test", style={"background": f"{AGENT_COLORS['Test']}20", "color": AGENT_COLORS["Test"], "padding": "5px 12px", "border_radius": "10px", "font_weight": "600", "font_size": "0.75rem", "border": f"1px solid {AGENT_COLORS['Test']}40"}),
                rx.text("→", color=COLORS["text_dim"], font_size="0.9rem"),
                rx.el.span("🐙 GitHub", style={"background": f"{AGENT_COLORS['GitHub']}20", "color": AGENT_COLORS["GitHub"], "padding": "5px 12px", "border_radius": "10px", "font_weight": "600", "font_size": "0.75rem", "border": f"1px solid {AGENT_COLORS['GitHub']}40"}),
                spacing="2",
                wrap="wrap",
                justify="center",
            ),
            style={
                "padding": "1rem",
                "background": rx.cond(
                    DashboardState.dark_mode,
                    "rgba(255, 255, 255, 0.02)",
                    "rgba(0, 0, 0, 0.02)",
                ),
                "border_radius": "14px",
                "margin_bottom": "1.5rem",
            }
        ),

        # Two-column layout: Management | Team
        rx.hstack(
            # LEFT: Management section (Orca, Audit)
            rx.el.div(
                # Section header
                rx.hstack(
                    rx.text("👔", font_size="0.9rem"),
                    rx.text(
                        "MANAGEMENT",
                        font_size="0.7rem",
                        font_weight="600",
                        letter_spacing="1.5px",
                        color=rx.cond(
                            DashboardState.dark_mode,
                            COLORS["text_muted"],
                            "#64748b",
                        ),
                    ),
                    spacing="2",
                    margin_bottom="1rem",
                ),
                # Agent cards (Orca, Audit - first 2)
                rx.el.div(
                    rx.foreach(
                        DashboardState.agents[:2],
                        agent_card,
                    ),
                    style={
                        "display": "flex",
                        "flex_direction": "column",
                        "gap": "1rem",
                    }
                ),
                style={
                    "flex": "1",
                    "min_width": "280px",
                    "padding": "1.25rem",
                    "background": rx.cond(
                        DashboardState.dark_mode,
                        f"linear-gradient(145deg, {COLORS['primary']}08, transparent)",
                        f"linear-gradient(145deg, {COLORS['primary']}05, transparent)",
                    ),
                    "border_radius": "20px",
                    "border": rx.cond(
                        DashboardState.dark_mode,
                        f"1px dashed {COLORS['primary']}25",
                        "1px dashed #e2e8f0",
                    ),
                }
            ),

            # RIGHT: Team section (Design, Code, Test, GitHub)
            rx.el.div(
                # Section header
                rx.hstack(
                    rx.text("⚙️", font_size="0.9rem"),
                    rx.text(
                        "TEAM",
                        font_size="0.7rem",
                        font_weight="600",
                        letter_spacing="1.5px",
                        color=rx.cond(
                            DashboardState.dark_mode,
                            COLORS["text_muted"],
                            "#64748b",
                        ),
                    ),
                    spacing="2",
                    margin_bottom="1rem",
                ),
                # Agent cards (Design, Code, Test, GitHub - last 4)
                rx.el.div(
                    rx.foreach(
                        DashboardState.agents[2:],
                        agent_card,
                    ),
                    style={
                        "display": "grid",
                        "grid_template_columns": "repeat(2, 1fr)",
                        "gap": "1rem",
                    }
                ),
                style={
                    "flex": "2",
                    "padding": "1.25rem",
                    "background": rx.cond(
                        DashboardState.dark_mode,
                        f"linear-gradient(145deg, {COLORS['accent_cyan']}05, transparent)",
                        f"linear-gradient(145deg, {COLORS['accent_cyan']}03, transparent)",
                    ),
                    "border_radius": "20px",
                    "border": rx.cond(
                        DashboardState.dark_mode,
                        f"1px dashed {COLORS['accent_cyan']}20",
                        "1px dashed #e2e8f0",
                    ),
                }
            ),
            spacing="5",
            width="100%",
            align="start",
        ),

        # Container styles
        style={
            "width": "100%",
            "background": rx.cond(
                DashboardState.dark_mode,
                "rgba(15, 15, 28, 0.7)",
                "white",
            ),
            "backdrop_filter": "blur(24px)",
            "border_radius": "24px",
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
            "padding": "1.5rem",
        }
    )


# ============================================================
# HOME PAGE
# ============================================================

def home_page() -> rx.Component:
    """Main home page with all dashboard sections (center column content)."""
    return rx.vstack(
        # Task input bar
        task_input_bar(),

        # Top stats bar
        top_stats_bar(),

        # Virtual Office
        rx.el.div(
            virtual_office(),
            margin_top="1.5rem",
        ),

        # Task Pipeline Stepper
        rx.el.div(
            task_stepper(),
            margin_top="1.5rem",
            width="100%",
        ),

        spacing="0",
        width="100%",
        padding="0",
    )


# ============================================================
# OTHER PAGES (Placeholder)
# ============================================================

def other_page() -> rx.Component:
    """Placeholder for other pages."""
    return rx.center(
        rx.vstack(
            rx.el.div(
                "🚧",
                style={
                    "font_size": "4rem",
                    "margin_bottom": "1rem",
                }
            ),
            rx.text(
                DashboardState.current_page.to(str).upper(),
                font_size="1.5rem",
                font_weight="700",
                color=COLORS["text_primary"],
            ),
            rx.text(
                "Page coming soon...",
                font_size="1rem",
                color=COLORS["text_muted"],
            ),
            spacing="2",
            align="center",
        ),
        style={
            "height": "400px",
            "background": "rgba(18, 18, 28, 0.6)",
            "border_radius": "24px",
            "border": f"1px solid {COLORS['border_subtle']}",
        }
    )


# ============================================================
# MAIN APP LAYOUT
# ============================================================

def index() -> rx.Component:
    """Main app layout with three-column design: sidebar, content, right panel."""
    return rx.el.div(
        # Left: Sidebar (fixed)
        sidebar(),

        # Center: Main content area
        rx.el.main(
            rx.cond(
                DashboardState.current_page == "home",
                home_page(),
                other_page(),
            ),
            style={
                # Adjust margins based on sidebar and right panel state
                "margin_left": rx.cond(DashboardState.sidebar_collapsed, "80px", "280px"),
                "margin_right": rx.cond(DashboardState.right_panel_collapsed, "0px", "380px"),
                "min_height": "100vh",
                "background": rx.cond(
                    DashboardState.dark_mode,
                    f"linear-gradient(135deg, {COLORS['bg_dark']} 0%, #12121C 50%, #0A0A14 100%)",
                    "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%)",
                ),
                "padding": "2rem",
                "transition": "margin-left 0.3s ease, margin-right 0.3s ease, background 0.3s ease",
            }
        ),

        # Right: Monitoring panel (Token Usage + Live Logs)
        right_panel(),

        # Right panel toggle button
        right_panel_toggle(),

        # Agent detail drawer
        agent_drawer(),

        # Global styles container
        style={
            "min_height": "100vh",
            "background": rx.cond(
                DashboardState.dark_mode,
                COLORS["bg_dark"],
                "#f8fafc",
            ),
            "transition": "background 0.3s ease",
        }
    )


# ============================================================
# APP CONFIGURATION
# ============================================================

# Custom CSS including animations
custom_style = f"""
{ANIMATIONS_CSS}

@keyframes spin {{
    from {{ transform: rotate(0deg); }}
    to {{ transform: rotate(360deg); }}
}}

* {{
    box-sizing: border-box;
}}

body {{
    background: {COLORS['bg_dark']};
    color: {COLORS['text_primary']};
}}

::selection {{
    background: {COLORS['primary']}40;
    color: white;
}}
"""

def layout() -> rx.Component:
    """Root layout with global styles."""
    return rx.fragment(
        rx.el.style(custom_style),
        index(),
    )


app = rx.App(
    style={
        "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "background": COLORS["bg_dark"],
        "color": COLORS["text_primary"],
    },
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
    ],
)

app.add_page(layout, route="/", title="ClawCrew Dashboard", description="AI Agent Monitoring Dashboard")
