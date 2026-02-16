"""
ClawCrew Data Fetcher
Real-time log parsing and data aggregation from OpenClaw gateway.
"""

import os
import re
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


# ============================================================
# LOG PARSING PATTERNS
# ============================================================

PATTERNS = {
    # Agent status: [AGENT:orca] status=working
    "agent_status": re.compile(r"\[AGENT:(\w+)\]\s*status=(\w+)", re.IGNORECASE),
    # Token usage: [token:1234] or tokens:1234
    "token": re.compile(r"\[?tokens?[:\s]+(\d+)\]?", re.IGNORECASE),
    # Task info: [TASK:task_id] phase=design
    "task": re.compile(r"\[TASK:([^\]]+)\]\s*phase=(\w+)", re.IGNORECASE),
    # Log level and message
    "log_entry": re.compile(r"(\d{2}:\d{2}:\d{2})\s*\[(\w+)\]\s*(.+)", re.IGNORECASE),
    # Agent output
    "agent_output": re.compile(r"\[(\w+)\]\s*(?:output|result|message):\s*(.+)", re.IGNORECASE),
}

# Agent name mapping
AGENT_MAP = {
    "orca": {"emoji": "🦑", "role": "Orchestrator", "color": "#7B4CFF"},
    "audit": {"emoji": "🔍", "role": "Token Monitor", "color": "#EF4444"},
    "design": {"emoji": "🎨", "role": "Architect", "color": "#A855F7"},
    "code": {"emoji": "💻", "role": "Engineer", "color": "#3B82F6"},
    "test": {"emoji": "🧪", "role": "QA Engineer", "color": "#10B981"},
    "github": {"emoji": "🐙", "role": "PR Manager", "color": "#6366F1"},
}


# ============================================================
# DATA FETCHER CLASS
# ============================================================

class DataFetcher:
    """Fetches and parses data from OpenClaw logs."""

    def __init__(self, log_dir: Optional[str] = None):
        self.log_dir = log_dir or self._find_log_dir()
        self.last_position: Dict[str, int] = {}
        self._cache: Dict[str, Any] = {}
        self._cache_time: float = 0
        self._cache_ttl: float = 2.0  # seconds

    def _find_log_dir(self) -> str:
        """Find the OpenClaw log directory."""
        possible_paths = [
            os.path.expanduser("~/.openclaw/logs"),
            os.path.expanduser("~/projects/clawcrew/logs"),
            "/var/log/openclaw",
            "./logs",
        ]
        for path in possible_paths:
            if os.path.isdir(path):
                return path
        return "./logs"  # Default fallback

    def _read_new_lines(self, filepath: str) -> List[str]:
        """Read new lines from a log file since last read."""
        if not os.path.exists(filepath):
            return []

        last_pos = self.last_position.get(filepath, 0)
        new_lines = []

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(last_pos)
                new_lines = f.readlines()
                self.last_position[filepath] = f.tell()
        except Exception:
            pass

        return new_lines

    def _parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single log line into structured data."""
        line = line.strip()
        if not line:
            return None

        result = {"raw": line, "timestamp": datetime.now().strftime("%H:%M:%S")}

        # Extract timestamp if present
        log_match = PATTERNS["log_entry"].search(line)
        if log_match:
            result["timestamp"] = log_match.group(1)
            result["agent"] = log_match.group(2).lower()
            result["message"] = log_match.group(3)

        # Extract agent status
        status_match = PATTERNS["agent_status"].search(line)
        if status_match:
            result["agent"] = status_match.group(1).lower()
            result["status"] = status_match.group(2).lower()

        # Extract token count
        token_match = PATTERNS["token"].search(line)
        if token_match:
            result["tokens"] = int(token_match.group(1))

        # Extract task info
        task_match = PATTERNS["task"].search(line)
        if task_match:
            result["task_id"] = task_match.group(1)
            result["phase"] = task_match.group(2).lower()

        return result

    def get_agent_data(self) -> List[Dict[str, Any]]:
        """Get current agent statuses and metrics."""
        agents = []

        for agent_id, info in AGENT_MAP.items():
            agent_data = {
                "id": agent_id,
                "name": agent_id.title(),
                "emoji": info["emoji"],
                "role": info["role"],
                "color": info["color"],
                "status": "online",  # Default
                "tokens": 0,
                "tasks_completed": 0,
                "current_task": "",
                "model": "claude-3-sonnet",
                "soul_summary": f"AI agent specialized in {info['role'].lower()} tasks.",
                "recent_outputs": [],
                "token_history": [0] * 10,
            }

            # Try to get real data from logs
            log_file = os.path.join(self.log_dir, f"{agent_id}.log")
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()[-50:]  # Last 50 lines
                        for line in lines:
                            parsed = self._parse_log_line(line)
                            if parsed:
                                if "status" in parsed:
                                    agent_data["status"] = parsed["status"]
                                if "tokens" in parsed:
                                    agent_data["tokens"] += parsed["tokens"]
                except Exception:
                    pass

            agents.append(agent_data)

        return agents

    def get_logs(self, limit: int = 100) -> List[Dict[str, str]]:
        """Get recent log entries."""
        logs = []

        # Try to read from main gateway log
        gateway_log = os.path.join(self.log_dir, "gateway.log")
        if os.path.exists(gateway_log):
            try:
                with open(gateway_log, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[-limit:]
                    for line in lines:
                        parsed = self._parse_log_line(line)
                        if parsed and "message" in parsed:
                            logs.append({
                                "id": str(len(logs)),
                                "timestamp": parsed.get("timestamp", ""),
                                "agent": parsed.get("agent", "system"),
                                "message": parsed.get("message", line.strip()),
                                "level": "info",
                            })
            except Exception:
                pass

        # Return mock data if no real logs
        if not logs:
            logs = self._get_mock_logs()

        return logs[-limit:]

    def get_token_stats(self) -> Dict[str, Any]:
        """Get token usage statistics."""
        total = 0
        by_agent = {}

        for agent_id in AGENT_MAP.keys():
            agent_tokens = 0
            log_file = os.path.join(self.log_dir, f"{agent_id}.log")
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            match = PATTERNS["token"].search(line)
                            if match:
                                agent_tokens += int(match.group(1))
                except Exception:
                    pass

            by_agent[agent_id.title()] = agent_tokens
            total += agent_tokens

        # Use mock data if no real tokens found
        if total == 0:
            return self._get_mock_token_stats()

        return {
            "total": total,
            "by_agent": by_agent,
            "budget": 100000,
            "budget_used_percent": min(100, (total / 100000) * 100),
        }

    def get_task_status(self) -> Dict[str, Any]:
        """Get current task pipeline status."""
        # Try to read from task log
        task_log = os.path.join(self.log_dir, "tasks.log")
        if os.path.exists(task_log):
            try:
                with open(task_log, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    # Parse last task info
                    for line in reversed(lines):
                        parsed = self._parse_log_line(line)
                        if parsed and "task_id" in parsed:
                            return {
                                "id": parsed["task_id"],
                                "phase": parsed.get("phase", "unknown"),
                                "progress": self._phase_to_progress(parsed.get("phase", "")),
                            }
            except Exception:
                pass

        # Return mock data
        return self._get_mock_task_status()

    def _phase_to_progress(self, phase: str) -> int:
        """Convert phase name to progress percentage."""
        phases = {
            "orchestrate": 20,
            "design": 40,
            "code": 60,
            "test": 80,
            "deploy": 100,
        }
        return phases.get(phase.lower(), 0)

    def _get_mock_logs(self) -> List[Dict[str, str]]:
        """Return mock log data when real logs unavailable."""
        return [
            {"id": "1", "timestamp": "15:33:10", "agent": "code", "message": "Adding type hints and docstrings", "level": "info"},
            {"id": "2", "timestamp": "15:32:45", "agent": "code", "message": "Implementing email validation with regex", "level": "info"},
            {"id": "3", "timestamp": "15:32:18", "agent": "orca", "message": "Quality gate passed → Calling CodeBot", "level": "success"},
            {"id": "4", "timestamp": "15:32:15", "agent": "design", "message": "Output saved to artifacts/design.md", "level": "info"},
            {"id": "5", "timestamp": "15:31:02", "agent": "design", "message": "Analyzing requirements...", "level": "info"},
            {"id": "6", "timestamp": "15:30:45", "agent": "orca", "message": "Calling DesignBot...", "level": "info"},
            {"id": "7", "timestamp": "15:30:42", "agent": "orca", "message": "Received task: Create email validation", "level": "info"},
            {"id": "8", "timestamp": "15:30:00", "agent": "audit", "message": "Token budget check: OK", "level": "success"},
        ]

    def _get_mock_token_stats(self) -> Dict[str, Any]:
        """Return mock token statistics."""
        return {
            "total": 18420,
            "by_agent": {
                "Orca": 4200,
                "Audit": 980,
                "Design": 3800,
                "Code": 5120,
                "Test": 2300,
                "GitHub": 2020,
            },
            "budget": 100000,
            "budget_used_percent": 18.4,
        }

    def _get_mock_task_status(self) -> Dict[str, Any]:
        """Return mock task status."""
        return {
            "id": "20240214-153042",
            "name": "Create email validation function",
            "phase": "code",
            "progress": 60,
            "steps": [
                {"name": "Orchestrate", "status": "completed", "duration": "0.8s", "tokens": 320},
                {"name": "Design", "status": "completed", "duration": "2.4s", "tokens": 850},
                {"name": "Code", "status": "active", "duration": "--", "tokens": 1240},
                {"name": "Test", "status": "pending", "duration": "--", "tokens": 0},
                {"name": "Deploy", "status": "pending", "duration": "--", "tokens": 0},
            ],
        }

    async def fetch_all(self) -> Dict[str, Any]:
        """Fetch all dashboard data."""
        now = asyncio.get_event_loop().time()

        # Return cached data if fresh
        if now - self._cache_time < self._cache_ttl and self._cache:
            return self._cache

        # Fetch fresh data
        data = {
            "agents": self.get_agent_data(),
            "logs": self.get_logs(100),
            "tokens": self.get_token_stats(),
            "task": self.get_task_status(),
            "last_update": datetime.now().strftime("%H:%M:%S"),
        }

        self._cache = data
        self._cache_time = now

        return data


# Global instance
data_fetcher = DataFetcher()
