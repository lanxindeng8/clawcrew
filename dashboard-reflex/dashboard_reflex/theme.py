"""
ClawCrew Dashboard Theme
Modern dark theme inspired by Linear.app and Vercel Dashboard.
"""

# ============================================================
# COLOR SYSTEM
# ============================================================

COLORS = {
    # Backgrounds - Rich dark navy instead of pure black
    "bg_dark": "#0a0a1a",
    "bg_darker": "#050510",
    "bg_card": "rgba(15, 15, 30, 0.7)",
    "bg_card_hover": "rgba(22, 22, 42, 0.85)",
    "bg_elevated": "rgba(25, 25, 45, 0.95)",
    "bg_input": "rgba(255, 255, 255, 0.04)",
    "bg_input_focus": "rgba(255, 255, 255, 0.08)",
    "bg_overlay": "rgba(0, 0, 0, 0.6)",

    # Borders - Subtle glass-morphism borders
    "border_subtle": "rgba(255, 255, 255, 0.06)",
    "border_muted": "rgba(255, 255, 255, 0.1)",
    "border_accent": "rgba(124, 58, 237, 0.3)",
    "border_focus": "rgba(124, 58, 237, 0.5)",

    # Primary Accent - Purple to Blue gradient
    "primary": "#7c3aed",
    "primary_light": "#8b5cf6",
    "primary_dark": "#6d28d9",
    "secondary": "#3b82f6",
    "primary_glow": "rgba(124, 58, 237, 0.4)",

    # Text
    "text_primary": "#ffffff",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "text_dim": "#475569",

    # Status Colors
    "status_online": "#22c55e",
    "status_working": "#f59e0b",
    "status_away": "#6b7280",
    "status_error": "#ef4444",
    "status_offline": "#374151",

    # Semantic
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",

    # Accent colors
    "accent_cyan": "#06b6d4",
    "accent_pink": "#ec4899",
    "accent_orange": "#f97316",
}

# Agent signature colors
AGENT_COLORS = {
    "Orca": "#7c3aed",      # Purple
    "Design": "#ec4899",     # Pink
    "Code": "#3b82f6",       # Blue
    "Test": "#22c55e",       # Green
    "GitHub": "#f97316",     # Orange
    "Repo": "#f97316",       # Orange (alias)
    "Audit": "#ef4444",      # Red
    "Main": "#ef4444",       # Red (alias)
}

# ============================================================
# LIGHT MODE COLORS
# ============================================================

COLORS_LIGHT = {
    # Backgrounds - Clean white/gray
    "bg_dark": "#f8fafc",
    "bg_darker": "#f1f5f9",
    "bg_card": "rgba(255, 255, 255, 0.9)",
    "bg_card_hover": "rgba(255, 255, 255, 0.95)",
    "bg_elevated": "rgba(255, 255, 255, 0.98)",
    "bg_input": "rgba(0, 0, 0, 0.03)",
    "bg_input_focus": "rgba(0, 0, 0, 0.05)",
    "bg_overlay": "rgba(0, 0, 0, 0.4)",

    # Borders
    "border_subtle": "rgba(0, 0, 0, 0.08)",
    "border_muted": "rgba(0, 0, 0, 0.12)",
    "border_accent": "rgba(124, 58, 237, 0.3)",
    "border_focus": "rgba(124, 58, 237, 0.5)",

    # Primary Accent (same)
    "primary": "#7c3aed",
    "primary_light": "#8b5cf6",
    "primary_dark": "#6d28d9",
    "secondary": "#3b82f6",
    "primary_glow": "rgba(124, 58, 237, 0.2)",

    # Text
    "text_primary": "#0f172a",
    "text_secondary": "#475569",
    "text_muted": "#64748b",
    "text_dim": "#94a3b8",

    # Status Colors (same)
    "status_online": "#22c55e",
    "status_working": "#f59e0b",
    "status_away": "#6b7280",
    "status_error": "#ef4444",
    "status_offline": "#9ca3af",

    # Semantic (same)
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",

    # Accent colors (same)
    "accent_cyan": "#06b6d4",
    "accent_pink": "#ec4899",
    "accent_orange": "#f97316",
}

# ============================================================
# GLASSMORPHISM PRESETS
# ============================================================

GLASS_CARD = {
    "background": "rgba(15, 15, 30, 0.6)",
    "backdrop_filter": "blur(20px)",
    "border": "1px solid rgba(255, 255, 255, 0.06)",
    "border_radius": "16px",
}

GLASS_CARD_HOVER = {
    "background": "rgba(22, 22, 42, 0.75)",
    "border": "1px solid rgba(255, 255, 255, 0.1)",
    "transform": "translateY(-4px)",
}

GLASS_PANEL = {
    "background": "rgba(10, 10, 26, 0.85)",
    "backdrop_filter": "blur(30px)",
    "border": "1px solid rgba(255, 255, 255, 0.06)",
}

GLASS_INPUT = {
    "background": "rgba(255, 255, 255, 0.04)",
    "border": "1px solid rgba(255, 255, 255, 0.08)",
    "border_radius": "12px",
    "color": "#ffffff",
    "transition": "all 0.2s ease",
}

# ============================================================
# SHADOWS & GLOWS
# ============================================================

def agent_glow(color: str, intensity: float = 0.2) -> str:
    """Generate a subtle colored glow for agent cards."""
    return f"0 0 30px {color}33, 0 4px 20px rgba(0, 0, 0, 0.3)"

def card_shadow() -> str:
    """Standard card shadow."""
    return "0 4px 24px rgba(0, 0, 0, 0.25)"

def elevated_shadow() -> str:
    """Elevated element shadow."""
    return "0 8px 32px rgba(0, 0, 0, 0.35)"

# ============================================================
# ANIMATION KEYFRAMES (CSS)
# ============================================================

ANIMATIONS_CSS = """
@keyframes pulse-glow {
    0%, 100% {
        opacity: 1;
        box-shadow: 0 0 10px currentColor;
    }
    50% {
        opacity: 0.6;
        box-shadow: 0 0 20px currentColor;
    }
}

@keyframes flow-dot {
    0% {
        transform: translateX(0);
        opacity: 0;
    }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% {
        transform: translateX(100%);
        opacity: 0;
    }
}

@keyframes fade-in-up {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes bounce-subtle {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
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

@keyframes slideInLeft {
    from {
        transform: translateX(-100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes status-pulse {
    0%, 100% {
        transform: scale(1);
        opacity: 1;
    }
    50% {
        transform: scale(1.2);
        opacity: 0.7;
    }
}

@keyframes flow-pulse {
    0%, 100% {
        transform: translateX(0) scale(1);
        opacity: 0.8;
    }
    50% {
        transform: translateX(10px) scale(1.2);
        opacity: 1;
    }
}

@keyframes ring-fill {
    from { stroke-dashoffset: 283; }
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Utility classes */
.skeleton {
    background: linear-gradient(
        90deg,
        rgba(255,255,255,0.03) 25%,
        rgba(255,255,255,0.08) 50%,
        rgba(255,255,255,0.03) 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}

.pulse-glow {
    animation: pulse-glow 2s ease-in-out infinite;
}

.fade-in-up {
    animation: fade-in-up 0.3s ease-out forwards;
}

.bounce-subtle {
    animation: bounce-subtle 2s ease-in-out infinite;
}

/* Agent card hover effect */
.agent-card {
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.agent-card:hover {
    transform: translateY(-4px) scale(1.02);
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
    background: rgba(124, 58, 237, 0.3);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(124, 58, 237, 0.5);
}

/* Drawer animation */
.drawer-content {
    animation: slideInRight 0.3s ease-out;
}

/* Log entry animation */
.log-entry {
    animation: fade-in-up 0.2s ease-out;
}

/* Ring chart animation */
.ring-chart circle {
    transition: stroke-dashoffset 1s ease-out;
}

/* Focus ring */
.focus-ring:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.3);
}

/* Gradient text */
.gradient-text {
    background: linear-gradient(135deg, #7c3aed, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
"""

# ============================================================
# COMPONENT STYLES
# ============================================================

# Sidebar
SIDEBAR_STYLE = {
    "background": "linear-gradient(180deg, rgba(10, 10, 26, 0.95) 0%, rgba(5, 5, 15, 0.98) 100%)",
    "border_right": f"1px solid {COLORS['border_subtle']}",
    "height": "100vh",
    "position": "fixed",
    "left": "0",
    "top": "0",
    "z_index": "100",
    "display": "flex",
    "flex_direction": "column",
    "transition": "width 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
    "overflow": "hidden",
}

# Navigation item styles
NAV_ITEM_STYLE = {
    "display": "flex",
    "align_items": "center",
    "gap": "12px",
    "padding": "10px 16px",
    "border_radius": "10px",
    "color": COLORS["text_secondary"],
    "cursor": "pointer",
    "transition": "all 0.2s ease",
    "text_decoration": "none",
}

NAV_ITEM_ACTIVE_STYLE = {
    **NAV_ITEM_STYLE,
    "background": f"linear-gradient(135deg, {COLORS['primary']}20, {COLORS['secondary']}15)",
    "color": COLORS["text_primary"],
    "border": f"1px solid {COLORS['border_accent']}",
}

# Main content area
MAIN_CONTENT_STYLE = {
    "min_height": "100vh",
    "background": f"linear-gradient(135deg, {COLORS['bg_dark']} 0%, #0f0f24 50%, {COLORS['bg_darker']} 100%)",
    "padding": "24px",
    "transition": "margin 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
}

# Stat card
STAT_CARD_STYLE = {
    "background": "rgba(15, 15, 30, 0.6)",
    "backdrop_filter": "blur(20px)",
    "border": f"1px solid {COLORS['border_subtle']}",
    "border_radius": "16px",
    "padding": "20px 24px",
    "position": "relative",
    "overflow": "hidden",
    "min_width": "180px",
    "transition": "all 0.2s ease",
}

# Agent card
AGENT_CARD_STYLE = {
    "background": "rgba(15, 15, 30, 0.6)",
    "backdrop_filter": "blur(20px)",
    "border": f"1px solid {COLORS['border_subtle']}",
    "border_radius": "16px",
    "padding": "16px",
    "cursor": "pointer",
    "transition": "all 0.25s cubic-bezier(0.4, 0, 0.2, 1)",
}

# Input styles
INPUT_STYLE = {
    "background": COLORS["bg_input"],
    "border": f"1px solid {COLORS['border_subtle']}",
    "border_radius": "12px",
    "padding": "14px 18px",
    "color": COLORS["text_primary"],
    "font_size": "0.95rem",
    "outline": "none",
    "transition": "all 0.2s ease",
    "width": "100%",
}

# Button primary
BUTTON_PRIMARY_STYLE = {
    "background": f"linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']})",
    "border": "none",
    "border_radius": "12px",
    "padding": "12px 24px",
    "color": "white",
    "font_weight": "600",
    "cursor": "pointer",
    "transition": "all 0.2s ease",
}

# Button ghost
BUTTON_GHOST_STYLE = {
    "background": "transparent",
    "border": f"1px solid {COLORS['border_subtle']}",
    "border_radius": "10px",
    "padding": "8px 16px",
    "color": COLORS["text_secondary"],
    "cursor": "pointer",
    "transition": "all 0.2s ease",
}

# Badge styles
BADGE_STYLE = {
    "padding": "4px 10px",
    "border_radius": "6px",
    "font_size": "0.75rem",
    "font_weight": "500",
    "display": "inline-flex",
    "align_items": "center",
    "gap": "6px",
}

# Log entry
LOG_ENTRY_STYLE = {
    "display": "flex",
    "align_items": "flex-start",
    "gap": "12px",
    "padding": "10px 12px",
    "border_radius": "8px",
    "transition": "background 0.15s ease",
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_status_badge_style(status: str) -> dict:
    """Get status-specific badge styling."""
    color_map = {
        "online": COLORS["status_online"],
        "working": COLORS["status_working"],
        "away": COLORS["status_away"],
        "error": COLORS["status_error"],
        "offline": COLORS["status_offline"],
    }
    color = color_map.get(status, COLORS["status_offline"])

    return {
        **BADGE_STYLE,
        "background": f"{color}15",
        "color": color,
        "border": f"1px solid {color}30",
    }

def get_agent_card_style(color: str) -> dict:
    """Get agent card style with colored glow on hover."""
    return {
        **AGENT_CARD_STYLE,
        "_hover": {
            "transform": "translateY(-4px) scale(1.02)",
            "border_color": f"{color}40",
            "box_shadow": f"0 0 30px {color}20, 0 8px 32px rgba(0, 0, 0, 0.3)",
        },
    }

# ============================================================
# GRADIENTS
# ============================================================

GRADIENT_PRIMARY = f"linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']})"
GRADIENT_CARD = "linear-gradient(145deg, rgba(15, 15, 30, 0.8), rgba(10, 10, 25, 0.6))"
GRADIENT_BG = f"linear-gradient(135deg, {COLORS['bg_dark']} 0%, #0f0f24 50%, {COLORS['bg_darker']} 100%)"
GRADIENT_PURPLE_BLUE = f"linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']})"

# ============================================================
# Z-INDEX SCALE
# ============================================================

Z_INDEX = {
    "sidebar": 100,
    "header": 90,
    "monitoring": 80,
    "modal": 200,
    "drawer": 150,
    "tooltip": 300,
    "notification": 400,
}
