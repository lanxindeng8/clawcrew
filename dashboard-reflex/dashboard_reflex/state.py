"""
ClawCrew Dashboard State Management
Centralized application state with dark mode, drawer, filters, and auto-refresh.
"""

import reflex as rx
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import asyncio


# ============================================================
# DATA MODELS (using pydantic.BaseModel)
# ============================================================

class Agent(BaseModel):
    """Agent data model with detailed information."""
    id: str
    name: str
    emoji: str
    role: str
    status: str  # online, working, away, offline, error
    model: str
    tokens: int
    tasks_completed: int
    current_task: str = ""
    color: str = "#7B4CFF"
    soul_summary: str = ""
    recent_outputs: List[str] = Field(default_factory=list)
    token_history: List[int] = Field(default_factory=list)  # Last 10 token readings


class LogEntry(BaseModel):
    """Log entry with agent and level."""
    id: str
    timestamp: str
    agent: str
    message: str
    level: str = "info"  # info, warning, error, success


class TaskStep(BaseModel):
    """Task pipeline step."""
    name: str
    agent: str
    emoji: str
    status: str  # pending, active, completed, error
    duration: str = ""
    tokens_used: int = 0


# ============================================================
# APPLICATION STATE
# ============================================================

class DashboardState(rx.State):
    """Main dashboard application state."""

    # === Theme & UI ===
    dark_mode: bool = True
    sidebar_collapsed: bool = False
    current_page: str = "home"

    # === Agent Drawer ===
    drawer_open: bool = False
    selected_agent_id: str = ""

    # === Stats ===
    total_tasks: int = 47
    active_tasks: int = 3
    total_tokens: int = 18420
    success_rate: float = 94.2

    # === Agents ===
    agents: List[Agent] = [
        Agent(
            id="orca",
            name="Orca",
            emoji="🦑",
            role="Orchestrator",
            status="working",
            model="claude-3-opus",
            tokens=4200,
            tasks_completed=12,
            current_task="Coordinating email validation task",
            color="#7B4CFF",
            soul_summary="Central orchestrator that coordinates all agent activities. Manages task distribution, quality gates, and workflow optimization.",
            recent_outputs=[
                "Quality gate passed → Calling CodeBot",
                "Task dispatched to DesignBot",
                "Workflow optimization complete",
                "Agent health check: All systems nominal",
                "Token budget allocated: 5000",
            ],
            token_history=[380, 420, 510, 480, 390, 450, 520, 480, 410, 420],
        ),
        Agent(
            id="audit",
            name="Audit",
            emoji="🔍",
            role="Token & Loop Monitor",
            status="online",
            model="claude-3-haiku",
            tokens=980,
            tasks_completed=156,
            current_task="Monitoring agent runtime",
            color="#EF4444",
            soul_summary="Monitors token consumption and detects infinite loops or stuck agents. Provides real-time alerts and cost optimization suggestions.",
            recent_outputs=[
                "Token budget: 82% remaining",
                "No anomalies detected",
                "Code agent efficiency: 94%",
                "Loop detection: Clear",
                "Cost optimization: -12% this session",
            ],
            token_history=[80, 95, 88, 92, 85, 90, 98, 87, 91, 98],
        ),
        Agent(
            id="design",
            name="Design",
            emoji="🎨",
            role="Architect",
            status="online",
            model="claude-3-sonnet",
            tokens=3800,
            tasks_completed=8,
            current_task="",
            color="#A855F7",
            soul_summary="System architect that designs solutions, creates specifications, and ensures architectural consistency across the codebase.",
            recent_outputs=[
                "API specification complete",
                "Database schema designed",
                "Component architecture documented",
                "Design review passed",
                "Technical debt assessment: Low",
            ],
            token_history=[320, 380, 450, 420, 380, 400, 350, 380, 410, 380],
        ),
        Agent(
            id="code",
            name="Code",
            emoji="💻",
            role="Engineer",
            status="working",
            model="claude-3-opus",
            tokens=5120,
            tasks_completed=15,
            current_task="Implementing email validation",
            color="#3B82F6",
            soul_summary="Primary code implementation agent. Writes clean, tested, and documented code following best practices.",
            recent_outputs=[
                "Email validation regex implemented",
                "Unit tests added: 12 passing",
                "Type hints added to module",
                "Documentation updated",
                "Code review suggestions applied",
            ],
            token_history=[480, 520, 580, 510, 490, 550, 520, 480, 510, 512],
        ),
        Agent(
            id="test",
            name="Test",
            emoji="🧪",
            role="QA Engineer",
            status="online",
            model="claude-3-sonnet",
            tokens=2300,
            tasks_completed=6,
            current_task="",
            color="#10B981",
            soul_summary="Quality assurance specialist that writes and runs tests, identifies edge cases, and ensures code reliability.",
            recent_outputs=[
                "Test coverage: 87%",
                "All integration tests passing",
                "Edge cases documented",
                "Performance benchmarks updated",
                "Security scan: No issues",
            ],
            token_history=[200, 220, 250, 230, 210, 240, 220, 230, 250, 230],
        ),
        Agent(
            id="github",
            name="GitHub",
            emoji="🐙",
            role="PR & Issue Manager",
            status="online",
            model="claude-3-haiku",
            tokens=1850,
            tasks_completed=24,
            current_task="",
            color="#6366F1",
            soul_summary="Manages GitHub operations including PR creation, issue tracking, code reviews, and repository maintenance.",
            recent_outputs=[
                "PR #142 created successfully",
                "Issue #89 closed",
                "Code review completed",
                "Branch merged to main",
                "Release notes generated",
            ],
            token_history=[150, 180, 200, 170, 190, 185, 175, 195, 180, 185],
        ),
    ]

    # === Task Pipeline ===
    task_steps: List[TaskStep] = [
        TaskStep(name="Orchestrate", agent="Orca", emoji="🦑", status="completed", duration="0.8s", tokens_used=320),
        TaskStep(name="Design", agent="Design", emoji="🎨", status="completed", duration="2.4s", tokens_used=850),
        TaskStep(name="Code", agent="Code", emoji="💻", status="active", duration="--", tokens_used=1240),
        TaskStep(name="Test", agent="Test", emoji="🧪", status="pending", duration="--", tokens_used=0),
        TaskStep(name="Deploy", agent="GitHub", emoji="🐙", status="pending", duration="--", tokens_used=0),
    ]

    # === Logs ===
    logs: List[LogEntry] = [
        LogEntry(id="1", timestamp="15:33:10", agent="code", message="Adding type hints and docstrings", level="info"),
        LogEntry(id="2", timestamp="15:32:45", agent="code", message="Implementing email validation with regex", level="info"),
        LogEntry(id="3", timestamp="15:32:18", agent="orca", message="Quality gate passed → Calling CodeBot", level="success"),
        LogEntry(id="4", timestamp="15:32:15", agent="design", message="Output saved to artifacts/design.md", level="info"),
        LogEntry(id="5", timestamp="15:31:02", agent="design", message="Analyzing requirements...", level="info"),
        LogEntry(id="6", timestamp="15:30:45", agent="orca", message="Calling DesignBot...", level="info"),
        LogEntry(id="7", timestamp="15:30:42", agent="orca", message="Received task: Create email validation", level="info"),
        LogEntry(id="8", timestamp="15:30:00", agent="audit", message="Token budget check: OK", level="success"),
    ]

    # === Log Filters ===
    log_filter_agents: List[str] = []  # Empty = show all
    log_search_query: str = ""
    log_auto_scroll: bool = True

    # === Task Input ===
    new_task_input: str = ""
    sending_task: bool = False

    # === Auto Refresh ===
    auto_refresh: bool = True
    last_refresh: str = ""
    refresh_interval: int = 5  # seconds

    # === Loading States ===
    is_loading: bool = False

    # ============================================================
    # COMPUTED PROPERTIES
    # ============================================================

    @rx.var
    def selected_agent(self) -> Optional[Agent]:
        """Get the currently selected agent for drawer."""
        for agent in self.agents:
            if agent.id == self.selected_agent_id:
                return agent
        return None

    @rx.var
    def filtered_logs(self) -> List[LogEntry]:
        """Get logs filtered by agent and search query."""
        result = self.logs

        # Filter by agents
        if self.log_filter_agents:
            result = [log for log in result if log.agent in self.log_filter_agents]

        # Filter by search query
        if self.log_search_query:
            query = self.log_search_query.lower()
            result = [log for log in result if query in log.message.lower()]

        return result

    @rx.var
    def active_agents_count(self) -> int:
        """Count agents currently working."""
        return len([a for a in self.agents if a.status == "working"])

    @rx.var
    def total_tokens_formatted(self) -> str:
        """Format total tokens with K suffix."""
        if self.total_tokens >= 1000:
            return f"{self.total_tokens / 1000:.1f}K"
        return str(self.total_tokens)

    @rx.var
    def current_task_progress(self) -> int:
        """Calculate current task progress percentage."""
        completed = len([s for s in self.task_steps if s.status == "completed"])
        total = len(self.task_steps)
        return int((completed / total) * 100) if total > 0 else 0

    # ============================================================
    # EVENT HANDLERS
    # ============================================================

    def toggle_dark_mode(self):
        """Toggle dark/light mode."""
        self.dark_mode = not self.dark_mode

    def toggle_sidebar(self):
        """Toggle sidebar collapse state."""
        self.sidebar_collapsed = not self.sidebar_collapsed

    def navigate(self, page: str):
        """Navigate to a page."""
        self.current_page = page

    def open_agent_drawer(self, agent_id: str):
        """Open drawer with agent details."""
        self.selected_agent_id = agent_id
        self.drawer_open = True

    def close_drawer(self):
        """Close the agent drawer."""
        self.drawer_open = False
        self.selected_agent_id = ""

    def toggle_log_filter(self, agent: str):
        """Toggle agent in log filter."""
        if agent in self.log_filter_agents:
            self.log_filter_agents = [a for a in self.log_filter_agents if a != agent]
        else:
            self.log_filter_agents = [*self.log_filter_agents, agent]

    def set_log_search(self, query: str):
        """Set log search query."""
        self.log_search_query = query

    def toggle_auto_scroll(self):
        """Toggle log auto-scroll."""
        self.log_auto_scroll = not self.log_auto_scroll

    def set_new_task(self, value: str):
        """Update new task input."""
        self.new_task_input = value

    async def send_task(self):
        """Send a new task to Orca."""
        if not self.new_task_input.strip():
            return

        self.sending_task = True

        # Add log entry
        new_log = LogEntry(
            id=str(len(self.logs) + 1),
            timestamp=datetime.now().strftime("%H:%M:%S"),
            agent="user",
            message=f"New task submitted: {self.new_task_input}",
            level="info",
        )
        self.logs = [new_log, *self.logs]

        # Simulate API call
        await asyncio.sleep(0.5)

        # Add Orca response
        orca_log = LogEntry(
            id=str(len(self.logs) + 1),
            timestamp=datetime.now().strftime("%H:%M:%S"),
            agent="orca",
            message=f"Received task: {self.new_task_input}",
            level="success",
        )
        self.logs = [orca_log, *self.logs]

        self.new_task_input = ""
        self.sending_task = False
        self.total_tasks += 1
        self.active_tasks += 1

    def toggle_auto_refresh(self):
        """Toggle auto-refresh."""
        self.auto_refresh = not self.auto_refresh

    async def refresh_data(self):
        """Refresh dashboard data."""
        self.is_loading = True
        await asyncio.sleep(0.3)  # Simulate API call
        self.last_refresh = datetime.now().strftime("%H:%M:%S")
        self.is_loading = False

    def clear_log_filters(self):
        """Clear all log filters."""
        self.log_filter_agents = []
        self.log_search_query = ""
