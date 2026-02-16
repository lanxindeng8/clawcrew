"""LLM interaction via OpenClaw."""

import subprocess
from typing import Optional


class LLMError(Exception):
    """Error calling LLM."""
    pass


def call_llm(message: str, agent_name: str = "main", timeout: int = 300) -> str:
    """
    Call LLM via OpenClaw agent command.

    Uses `openclaw agent --agent <name>` which:
    - Loads the agent's SOUL.md from its workspace
    - Uses the configured Anthropic OAuth
    - Returns the agent's response

    Args:
        message: The message/task to send
        agent_name: OpenClaw agent ID (orca, design, code, test, or main)
        timeout: Timeout in seconds

    Returns:
        LLM response content

    Raises:
        LLMError: On subprocess errors
    """
    try:
        result = subprocess.run(
            [
                "openclaw", "agent",
                "--agent", agent_name,
                "--local",
                "--message", message,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            raise LLMError(f"LLM call failed: {result.stderr}")

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        raise LLMError("LLM call timed out")
    except FileNotFoundError:
        raise LLMError("openclaw command not found. Please install OpenClaw first.")


def extract_output(response: str) -> str:
    """
    Extract content between ---OUTPUT--- and ---END OUTPUT--- markers.

    If markers not found, returns the full response.

    Args:
        response: LLM response text

    Returns:
        Extracted output or full response
    """
    if "---OUTPUT---" in response and "---END OUTPUT---" in response:
        return response.split("---OUTPUT---")[1].split("---END OUTPUT---")[0].strip()
    return response
