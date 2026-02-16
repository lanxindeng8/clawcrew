"""
Token Chart Components
Ring chart for usage breakdown + trend line for history.
"""

import reflex as rx
from ..theme import COLORS, AGENT_COLORS
from ..state import DashboardState


def token_ring_chart() -> rx.Component:
    """
    SVG ring chart showing token distribution across agents.
    """
    # Ring dimensions
    size = 180
    stroke_width = 16
    radius = (size - stroke_width) / 2
    circumference = 2 * 3.14159 * radius

    # Calculate percentages for each agent segment
    # We'll create colored segments around the ring

    return rx.el.div(
        # Ring Chart SVG
        rx.el.div(
            rx.el.svg(
                # Background ring
                rx.el.circle(
                    cx=str(size // 2),
                    cy=str(size // 2),
                    r=str(radius),
                    fill="none",
                    stroke="rgba(255, 255, 255, 0.05)",
                    stroke_width=str(stroke_width),
                ),
                # Orca segment (0-28%)
                rx.el.circle(
                    cx=str(size // 2),
                    cy=str(size // 2),
                    r=str(radius),
                    fill="none",
                    stroke=AGENT_COLORS["Orca"],
                    stroke_width=str(stroke_width),
                    stroke_dasharray=f"{circumference * 0.23} {circumference}",
                    stroke_dashoffset="0",
                    stroke_linecap="round",
                    transform=f"rotate(-90 {size // 2} {size // 2})",
                    style={"transition": "stroke-dashoffset 1s ease-out"},
                ),
                # Code segment (28-56%)
                rx.el.circle(
                    cx=str(size // 2),
                    cy=str(size // 2),
                    r=str(radius),
                    fill="none",
                    stroke=AGENT_COLORS["Code"],
                    stroke_width=str(stroke_width),
                    stroke_dasharray=f"{circumference * 0.28} {circumference}",
                    stroke_dashoffset=str(-circumference * 0.23),
                    stroke_linecap="round",
                    transform=f"rotate(-90 {size // 2} {size // 2})",
                ),
                # Design segment (56-77%)
                rx.el.circle(
                    cx=str(size // 2),
                    cy=str(size // 2),
                    r=str(radius),
                    fill="none",
                    stroke=AGENT_COLORS["Design"],
                    stroke_width=str(stroke_width),
                    stroke_dasharray=f"{circumference * 0.21} {circumference}",
                    stroke_dashoffset=str(-circumference * 0.51),
                    stroke_linecap="round",
                    transform=f"rotate(-90 {size // 2} {size // 2})",
                ),
                # Test segment (77-90%)
                rx.el.circle(
                    cx=str(size // 2),
                    cy=str(size // 2),
                    r=str(radius),
                    fill="none",
                    stroke=AGENT_COLORS["Test"],
                    stroke_width=str(stroke_width),
                    stroke_dasharray=f"{circumference * 0.13} {circumference}",
                    stroke_dashoffset=str(-circumference * 0.72),
                    stroke_linecap="round",
                    transform=f"rotate(-90 {size // 2} {size // 2})",
                ),
                # GitHub segment (90-100%)
                rx.el.circle(
                    cx=str(size // 2),
                    cy=str(size // 2),
                    r=str(radius),
                    fill="none",
                    stroke=AGENT_COLORS["GitHub"],
                    stroke_width=str(stroke_width),
                    stroke_dasharray=f"{circumference * 0.10} {circumference}",
                    stroke_dashoffset=str(-circumference * 0.85),
                    stroke_linecap="round",
                    transform=f"rotate(-90 {size // 2} {size // 2})",
                ),
                # Audit segment (remaining)
                rx.el.circle(
                    cx=str(size // 2),
                    cy=str(size // 2),
                    r=str(radius),
                    fill="none",
                    stroke=AGENT_COLORS["Audit"],
                    stroke_width=str(stroke_width),
                    stroke_dasharray=f"{circumference * 0.05} {circumference}",
                    stroke_dashoffset=str(-circumference * 0.95),
                    stroke_linecap="round",
                    transform=f"rotate(-90 {size // 2} {size // 2})",
                ),
                width=str(size),
                height=str(size),
                viewBox=f"0 0 {size} {size}",
            ),
            # Center content
            rx.el.div(
                rx.vstack(
                    rx.text(
                        DashboardState.total_tokens_formatted,
                        font_size="2rem",
                        font_weight="700",
                        color=COLORS["text_primary"],
                        line_height="1",
                    ),
                    rx.text(
                        "Total Tokens",
                        font_size="0.7rem",
                        color=COLORS["text_muted"],
                    ),
                    spacing="1",
                    align="center",
                ),
                style={
                    "position": "absolute",
                    "top": "50%",
                    "left": "50%",
                    "transform": "translate(-50%, -50%)",
                }
            ),
            style={
                "position": "relative",
                "width": f"{size}px",
                "height": f"{size}px",
            }
        ),

        # Legend
        rx.el.div(
            rx.foreach(
                DashboardState.agents,
                lambda agent: rx.hstack(
                    rx.el.div(
                        style={
                            "width": "10px",
                            "height": "10px",
                            "border_radius": "3px",
                            "background": agent.color,
                        }
                    ),
                    rx.text(
                        agent.name,
                        font_size="0.75rem",
                        color=COLORS["text_secondary"],
                    ),
                    rx.text(
                        agent.tokens,
                        font_size="0.75rem",
                        font_weight="600",
                        color=COLORS["text_primary"],
                    ),
                    spacing="2",
                    align="center",
                ),
            ),
            style={
                "display": "grid",
                "grid_template_columns": "repeat(2, 1fr)",
                "gap": "8px",
                "margin_top": "1rem",
            }
        ),

        style={
            "background": "rgba(18, 18, 28, 0.6)",
            "backdrop_filter": "blur(20px)",
            "border_radius": "20px",
            "border": f"1px solid {COLORS['border_subtle']}",
            "padding": "1.5rem",
            "display": "flex",
            "flex_direction": "column",
            "align_items": "center",
        }
    )


def token_trend_chart() -> rx.Component:
    """
    SVG line chart showing token usage over time.
    """
    width = 300
    height = 100
    padding = 20

    # Sample data as path (converted from polyline points)
    line_path = "M 20 80 L 50 65 L 80 70 L 110 55 L 140 60 L 170 45 L 200 50 L 230 35 L 260 40 L 280 30"
    fill_path = "M 20 100 L 20 80 L 50 65 L 80 70 L 110 55 L 140 60 L 170 45 L 200 50 L 230 35 L 260 40 L 280 30 L 280 100 Z"

    return rx.el.div(
        rx.text(
            "Token Trend (Last Hour)",
            font_size="0.8rem",
            color=COLORS["text_muted"],
            margin_bottom="0.75rem",
        ),
        rx.el.svg(
            # Grid lines
            rx.el.line(x1="20", y1="20", x2="280", y2="20", stroke="rgba(255,255,255,0.05)", stroke_width="1"),
            rx.el.line(x1="20", y1="50", x2="280", y2="50", stroke="rgba(255,255,255,0.05)", stroke_width="1"),
            rx.el.line(x1="20", y1="80", x2="280", y2="80", stroke="rgba(255,255,255,0.05)", stroke_width="1"),

            # Fill area (using path instead of polygon)
            rx.el.path(
                d=fill_path,
                fill=f"{COLORS['primary']}30",
            ),

            # Line (using path instead of polyline)
            rx.el.path(
                d=line_path,
                fill="none",
                stroke=COLORS["primary"],
                stroke_width="2.5",
                stroke_linecap="round",
                stroke_linejoin="round",
            ),

            # Data points
            rx.el.circle(cx="280", cy="30", r="4", fill=COLORS["primary"]),
            rx.el.circle(cx="280", cy="30", r="8", fill=f"{COLORS['primary']}40"),

            width=str(width),
            height=str(height),
            viewBox=f"0 0 {width} {height}",
        ),

        # Current session stats
        rx.hstack(
            rx.el.div(
                rx.text("This Task", font_size="0.7rem", color=COLORS["text_muted"]),
                rx.text(
                    "+2,410",
                    font_size="1rem",
                    font_weight="700",
                    color=COLORS["status_working"],
                ),
                text_align="center",
            ),
            rx.el.div(
                style={
                    "width": "1px",
                    "height": "30px",
                    "background": COLORS["border_subtle"],
                }
            ),
            rx.el.div(
                rx.text("Avg/Task", font_size="0.7rem", color=COLORS["text_muted"]),
                rx.text(
                    "1,847",
                    font_size="1rem",
                    font_weight="700",
                    color=COLORS["text_primary"],
                ),
                text_align="center",
            ),
            rx.el.div(
                style={
                    "width": "1px",
                    "height": "30px",
                    "background": COLORS["border_subtle"],
                }
            ),
            rx.el.div(
                rx.text("Budget Left", font_size="0.7rem", color=COLORS["text_muted"]),
                rx.text(
                    "81.6K",
                    font_size="1rem",
                    font_weight="700",
                    color=COLORS["status_online"],
                ),
                text_align="center",
            ),
            justify="around",
            width="100%",
            margin_top="1rem",
            padding_top="1rem",
            border_top=f"1px solid {COLORS['border_subtle']}",
        ),

        style={
            "background": "rgba(18, 18, 28, 0.6)",
            "backdrop_filter": "blur(20px)",
            "border_radius": "20px",
            "border": f"1px solid {COLORS['border_subtle']}",
            "padding": "1.5rem",
        }
    )


def token_usage_section() -> rx.Component:
    """Combined token usage section with ring chart and trend."""
    return rx.el.div(
        rx.text(
            "📊 Token Usage",
            font_size="1.1rem",
            font_weight="600",
            color=COLORS["text_primary"],
            margin_bottom="1rem",
        ),
        rx.hstack(
            token_ring_chart(),
            token_trend_chart(),
            spacing="4",
            width="100%",
            align="start",
            wrap="wrap",
        ),
    )
