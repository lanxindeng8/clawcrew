"""
ClawCrew Dashboard Theme System
Modern glassmorphism + neumorphism design tokens for 2026-style AI Dashboard.
"""

# ============================================================
# COLOR SYSTEM
# ============================================================

# Primary palette
COLORS = {
    # Primary purple gradient
    "primary": "#7B4CFF",
    "primary_light": "#9D7AFF",
    "primary_dark": "#5A2ED9",
    "primary_glow": "rgba(123, 76, 255, 0.4)",

    # Accent colors
    "accent_cyan": "#00D9FF",
    "accent_green": "#10B981",
    "accent_orange": "#F97316",
    "accent_red": "#EF4444",
    "accent_yellow": "#FBBF24",

    # Dark mode backgrounds
    "bg_dark": "#0A0A0F",
    "bg_card": "rgba(18, 18, 28, 0.85)",
    "bg_card_hover": "rgba(28, 28, 42, 0.9)",
    "bg_elevated": "rgba(30, 30, 48, 0.95)",
    "bg_glass": "rgba(255, 255, 255, 0.03)",

    # Light mode backgrounds
    "bg_light": "#F8FAFC",
    "bg_card_light": "rgba(255, 255, 255, 0.85)",
    "bg_elevated_light": "rgba(255, 255, 255, 0.95)",

    # Text colors
    "text_primary": "#FFFFFF",
    "text_secondary": "rgba(255, 255, 255, 0.7)",
    "text_muted": "rgba(255, 255, 255, 0.4)",
    "text_dark": "#1E293B",
    "text_dark_secondary": "#64748B",

    # Borders
    "border_subtle": "rgba(255, 255, 255, 0.08)",
    "border_light": "rgba(255, 255, 255, 0.12)",
    "border_glow": "rgba(123, 76, 255, 0.3)",

    # Status colors
    "status_online": "#22C55E",
    "status_working": "#F97316",
    "status_away": "#FBBF24",
    "status_offline": "#6B7280",
    "status_error": "#EF4444",
}

# Agent-specific colors
AGENT_COLORS = {
    "Orca": "#7B4CFF",
    "Audit": "#EF4444",
    "Design": "#A855F7",
    "Code": "#3B82F6",
    "Test": "#10B981",
    "GitHub": "#6366F1",
}

# ============================================================
# GLASSMORPHISM STYLES
# ============================================================

GLASS_CARD = {
    "background": "rgba(18, 18, 28, 0.75)",
    "backdrop_filter": "blur(20px) saturate(180%)",
    "-webkit-backdrop-filter": "blur(20px) saturate(180%)",
    "border": "1px solid rgba(255, 255, 255, 0.08)",
    "border_radius": "20px",
    "box_shadow": """
        0 8px 32px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.05)
    """,
}

GLASS_CARD_HOVER = {
    **GLASS_CARD,
    "background": "rgba(28, 28, 42, 0.85)",
    "border": f"1px solid {COLORS['border_glow']}",
    "box_shadow": f"""
        0 12px 40px rgba(0, 0, 0, 0.5),
        0 0 30px {COLORS['primary_glow']},
        inset 0 1px 0 rgba(255, 255, 255, 0.08)
    """,
    "transform": "translateY(-4px) scale(1.02)",
}

GLASS_PANEL = {
    "background": "rgba(12, 12, 20, 0.9)",
    "backdrop_filter": "blur(30px) saturate(200%)",
    "border": "1px solid rgba(255, 255, 255, 0.06)",
    "border_radius": "24px",
}

GLASS_INPUT = {
    "background": "rgba(255, 255, 255, 0.05)",
    "border": "1px solid rgba(255, 255, 255, 0.1)",
    "border_radius": "12px",
    "color": COLORS["text_primary"],
    "padding": "12px 16px",
    "transition": "all 0.3s ease",
}

# ============================================================
# NEUMORPHISM ACCENTS
# ============================================================

NEUMORPHIC_BUTTON = {
    "background": "linear-gradient(145deg, rgba(30,30,48,1), rgba(20,20,32,1))",
    "box_shadow": """
        6px 6px 12px rgba(0, 0, 0, 0.4),
        -6px -6px 12px rgba(60, 60, 80, 0.1)
    """,
    "border": "1px solid rgba(255, 255, 255, 0.05)",
    "border_radius": "14px",
}

NEUMORPHIC_INSET = {
    "background": "rgba(10, 10, 18, 0.8)",
    "box_shadow": """
        inset 4px 4px 8px rgba(0, 0, 0, 0.5),
        inset -4px -4px 8px rgba(60, 60, 80, 0.05)
    """,
    "border_radius": "12px",
}

# ============================================================
# ANIMATIONS (CSS keyframes)
# ============================================================

ANIMATIONS_CSS = """
/* Pulse glow for working status */
@keyframes pulse-glow {
    0%, 100% {
        box-shadow: 0 0 10px rgba(249, 115, 22, 0.4);
        transform: scale(1);
    }
    50% {
        box-shadow: 0 0 25px rgba(249, 115, 22, 0.7);
        transform: scale(1.1);
    }
}

/* Subtle float animation */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-6px); }
}

/* Gradient border animation */
@keyframes gradient-rotate {
    0% { --angle: 0deg; }
    100% { --angle: 360deg; }
}

/* Shimmer loading effect */
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* Fade in up */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Ring chart fill animation */
@keyframes ring-fill {
    from { stroke-dashoffset: 283; }
}

/* Status dot pulse */
@keyframes status-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Card hover glow */
.agent-card {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.agent-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow:
        0 20px 50px rgba(0, 0, 0, 0.5),
        0 0 40px rgba(123, 76, 255, 0.3);
}

/* Skeleton loading */
.skeleton {
    background: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0.03) 0%,
        rgba(255, 255, 255, 0.08) 50%,
        rgba(255, 255, 255, 0.03) 100%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 8px;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb {
    background: rgba(123, 76, 255, 0.4);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(123, 76, 255, 0.6);
}

/* Drawer animation */
.drawer-content {
    animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Ring chart */
.ring-chart circle {
    transition: stroke-dashoffset 1s ease-out;
}

/* Stepper connector animation */
.stepper-connector {
    transition: background 0.5s ease;
}

/* Log entry animation */
.log-entry {
    animation: fadeInUp 0.3s ease-out;
}
"""

# ============================================================
# COMPONENT STYLE PRESETS
# ============================================================

SIDEBAR_STYLE = {
    "width": "280px",
    "min_height": "100vh",
    "background": "linear-gradient(180deg, rgba(12,12,20,0.98) 0%, rgba(8,8,14,0.98) 100%)",
    "border_right": "1px solid rgba(255, 255, 255, 0.06)",
    "padding": "1.5rem 1rem",
    "position": "fixed",
    "left": "0",
    "top": "0",
    "z_index": "100",
    "backdrop_filter": "blur(20px)",
}

MAIN_CONTENT_STYLE = {
    "margin_left": "280px",
    "min_height": "100vh",
    "background": f"linear-gradient(135deg, {COLORS['bg_dark']} 0%, #12121C 50%, #0A0A14 100%)",
    "padding": "2rem",
    "width": "calc(100% - 280px)",
}

STAT_CARD_STYLE = {
    **GLASS_CARD,
    "padding": "1.25rem",
    "min_width": "180px",
}

BADGE_STYLE = {
    "padding": "4px 12px",
    "border_radius": "20px",
    "font_size": "0.75rem",
    "font_weight": "600",
    "display": "inline-flex",
    "align_items": "center",
    "gap": "6px",
}

# Status badge variants
def get_status_badge_style(status: str) -> dict:
    """Get status-specific badge styling."""
    base = {**BADGE_STYLE}
    status_styles = {
        "online": {
            "background": "rgba(34, 197, 94, 0.15)",
            "color": COLORS["status_online"],
            "border": f"1px solid {COLORS['status_online']}40",
        },
        "working": {
            "background": "rgba(249, 115, 22, 0.15)",
            "color": COLORS["status_working"],
            "border": f"1px solid {COLORS['status_working']}40",
            "animation": "status-pulse 1.5s infinite",
        },
        "away": {
            "background": "rgba(251, 191, 36, 0.15)",
            "color": COLORS["status_away"],
            "border": f"1px solid {COLORS['status_away']}40",
        },
        "offline": {
            "background": "rgba(107, 114, 128, 0.15)",
            "color": COLORS["status_offline"],
            "border": f"1px solid {COLORS['status_offline']}40",
        },
        "error": {
            "background": "rgba(239, 68, 68, 0.15)",
            "color": COLORS["status_error"],
            "border": f"1px solid {COLORS['status_error']}40",
        },
    }
    base.update(status_styles.get(status, status_styles["offline"]))
    return base
