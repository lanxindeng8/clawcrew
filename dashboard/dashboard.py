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

# Custom CSS - Figma-inspired design
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
        --accent-green: #10b981;
        --accent-orange: #f97316;
        --accent-red: #ef4444;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

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

    [data-testid="stSidebar"] .stMarkdown h1 {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    /* Card styling */
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

    /* Agent card */
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

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
        border-radius: 12px;
        padding: 1.25rem;
        color: white;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .metric-label {
        font-size: 0.875rem;
        opacity: 0.9;
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

    /* Workflow visualization */
    .workflow-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.5rem;
        gap: 0.5rem;
    }

    .workflow-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }

    .workflow-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        background: var(--bg-sidebar);
        border: 2px solid var(--border-color);
    }

    .workflow-icon.active {
        border-color: var(--accent-blue);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    }

    .workflow-icon.completed {
        border-color: var(--accent-green);
        background: #ecfdf5;
    }

    .workflow-arrow {
        color: var(--border-color);
        font-size: 1.5rem;
    }

    /* File tree */
    .file-item {
        display: flex;
        align-items: center;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        cursor: pointer;
        transition: background 0.2s;
    }

    .file-item:hover {
        background: var(--bg-sidebar);
    }

    .file-icon {
        margin-right: 0.5rem;
    }

    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Navigation */
    .nav-item {
        padding: 0.625rem 0.875rem;
        border-radius: 8px;
        margin-bottom: 0.25rem;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 0.625rem;
        color: var(--text-secondary);
    }

    .nav-item:hover {
        background: rgba(59, 130, 246, 0.1);
        color: var(--accent-blue);
    }

    .nav-item.active {
        background: var(--accent-blue);
        color: white;
    }

    /* Top bar */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid var(--border-color);
    }

    .search-box {
        background: var(--bg-sidebar);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        width: 300px;
        font-size: 0.875rem;
    }

    /* Chart container */
    .chart-container {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid var(--border-color);
    }

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
    return f"status-{status.lower()}"


def format_tokens(n: int) -> str:
    """Format token count."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def render_agent_card(agent: dict, expanded: bool = False):
    """Render an agent card in the sidebar."""
    status_class = get_status_class(agent.get("status", "idle"))

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


def render_workflow(current_phase: str = "code"):
    """Render workflow visualization."""
    phases = [
        {"name": "Orca", "emoji": "🦑", "status": "completed"},
        {"name": "Design", "emoji": "🎨", "status": "completed"},
        {"name": "Code", "emoji": "💻", "status": "active"},
        {"name": "Test", "emoji": "🧪", "status": "pending"},
    ]

    html = '<div class="workflow-container">'
    for i, phase in enumerate(phases):
        status_class = phase["status"]
        html += f'''
        <div class="workflow-step">
            <div class="workflow-icon {status_class}">{phase["emoji"]}</div>
            <span style="font-size: 0.75rem; color: var(--text-secondary);">{phase["name"]}</span>
        </div>
        '''
        if i < len(phases) - 1:
            html += '<span class="workflow-arrow">→</span>'
    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)


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
    if agents:
        for agent in agents:
            render_agent_card(agent)
    else:
        # Mock data when API is not available
        mock_agents = [
            {"name": "orca", "emoji": "🦑", "role": "Orchestrator", "status": "running"},
            {"name": "design", "emoji": "🎨", "role": "Architect", "status": "completed"},
            {"name": "code", "emoji": "💻", "role": "Engineer", "status": "running"},
            {"name": "test", "emoji": "🧪", "role": "QA", "status": "idle"},
        ]
        for agent in mock_agents:
            render_agent_card(agent)

    st.divider()

    # Auto-refresh toggle
    st.session_state.auto_refresh = st.toggle("Auto-refresh", value=st.session_state.auto_refresh)

    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()


# Main content area
page = st.session_state.page

if page == "home":
    # Top bar
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("## 🏠 Dashboard")
    with col2:
        st.text_input("🔍", placeholder="Search...", label_visibility="collapsed")
    with col3:
        st.markdown(f"<div style='text-align: right; padding-top: 0.5rem;'>🔔  👤</div>", unsafe_allow_html=True)

    st.divider()

    # Stats row
    stats = fetch_api("/api/stats", {})
    tokens = fetch_api("/api/tokens", {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Tasks",
            value=stats.get("total_tasks", 0),
            delta=None
        )
    with col2:
        st.metric(
            label="Agents Running",
            value=stats.get("agents_running", 1),
            delta=None
        )
    with col3:
        st.metric(
            label="Total Tokens",
            value=format_tokens(tokens.get("total", 15420)),
            delta=None
        )
    with col4:
        st.metric(
            label="Log Entries",
            value=stats.get("log_count", 8),
            delta=None
        )

    st.divider()

    # Current task & workflow
    st.markdown("### 📋 Current Task")

    with st.container():
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <span style="font-size: 1.25rem;">📧</span>
                <h3 class="card-title">Create email validation function</h3>
            </div>
            <div style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 1rem;">
                Task ID: 20240214-153042 • Started 5 minutes ago
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Workflow visualization
        render_workflow()

        # Progress bar
        st.progress(0.6, text="Code phase in progress...")

    st.divider()

    # Two columns: Logs and Token chart
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📜 Live Logs")

        logs = fetch_api("/api/logs", [])
        if not logs:
            # Mock logs when API is unavailable
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

    with col2:
        st.markdown("### 📊 Token Usage")

        # Token usage by agent
        token_data = tokens.get("by_agent", {"orca": 4200, "design": 3800, "code": 5120, "test": 2300})

        import pandas as pd
        df = pd.DataFrame({
            "Agent": list(token_data.keys()),
            "Tokens": list(token_data.values())
        })

        st.bar_chart(df.set_index("Agent"), color="#6366f1")

        st.markdown("---")
        st.markdown("**Recent Activity**")

        history = tokens.get("history", [])[-5:]
        if history:
            for entry in reversed(history):
                agent = entry.get("agent", "unknown")
                toks = entry.get("tokens", 0)
                st.markdown(f"🔹 **{agent.title()}**: +{toks} tokens")
        else:
            st.markdown("🔹 **Orca**: +320 tokens")
            st.markdown("🔹 **Code**: +480 tokens")
            st.markdown("🔹 **Design**: +250 tokens")


elif page == "agents":
    st.markdown("## 🤖 Agents")
    st.divider()

    agents = fetch_api("/api/agents", [])
    if not agents:
        agents = [
            {"name": "orca", "emoji": "🦑", "role": "Orchestrator", "status": "running", "last_active": "2 min ago", "color": "#6366f1"},
            {"name": "design", "emoji": "🎨", "role": "Architect", "status": "idle", "last_active": "10 min ago", "color": "#8b5cf6"},
            {"name": "code", "emoji": "💻", "role": "Engineer", "status": "completed", "last_active": "5 min ago", "color": "#3b82f6"},
            {"name": "test", "emoji": "🧪", "role": "QA", "status": "error", "last_active": "1 min ago", "color": "#10b981"},
        ]

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
