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
    """Right side panel with Token Usage and Live Logs."""
    return rx.el.div(
        # Panel header
        rx.hstack(
            rx.hstack(
                rx.text("📊", font_size="1rem"),
                rx.text(
                    "MONITORING",
                    font_size="0.7rem",
                    font_weight="700",
                    letter_spacing="1.5px",
                    color=COLORS["text_muted"],
                ),
                spacing="2",
            ),
            rx.spacer(),
            rx.el.button(
                "✕",
                style={
                    "background": "rgba(255,255,255,0.05)",
                    "border": "none",
                    "border_radius": "6px",
                    "width": "24px",
                    "height": "24px",
                    "cursor": "pointer",
                    "color": COLORS["text_muted"],
                    "font_size": "0.8rem",
                    "_hover": {"background": "rgba(255,255,255,0.1)"},
                },
                on_click=DashboardState.toggle_right_panel,
            ),
            width="100%",
            padding="1rem 1.25rem",
            border_bottom=f"1px solid {COLORS['border_subtle']}",
        ),

        # Scrollable content
        rx.el.div(
            # Token Usage Section
            token_usage_section(),

            # Live Logs Section
            rx.el.div(
                live_logs(),
                margin_top="1.5rem",
            ),

            style={
                "padding": "1.25rem",
                "overflow_y": "auto",
                "flex": "1",
            }
        ),

        style={
            "width": "380px",
            "height": "100vh",
            "background": "linear-gradient(180deg, rgba(12,12,20,0.98) 0%, rgba(8,8,14,0.98) 100%)",
            "border_left": f"1px solid {COLORS['border_subtle']}",
            "backdrop_filter": "blur(30px)",
            "display": "flex",
            "flex_direction": "column",
            "position": "fixed",
            "right": "0",
            "top": "0",
            "z_index": "50",
            "transition": "transform 0.3s ease",
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
    Modern glassmorphism design with office background.
    """
    return rx.el.div(
        # Office header badge
        rx.center(
            rx.el.div(
                rx.hstack(
                    rx.text("🏢", font_size="1rem"),
                    rx.text(
                        "VIRTUAL OFFICE",
                        font_weight="700",
                        letter_spacing="2px",
                        font_size="0.75rem",
                    ),
                    spacing="2",
                ),
                style={
                    "background": f"linear-gradient(135deg, {COLORS['primary']}, {COLORS['primary_dark']})",
                    "color": "white",
                    "padding": "10px 24px",
                    "border_radius": "25px",
                    "box_shadow": f"0 4px 20px {COLORS['primary']}40",
                }
            ),
            margin_bottom="1.5rem",
        ),

        # Workflow pipeline
        rx.center(
            rx.hstack(
                rx.el.span("🦑 Orca", style={"background": AGENT_COLORS["Orca"], "color": "white", "padding": "6px 14px", "border_radius": "12px", "font_weight": "600", "font_size": "0.8rem"}),
                rx.text("→", color=COLORS["primary"], font_weight="bold", font_size="1.2rem"),
                rx.el.span("🎨 Design", style={"background": AGENT_COLORS["Design"], "color": "white", "padding": "6px 14px", "border_radius": "12px", "font_weight": "600", "font_size": "0.8rem"}),
                rx.text("→", color=COLORS["primary"], font_weight="bold", font_size="1.2rem"),
                rx.el.span("💻 Code", style={"background": AGENT_COLORS["Code"], "color": "white", "padding": "6px 14px", "border_radius": "12px", "font_weight": "600", "font_size": "0.8rem"}),
                rx.text("→", color=COLORS["primary"], font_weight="bold", font_size="1.2rem"),
                rx.el.span("🧪 Test", style={"background": AGENT_COLORS["Test"], "color": "white", "padding": "6px 14px", "border_radius": "12px", "font_weight": "600", "font_size": "0.8rem"}),
                rx.text("→", color=COLORS["primary"], font_weight="bold", font_size="1.2rem"),
                rx.el.span("🐙 GitHub", style={"background": AGENT_COLORS["GitHub"], "color": "white", "padding": "6px 14px", "border_radius": "12px", "font_weight": "600", "font_size": "0.8rem"}),
                spacing="2",
                wrap="wrap",
                justify="center",
            ),
            margin_bottom="2rem",
        ),

        # Main office layout
        rx.hstack(
            # LEFT: Management area
            rx.el.div(
                rx.el.div(
                    rx.hstack(
                        rx.text("👔", font_size="0.9rem"),
                        rx.text(
                            "MANAGEMENT",
                            font_size="0.7rem",
                            font_weight="600",
                            letter_spacing="1.5px",
                        ),
                        spacing="2",
                        justify="center",
                    ),
                    style={
                        "color": COLORS["text_muted"],
                        "margin_bottom": "1.25rem",
                        "text_align": "center",
                    }
                ),
                rx.el.div(
                    rx.foreach(
                        DashboardState.agents[:2],  # Orca and Audit
                        agent_card,
                    ),
                    style={
                        "display": "flex",
                        "flex_direction": "column",
                        "gap": "1.25rem",
                        "align_items": "center",
                    }
                ),
                style={
                    "padding": "1.5rem",
                    "background": f"linear-gradient(145deg, {COLORS['primary']}08, transparent)",
                    "border_radius": "24px",
                    "border": f"2px dashed {COLORS['primary']}25",
                }
            ),

            # RIGHT: Worker area (2x2 grid)
            rx.el.div(
                rx.el.div(
                    rx.hstack(
                        rx.text("⚙️", font_size="0.9rem"),
                        rx.text(
                            "WORKERS",
                            font_size="0.7rem",
                            font_weight="600",
                            letter_spacing="1.5px",
                        ),
                        spacing="2",
                        justify="center",
                    ),
                    style={
                        "color": COLORS["text_muted"],
                        "margin_bottom": "1.25rem",
                        "text_align": "center",
                    }
                ),
                rx.el.div(
                    rx.foreach(
                        DashboardState.agents[2:],  # Design, Code, Test, GitHub
                        agent_card,
                    ),
                    style={
                        "display": "grid",
                        "grid_template_columns": "repeat(2, 200px)",
                        "gap": "1.25rem",
                        "justify_content": "center",
                    }
                ),
                style={
                    "flex": "1",
                    "padding": "1.5rem",
                    "background": f"linear-gradient(145deg, {COLORS['accent_cyan']}05, transparent)",
                    "border_radius": "24px",
                    "border": f"2px dashed {COLORS['accent_cyan']}20",
                }
            ),
            spacing="6",
            width="100%",
            align="start",
            wrap="wrap",
        ),

        # Container styles with background
        style={
            "width": "100%",
            "background": f"""
                linear-gradient(135deg, rgba(10,10,15,0.95) 0%, rgba(18,18,28,0.92) 100%),
                url('https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=80')
            """,
            "background_size": "cover",
            "background_position": "center",
            "border_radius": "28px",
            "border": f"1px solid {COLORS['border_subtle']}",
            "box_shadow": "0 20px 60px rgba(0, 0, 0, 0.4)",
            "padding": "2rem",
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
                "background": f"linear-gradient(135deg, {COLORS['bg_dark']} 0%, #12121C 50%, #0A0A14 100%)",
                "padding": "2rem",
                "transition": "margin-left 0.3s ease, margin-right 0.3s ease",
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
            "background": COLORS["bg_dark"],
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
