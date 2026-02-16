"""
ClawCrew Dashboard
A Streamlit-based dashboard for monitoring AI agent teams.
Inspired by Figma Virtual Office Dashboard design.
"""

import streamlit as st
import requests
import time
from datetime import datetime
import json
from pathlib import Path

# Configuration
API_URL = "http://localhost:6000"
REFRESH_INTERVAL = 5  # seconds

# Page config
st.set_page_config(
    page_title="ClawCrew Dashboard",
    page_icon="🦞",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS - Figma Virtual Office Dashboard inspired design
st.markdown("""
<style>
    /* Main theme - Light mode with soft blue/purple */
    :root {
        --bg-primary: #f8fafc;
        --bg-card: #ffffff;
        --bg-sidebar: #f1f5f9;
        --border-color: #e2e8f0;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-green: #22c55e;
        --accent-orange: #f97316;
        --accent-red: #ef4444;
        --accent-yellow: #eab308;
    }

    /* Hide Streamlit branding but keep sidebar toggle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Keep header visible for sidebar toggle button */
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* Main container */
    .main .block-container {
        padding: 1rem 2rem;
        max-width: 100%;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar);
        border-right: 1px solid var(--border-color);
    }

    /* ============================================ */
    /* AGENT FLOOR - Virtual Office Style */
    /* ============================================ */

    .agent-floor {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        padding: 2rem;
        min-height: 400px;
        position: relative;
        border: 1px solid var(--border-color);
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
    }

    .department-label {
        position: absolute;
        top: -12px;
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
    }

    .department-orchestrator { background: #6366f1; left: 20px; }
    .department-design { background: #8b5cf6; left: 180px; }
    .department-engineering { background: #3b82f6; right: 180px; }
    .department-qa { background: #10b981; right: 20px; }

    /* Agent Card - Virtual Office Style */
    .vo-agent-card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        border: 2px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        min-height: 200px;
    }

    .vo-agent-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: var(--accent-blue);
        z-index: 100;
    }

    .vo-agent-card.status-running {
        border-color: var(--accent-orange);
        animation: card-pulse 2s infinite;
    }

    .vo-agent-card.status-running:hover {
        border-color: var(--accent-orange);
    }

    @keyframes card-pulse {
        0%, 100% { box-shadow: 0 4px 6px -1px rgba(249, 115, 22, 0.2); }
        50% { box-shadow: 0 4px 20px -1px rgba(249, 115, 22, 0.4); }
    }

    /* ===== NEW: Virtual Office Animations ===== */
    @keyframes pulse-glow {
        0%, 100% {
            box-shadow: 0 0 10px rgba(249,115,22,0.4);
            transform: scale(1);
        }
        50% {
            box-shadow: 0 0 25px rgba(249,115,22,0.7);
            transform: scale(1.1);
        }
    }

    /* ===== NEW: Gradient Progress Bar ===== */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 25%, #3b82f6 50%, #10b981 100%) !important;
    }

    /* Lead Badge */
    .lead-badge {
        position: absolute;
        top: -8px;
        left: 12px;
        background: #dbeafe;
        color: #1d4ed8;
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        border: 1px solid #93c5fd;
    }

    /* Avatar */
    .vo-avatar {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        margin: 0 auto 0.75rem;
        position: relative;
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .vo-avatar-status {
        position: absolute;
        bottom: 2px;
        right: 2px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border: 3px solid white;
    }

    .vo-avatar-status.online { background: var(--accent-green); }
    .vo-avatar-status.running { background: var(--accent-orange); animation: status-blink 1s infinite; }
    .vo-avatar-status.away { background: var(--accent-yellow); }
    .vo-avatar-status.offline { background: #94a3b8; }
    .vo-avatar-status.error { background: var(--accent-red); }

    @keyframes status-blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Agent Info */
    .vo-agent-name {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        text-align: center;
        margin-bottom: 0.25rem;
    }

    .vo-agent-role {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 0.75rem;
    }

    /* Status Badge */
    .vo-status-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }

    .vo-status-badge.online {
        background: #dcfce7;
        color: #15803d;
    }

    .vo-status-badge.running {
        background: #ffedd5;
        color: #c2410c;
    }

    .vo-status-badge.away {
        background: #fef9c3;
        color: #a16207;
    }

    .vo-status-badge.offline {
        background: #f1f5f9;
        color: #64748b;
    }

    .vo-status-badge.error {
        background: #fee2e2;
        color: #b91c1c;
    }

    .vo-status-icon {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    .vo-status-icon.online { background: var(--accent-green); }
    .vo-status-icon.running { background: var(--accent-orange); }
    .vo-status-icon.away { background: var(--accent-yellow); }
    .vo-status-icon.offline { background: #94a3b8; }
    .vo-status-icon.error { background: var(--accent-red); }

    /* Idle time */
    .vo-idle-time {
        font-size: 0.7rem;
        color: var(--text-secondary);
        text-align: center;
    }

    /* Agent Details (on hover/click) */
    .vo-agent-details {
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid var(--border-color);
        font-size: 0.75rem;
    }

    .vo-detail-row {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
        color: var(--text-secondary);
    }

    .vo-detail-label {
        font-weight: 500;
    }

    .vo-detail-value {
        color: var(--text-primary);
        font-weight: 600;
    }

    .vo-current-task {
        background: #f8fafc;
        border-radius: 8px;
        padding: 8px;
        margin-top: 8px;
        font-size: 0.7rem;
        color: var(--text-secondary);
        line-height: 1.4;
    }

    .vo-current-task strong {
        color: var(--text-primary);
        display: block;
        margin-bottom: 4px;
    }

    /* ============================================ */
    /* Status Legend */
    /* ============================================ */

    .status-legend {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        padding: 0.75rem;
        background: white;
        border-radius: 30px;
        border: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        color: var(--text-secondary);
    }

    .legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }

    .legend-dot.online { background: var(--accent-green); }
    .legend-dot.running { background: var(--accent-orange); }
    .legend-dot.away { background: var(--accent-yellow); }
    .legend-dot.offline { background: #94a3b8; }

    /* ============================================ */
    /* Other existing styles */
    /* ============================================ */

    .card {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid var(--border-color);
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    .card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }

    .card-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }

    /* Sidebar Agent card */
    .agent-card {
        background: var(--bg-card);
        border-radius: 10px;
        padding: 0.875rem;
        border: 1px solid var(--border-color);
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }

    .agent-card:hover {
        border-color: var(--accent-blue);
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
    }

    .agent-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .agent-emoji {
        font-size: 1.5rem;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-sidebar);
        border-radius: 8px;
    }

    .agent-info {
        flex: 1;
    }

    .agent-name {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.9rem;
        text-transform: capitalize;
    }

    .agent-role {
        color: var(--text-secondary);
        font-size: 0.75rem;
    }

    /* Status indicators */
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }

    .status-running { background-color: var(--accent-orange); animation: pulse 1.5s infinite; }
    .status-idle { background-color: var(--accent-green); }
    .status-completed { background-color: #94a3b8; }
    .status-error { background-color: var(--accent-red); }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Log container */
    .log-container {
        background: #1e293b;
        border-radius: 10px;
        padding: 1rem;
        font-family: 'SF Mono', 'Fira Code', monospace;
        font-size: 0.8rem;
        max-height: 400px;
        overflow-y: auto;
        color: #e2e8f0;
    }

    .log-entry {
        padding: 0.25rem 0;
        border-bottom: 1px solid #334155;
    }

    .log-time {
        color: #64748b;
        margin-right: 0.5rem;
    }

    .log-agent {
        color: var(--accent-blue);
        font-weight: 600;
    }

    .log-agent-orca { color: #6366f1; }
    .log-agent-design { color: #8b5cf6; }
    .log-agent-code { color: #3b82f6; }
    .log-agent-test { color: #10b981; }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-sidebar);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)


# Helper functions
def fetch_api(endpoint: str, default=None):
    """Fetch data from API with error handling."""
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return default
    except requests.exceptions.RequestException:
        return default


def get_status_class(status: str) -> str:
    """Get CSS class for status."""
    status_map = {
        "running": "running",
        "idle": "online",
        "completed": "offline",
        "error": "error",
        "away": "away",
    }
    return status_map.get(status.lower(), "offline")


def get_status_label(status: str) -> str:
    """Get display label for status."""
    status_map = {
        "running": "In Progress",
        "idle": "Online",
        "completed": "Completed",
        "error": "Error",
        "away": "Away",
    }
    return status_map.get(status.lower(), status.title())


def format_tokens(n: int) -> str:
    """Format token count."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def render_agent_card_sidebar(agent: dict):
    """Render an agent card in the sidebar."""
    status_class = f"status-{agent.get('status', 'idle').lower()}"

    html = f"""
    <div class="agent-card">
        <div class="agent-header">
            <div class="agent-emoji">{agent.get('emoji', '🤖')}</div>
            <div class="agent-info">
                <div class="agent-name">
                    <span class="status-dot {status_class}"></span>
                    {agent.get('name', 'Unknown').title()}
                </div>
                <div class="agent-role">{agent.get('role', 'Agent')}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_virtual_office_agent(agent: dict, show_details: bool = True):
    """Render a single agent card in Virtual Office style."""
    status = agent.get("status", "idle")
    status_class = get_status_class(status)
    status_label = get_status_label(status)
    is_lead = agent.get("name", "").lower() == "orca"

    # Card status class
    card_class = f"vo-agent-card status-{status}"

    # Build HTML
    html = f'''
    <div class="{card_class}">
        {"<div class='lead-badge'>LEAD</div>" if is_lead else ""}

        <div class="vo-avatar">
            {agent.get('emoji', '🤖')}
            <div class="vo-avatar-status {status_class}"></div>
        </div>

        <div class="vo-agent-name">{agent.get('name', 'Unknown').title()}</div>
        <div class="vo-agent-role">{agent.get('role', 'Agent')}</div>

        <div class="vo-status-badge {status_class}">
            <span class="vo-status-icon {status_class}"></span>
            {status_label}
        </div>

        <div class="vo-idle-time">
            {f"Active: {agent.get('last_active', 'Just now')}" if status == "running" else f"Idle: {agent.get('idle_time', '3 min')}"}
        </div>
    '''

    if show_details:
        html += f'''
        <div class="vo-agent-details">
            <div class="vo-detail-row">
                <span class="vo-detail-label">Model</span>
                <span class="vo-detail-value">{agent.get('model', 'claude-3-opus')}</span>
            </div>
            <div class="vo-detail-row">
                <span class="vo-detail-label">Tokens</span>
                <span class="vo-detail-value">{format_tokens(agent.get('tokens', 0))}</span>
            </div>
            <div class="vo-detail-row">
                <span class="vo-detail-label">Tasks</span>
                <span class="vo-detail-value">{agent.get('task_count', 0)}</span>
            </div>
        '''

        if agent.get('current_task'):
            html += f'''
            <div class="vo-current-task">
                <strong>Current Task:</strong>
                {agent.get('current_task', '')[:60]}{'...' if len(agent.get('current_task', '')) > 60 else ''}
            </div>
            '''

        html += '</div>'

    html += '</div>'

    return html


def render_agent_floor_native(agents: list):
    """Render the Virtual Office agent floor using native Streamlit components."""

    # ========== VIRTUAL OFFICE HEADER ==========
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(248,250,252,0.98) 0%, rgba(241,245,249,0.98) 100%),
            url('https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=80') center/cover;
        background-blend-mode: overlay;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    ">
        <div style="text-align:center;margin-bottom:1rem;">
            <span style="
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                color: white;
                padding: 6px 20px;
                border-radius: 25px;
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 1px;
                box-shadow: 0 4px 15px rgba(99,102,241,0.3);
            ">🏢 VIRTUAL OFFICE</span>
        </div>
        <div style="display:flex;justify-content:center;align-items:center;gap:0.5rem;flex-wrap:wrap;">
            <span style="background:#6366f1;color:white;padding:4px 12px;border-radius:12px;font-weight:600;font-size:0.8rem;">🦑 Orca</span>
            <span style="color:#6366f1;font-weight:bold;">→</span>
            <span style="background:#8b5cf6;color:white;padding:4px 12px;border-radius:12px;font-weight:600;font-size:0.8rem;">🎨 Design</span>
            <span style="color:#8b5cf6;font-weight:bold;">→</span>
            <span style="background:#3b82f6;color:white;padding:4px 12px;border-radius:12px;font-weight:600;font-size:0.8rem;">💻 Code</span>
            <span style="color:#3b82f6;font-weight:bold;">→</span>
            <span style="background:#10b981;color:white;padding:4px 12px;border-radius:12px;font-weight:600;font-size:0.8rem;">🧪 Test</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ========== AGENT WORKSTATION CARDS ==========
    cols = st.columns(4, gap="medium")

    agent_colors = {"orca": "#6366f1", "design": "#8b5cf6", "code": "#3b82f6", "test": "#10b981"}

    for i, agent in enumerate(agents):
        with cols[i % 4]:
            status = agent.get("status", "idle")
            agent_name = agent.get("name", "agent").lower()
            accent_color = agent_colors.get(agent_name, "#6366f1")
            is_lead = agent_name == "orca"

            status_config = {
                "running": {"bg": "#ffedd5", "color": "#c2410c", "dot": "#f97316", "label": "Working"},
                "idle": {"bg": "#dcfce7", "color": "#15803d", "dot": "#22c55e", "label": "Online"},
                "completed": {"bg": "#f1f5f9", "color": "#64748b", "dot": "#94a3b8", "label": "Done"},
                "error": {"bg": "#fee2e2", "color": "#b91c1c", "dot": "#ef4444", "label": "Error"},
            }
            cfg = status_config.get(status, status_config["idle"])

            lead_badge = f'<div style="position:absolute;top:-10px;left:12px;background:linear-gradient(135deg,#fbbf24,#f59e0b);color:white;padding:3px 10px;border-radius:10px;font-size:0.65rem;font-weight:700;">👑 LEAD</div>' if is_lead else ''

            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.95);border-radius:16px;padding:1rem;border:2px solid {accent_color}40;box-shadow:0 8px 25px rgba(0,0,0,0.08);position:relative;margin-top:12px;">
                <div style="position:absolute;top:-12px;right:12px;font-size:1.2rem;background:white;padding:2px 6px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">🖥️</div>
                {lead_badge}
                <div style="position:absolute;top:12px;left:12px;width:12px;height:12px;border-radius:50%;background:{cfg['dot']};box-shadow:0 0 10px {cfg['dot']}80;"></div>
                <div style="text-align:center;margin:0.5rem 0;">
                    <div style="width:60px;height:60px;margin:0 auto;background:linear-gradient(145deg,#fff,#f1f5f9);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;border:3px solid {accent_color};box-shadow:0 4px 12px rgba(0,0,0,0.1);">{agent.get('emoji', '🤖')}</div>
                </div>
                <h4 style="text-align:center;margin:0.4rem 0 0.2rem;font-size:0.95rem;color:#1e293b;">{agent.get('name', '?').title()}</h4>
                <p style="text-align:center;color:#64748b;font-size:0.7rem;margin:0 0 0.5rem;">{agent.get('role', 'Agent')}</p>
                <div style="text-align:center;margin:0.5rem 0;">
                    <span style="background:{cfg['bg']};color:{cfg['color']};padding:4px 12px;border-radius:15px;font-size:0.7rem;font-weight:600;">● {cfg['label']}</span>
                </div>
                <div style="background:#f8fafc;border-radius:8px;padding:6px 8px;margin-top:8px;font-size:0.7rem;">
                    <div style="display:flex;justify-content:space-between;color:#64748b;"><span>📊 Tokens</span><span style="font-weight:600;color:#1e293b;">{format_tokens(agent.get('tokens', 0))}</span></div>
                    <div style="display:flex;justify-content:space-between;color:#64748b;"><span>📋 Tasks</span><span style="font-weight:600;color:#1e293b;">{agent.get('task_count', 0)}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if agent.get('current_task'):
                task_text = agent.get('current_task', '')[:40]
                if len(agent.get('current_task', '')) > 40:
                    task_text += '...'
                st.markdown(f'<div style="background:{accent_color}10;border-radius:8px;padding:6px 10px;margin-top:6px;font-size:0.7rem;border-left:3px solid {accent_color};"><span style="color:#64748b;">💬 {task_text}</span></div>', unsafe_allow_html=True)


def render_logs(logs: list):
    """Render log entries."""
    if not logs:
        st.info("No logs available. Start a task to see activity.")
        return

    log_html = '<div class="log-container">'
    for log in reversed(logs[-50:]):
        timestamp = log.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M:%S")
            except:
                time_str = timestamp[:8]
        else:
            time_str = "--:--:--"

        agent = log.get("agent", "system")
        message = log.get("message", "")

        log_html += f'''
        <div class="log-entry">
            <span class="log-time">{time_str}</span>
            <span class="log-agent log-agent-{agent}">[{agent}]</span>
            <span>{message}</span>
        </div>
        '''
    log_html += '</div>'

    st.markdown(log_html, unsafe_allow_html=True)


# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None


# Sidebar
with st.sidebar:
    # Logo & Title
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem;">
        <span style="font-size: 2rem;">🦞</span>
        <div>
            <h1 style="margin: 0; font-size: 1.5rem;">ClawCrew</h1>
            <span style="color: var(--text-secondary); font-size: 0.75rem;">Agent Dashboard</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown("### Navigation")

    nav_items = [
        ("🏠", "Home", "home"),
        ("🤖", "Agents", "agents"),
        ("📁", "Artifacts", "artifacts"),
        ("📋", "Logs", "logs"),
        ("⚙️", "Settings", "settings"),
    ]

    for icon, label, page_id in nav_items:
        if st.button(f"{icon}  {label}", key=f"nav_{page_id}", use_container_width=True):
            st.session_state.page = page_id
            st.rerun()

    st.divider()

    # Agents list
    st.markdown("### Agents")

    agents = fetch_api("/api/agents", [])
    if not agents:
        # Mock data when API is not available
        agents = [
            {"name": "orca", "emoji": "🦑", "role": "Orchestrator", "status": "running"},
            {"name": "design", "emoji": "🎨", "role": "Architect", "status": "completed"},
            {"name": "code", "emoji": "💻", "role": "Engineer", "status": "running"},
            {"name": "test", "emoji": "🧪", "role": "QA", "status": "idle"},
        ]

    for agent in agents:
        render_agent_card_sidebar(agent)

    st.divider()

    # Auto-refresh toggle
    st.session_state.auto_refresh = st.toggle("Auto-refresh", value=st.session_state.auto_refresh)

    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()


# Main content area
page = st.session_state.page

if page == "home":
    # Top Bar: Stats (left) + Status Legend (right)
    stats = fetch_api("/api/stats", {})
    tokens = fetch_api("/api/tokens", {})

    st.markdown(f"""
    <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 1rem;
        background: white;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    ">
        <div style="display: flex; gap: 2rem; align-items: center;">
            <span><span style="color:#64748b;">Tasks:</span> <strong>{stats.get("total_tasks", 3)}</strong></span>
            <span><span style="color:#64748b;">Running:</span> <strong>{stats.get("agents_running", 2)}</strong></span>
            <span><span style="color:#64748b;">Tokens:</span> <strong>{format_tokens(tokens.get("total", 15420))}</strong></span>
            <span><span style="color:#64748b;">Success:</span> <strong>94%</strong></span>
        </div>
        <div style="display: flex; gap: 1rem; font-size: 0.8rem; color: #64748b;">
            <span>🟢 Online</span>
            <span>🟠 Running</span>
            <span>🟡 Away</span>
            <span>⚪ Offline</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Agent Team - Visual Focus
    agents = fetch_api("/api/agents", [])
    if not agents:
        agents = [
            {
                "name": "orca",
                "emoji": "🦑",
                "role": "Orchestrator",
                "status": "running",
                "last_active": "Just now",
                "idle_time": "0 min",
                "model": "claude-3-opus",
                "tokens": 4200,
                "task_count": 12,
                "current_task": "Coordinating email validation task, reviewing CodeBot output"
            },
            {
                "name": "design",
                "emoji": "🎨",
                "role": "Architect",
                "status": "idle",
                "last_active": "10 min ago",
                "idle_time": "10 min",
                "model": "claude-3-sonnet",
                "tokens": 3800,
                "task_count": 8,
                "current_task": None
            },
            {
                "name": "code",
                "emoji": "💻",
                "role": "Engineer",
                "status": "running",
                "last_active": "2 min ago",
                "idle_time": "0 min",
                "model": "claude-3-opus",
                "tokens": 5120,
                "task_count": 15,
                "current_task": "Implementing email validation with regex pattern matching"
            },
            {
                "name": "test",
                "emoji": "🧪",
                "role": "QA Engineer",
                "status": "idle",
                "last_active": "30 min ago",
                "idle_time": "30 min",
                "model": "claude-3-sonnet",
                "tokens": 2300,
                "task_count": 6,
                "current_task": None
            },
        ]

    render_agent_floor_native(agents)

    st.divider()

    # === TASKS SECTION ===
    st.markdown("### 📋 Tasks")
    st.markdown("""
    <div style="background:white;border-radius:10px;padding:0.75rem 1rem;border:1px solid #e2e8f0;margin-bottom:0.5rem;">
        <strong>Create email validation function</strong>
        <span style="color:#64748b;font-size:0.8rem;margin-left:0.5rem;">ID: 20240214-153042 • Code phase</span>
    </div>
    """, unsafe_allow_html=True)
    st.progress(0.6, text="Orca → Design ✓ → Code (running) → Test")

    st.divider()

    # === TOKEN USAGE SECTION ===
    st.markdown("### 📊 Token Usage")
    token_data = tokens.get("by_agent", {"orca": 4200, "design": 3800, "code": 5120, "test": 2300})

    import pandas as pd
    df = pd.DataFrame({
        "Agent": list(token_data.keys()),
        "Tokens": list(token_data.values())
    })

    col1, col2 = st.columns([2, 1])
    with col1:
        st.bar_chart(df.set_index("Agent"), color="#6366f1", height=200)
    with col2:
        st.markdown("**Recent Activity**")
        history = tokens.get("history", [])[-5:]
        if history:
            for entry in reversed(history):
                agent = entry.get("agent", "unknown")
                toks = entry.get("tokens", 0)
                st.markdown(f"🔹 **{agent.title()}**: +{toks}")
        else:
            st.markdown("🔹 **Orca**: +320")
            st.markdown("🔹 **Code**: +480")
            st.markdown("🔹 **Design**: +250")

    st.divider()

    # === LIVE LOGS SECTION ===
    st.markdown("### 📜 Live Logs")
    logs = fetch_api("/api/logs", [])
    if not logs:
        logs = [
            {"timestamp": "2024-02-14T15:30:42", "agent": "orca", "message": "Received task: Create email validation function"},
            {"timestamp": "2024-02-14T15:30:43", "agent": "orca", "message": "task_id = 20240214-153042"},
            {"timestamp": "2024-02-14T15:30:45", "agent": "orca", "message": "Calling DesignBot: ./bin/agent-cli.py --agent design api-spec ..."},
            {"timestamp": "2024-02-14T15:31:02", "agent": "design", "message": "Analyzing requirements..."},
            {"timestamp": "2024-02-14T15:32:15", "agent": "design", "message": "Output saved to artifacts/20240214-153042/design.md"},
            {"timestamp": "2024-02-14T15:32:18", "agent": "orca", "message": "Quality gate passed → Calling CodeBot ..."},
            {"timestamp": "2024-02-14T15:32:45", "agent": "code", "message": "Implementing email validation with regex pattern"},
            {"timestamp": "2024-02-14T15:33:10", "agent": "code", "message": "Adding type hints and docstrings"},
        ]
    render_logs(logs)


elif page == "agents":
    st.markdown("## 🤖 Agents")
    st.divider()

    agents = fetch_api("/api/agents", [])
    if not agents:
        agents = [
            {
                "name": "orca",
                "emoji": "🦑",
                "role": "Orchestrator",
                "status": "running",
                "last_active": "Just now",
                "idle_time": "0 min",
                "model": "claude-3-opus",
                "tokens": 4200,
                "task_count": 12,
                "current_task": "Coordinating email validation task",
                "color": "#6366f1"
            },
            {
                "name": "design",
                "emoji": "🎨",
                "role": "Architect",
                "status": "idle",
                "last_active": "10 min ago",
                "idle_time": "10 min",
                "model": "claude-3-sonnet",
                "tokens": 3800,
                "task_count": 8,
                "current_task": None,
                "color": "#8b5cf6"
            },
            {
                "name": "code",
                "emoji": "💻",
                "role": "Engineer",
                "status": "running",
                "last_active": "2 min ago",
                "idle_time": "0 min",
                "model": "claude-3-opus",
                "tokens": 5120,
                "task_count": 15,
                "current_task": "Implementing email validation",
                "color": "#3b82f6"
            },
            {
                "name": "test",
                "emoji": "🧪",
                "role": "QA Engineer",
                "status": "idle",
                "last_active": "30 min ago",
                "idle_time": "30 min",
                "model": "claude-3-sonnet",
                "tokens": 2300,
                "task_count": 6,
                "current_task": None,
                "color": "#10b981"
            },
        ]

    render_agent_floor_native(agents)

    st.divider()

    # Detailed view with expanders
    st.markdown("### 📋 Agent Details")

    cols = st.columns(2)
    for i, agent in enumerate(agents):
        with cols[i % 2]:
            status = agent.get("status", "idle")
            status_color = {
                "running": "#f97316",
                "idle": "#10b981",
                "completed": "#94a3b8",
                "error": "#ef4444"
            }.get(status, "#94a3b8")

            with st.container():
                st.markdown(f"""
                <div class="card" style="border-left: 4px solid {agent.get('color', '#6366f1')};">
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                        <span style="font-size: 2.5rem;">{agent.get('emoji', '🤖')}</span>
                        <div>
                            <h3 style="margin: 0; font-size: 1.25rem;">{agent.get('name', 'Unknown').title()}</h3>
                            <span style="color: var(--text-secondary);">{agent.get('role', 'Agent')}</span>
                        </div>
                        <div style="margin-left: auto; display: flex; align-items: center; gap: 0.5rem;">
                            <span style="width: 10px; height: 10px; border-radius: 50%; background: {status_color};"></span>
                            <span style="text-transform: capitalize; color: {status_color}; font-weight: 500;">{status}</span>
                        </div>
                    </div>
                    <div style="color: var(--text-secondary); font-size: 0.875rem;">
                        Last active: {agent.get('last_active', 'Never')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("View Details"):
                    detail = fetch_api(f"/api/agents/{agent.get('name')}", {})
                    if detail:
                        st.markdown("**SOUL Summary:**")
                        st.code(detail.get("soul_summary", "No SOUL.md found"), language="markdown")

                        memory = detail.get("recent_memory", [])
                        if memory:
                            st.markdown("**Recent Memory:**")
                            for m in memory:
                                st.text(f"📅 {m.get('date', '')}")
                                st.code(m.get("content", ""), language="markdown")
                    else:
                        st.info("Connect to API for live details")


elif page == "artifacts":
    st.markdown("## 📁 Artifacts")
    st.divider()

    artifacts = fetch_api("/api/artifacts", {})

    if artifacts and artifacts.get("tasks"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Files", artifacts.get("total_files", 0))
        with col2:
            size_kb = artifacts.get("total_size", 0) / 1024
            st.metric("Total Size", f"{size_kb:.1f} KB")
        with col3:
            st.metric("Tasks", len(artifacts.get("tasks", [])))

        st.divider()

        for task in artifacts.get("tasks", []):
            with st.expander(f"📂 {task.get('task_id', 'Unknown')}", expanded=False):
                for f in task.get("files", []):
                    file_icon = {"py": "🐍", "md": "📝", "txt": "📄", "json": "📋"}.get(f.get("type", ""), "📄")

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button(f"{file_icon} {f.get('name', 'file')}", key=f"file_{f.get('path', '')}"):
                            content = fetch_api(f"/api/artifacts/{f.get('path', '')}", {})
                            if content:
                                st.session_state.preview_file = content
                    with col2:
                        st.caption(f"{f.get('size', 0)} bytes")

                if hasattr(st.session_state, 'preview_file') and st.session_state.preview_file:
                    preview = st.session_state.preview_file
                    lang = {"py": "python", "md": "markdown", "json": "json"}.get(preview.get("type", ""), "text")
                    st.code(preview.get("content", ""), language=lang)
    else:
        st.info("No artifacts found. Run a task to generate outputs.")

        # Demo file structure
        st.markdown("**Expected structure:**")
        st.code("""
artifacts/
├── 20240214-153042/
│   ├── design.md       (API specification)
│   ├── main.py         (Implementation)
│   └── test_main.py    (Unit tests)
└── ...
        """, language="text")


elif page == "logs":
    st.markdown("## 📋 Logs")
    st.divider()

    col1, col2 = st.columns([2, 1])
    with col1:
        agent_filter = st.selectbox(
            "Filter by agent",
            ["All", "orca", "design", "code", "test"],
            index=0
        )
    with col2:
        limit = st.number_input("Show last N entries", min_value=10, max_value=500, value=100)

    logs = fetch_api(f"/api/logs?limit={limit}", [])
    if agent_filter != "All":
        logs = [l for l in logs if l.get("agent") == agent_filter]

    if not logs:
        logs = [
            {"timestamp": "2024-02-14T15:30:42", "agent": "orca", "message": "Received task: Create email validation function", "level": "info"},
            {"timestamp": "2024-02-14T15:30:43", "agent": "orca", "message": "task_id = 20240214-153042", "level": "info"},
            {"timestamp": "2024-02-14T15:30:45", "agent": "orca", "message": "Calling DesignBot: ./bin/agent-cli.py --agent design api-spec ...", "level": "info"},
            {"timestamp": "2024-02-14T15:31:02", "agent": "design", "message": "Analyzing requirements...", "level": "info"},
            {"timestamp": "2024-02-14T15:32:15", "agent": "design", "message": "Output saved to artifacts/20240214-153042/design.md", "level": "success"},
            {"timestamp": "2024-02-14T15:32:18", "agent": "orca", "message": "Quality gate passed → Calling CodeBot ...", "level": "info"},
            {"timestamp": "2024-02-14T15:32:45", "agent": "code", "message": "Implementing email validation with regex pattern", "level": "info"},
            {"timestamp": "2024-02-14T15:33:10", "agent": "code", "message": "Adding type hints and docstrings", "level": "info"},
        ]

    render_logs(logs)

    # Download logs
    if logs:
        log_text = "\n".join([
            f"{l.get('timestamp', '')} [{l.get('agent', '')}] {l.get('message', '')}"
            for l in logs
        ])
        st.download_button(
            "📥 Download Logs",
            data=log_text,
            file_name="clawcrew_logs.txt",
            mime="text/plain"
        )


elif page == "settings":
    st.markdown("## ⚙️ Settings")
    st.divider()

    st.markdown("### API Configuration")

    api_url = st.text_input("API URL", value=API_URL)
    refresh_interval = st.slider("Auto-refresh interval (seconds)", 1, 30, REFRESH_INTERVAL)

    st.divider()

    st.markdown("### Theme")
    theme = st.radio("Color mode", ["Light", "Dark"], horizontal=True)

    st.divider()

    st.markdown("### Demo Data")
    st.info("Generate demo data for testing the dashboard without a running backend.")

    if st.button("🎲 Generate Demo Data", type="primary"):
        result = fetch_api("/api/demo/generate", None)
        if result:
            st.success("Demo data generated! Refresh to see changes.")
        else:
            st.warning("API not available. Using mock data.")

    st.divider()

    st.markdown("### About")
    st.markdown("""
    **ClawCrew Dashboard** v1.0.0

    A Streamlit-based monitoring interface for ClawCrew multi-agent teams.

    - 🦞 [ClawCrew GitHub](https://github.com/lanxindeng8/clawcrew)
    - 📚 [OpenClaw Docs](https://openclaw.ai)
    """)


# Auto-refresh
if st.session_state.auto_refresh and page in ["home", "logs"]:
    time.sleep(REFRESH_INTERVAL)
    st.rerun()
