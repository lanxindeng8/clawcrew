"""Validation utilities for ClawCrew."""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class ValidationResult:
    """Result of a validation check."""
    valid: bool
    errors: List[str]
    warnings: List[str]

    @property
    def ok(self) -> bool:
        return self.valid and len(self.errors) == 0


@dataclass
class PatchValidationResult(ValidationResult):
    """Result of patch validation."""
    affected_files: List[str] = None

    def __post_init__(self):
        if self.affected_files is None:
            self.affected_files = []


@dataclass
class OutputValidationResult(ValidationResult):
    """Result of agent output validation."""
    content: Optional[str] = None


def validate_patch(patch_content: str, repo_path: Path) -> PatchValidationResult:
    """
    Validate a unified diff patch before applying.

    Checks:
    1. Patch syntax is valid
    2. Target files exist (or will be created)
    3. Context lines match
    4. Line numbers are within file bounds

    Args:
        patch_content: The unified diff patch content
        repo_path: Path to the repository root

    Returns:
        PatchValidationResult with validation status
    """
    errors = []
    warnings = []
    affected_files = []

    # Extract affected files from patch headers
    for line in patch_content.splitlines():
        if line.startswith("+++ ") or line.startswith("--- "):
            file_path = line[4:].split("\t")[0]
            if file_path not in ("a/dev/null", "b/dev/null", "/dev/null"):
                # Remove a/ or b/ prefix
                if file_path.startswith(("a/", "b/")):
                    file_path = file_path[2:]
                if file_path not in affected_files:
                    affected_files.append(file_path)

    # Check if files exist (for modifications)
    for file_path in affected_files:
        full_path = repo_path / file_path
        if not full_path.exists():
            warnings.append(f"File will be created: {file_path}")

    # Validate patch syntax using git apply --check
    try:
        result = subprocess.run(
            ["git", "apply", "--check", "-"],
            input=patch_content,
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=30,
        )

        if result.returncode != 0:
            stderr = result.stderr.strip()
            for line in stderr.splitlines():
                if "patch does not apply" in line:
                    errors.append(f"Patch does not apply cleanly: {line}")
                elif "No such file" in line:
                    errors.append(f"Target file not found: {line}")
                elif "corrupt patch" in line:
                    errors.append(f"Corrupt patch syntax: {line}")
                elif "error:" in line.lower():
                    errors.append(line)

    except subprocess.TimeoutExpired:
        errors.append("Patch validation timed out")
    except FileNotFoundError:
        errors.append("git command not found")
    except Exception as e:
        errors.append(f"Validation error: {e}")

    return PatchValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        affected_files=affected_files,
    )


def preview_patch(patch_content: str, repo_path: Path) -> str:
    """
    Generate a preview of what the patch will change.

    Args:
        patch_content: The unified diff patch content
        repo_path: Path to the repository root

    Returns:
        Human-readable diff statistics
    """
    try:
        result = subprocess.run(
            ["git", "apply", "--stat", "-"],
            input=patch_content,
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=30,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Could not preview patch: {e}"


def validate_agent_output(
    raw_output: str,
    agent_type: str,
) -> OutputValidationResult:
    """
    Validate and extract agent output based on expected format.

    Expected format:
        ---OUTPUT---
        <actual output>
        ---END OUTPUT---

    Args:
        raw_output: Raw response from agent
        agent_type: Type of agent (design, code, test, etc.)

    Returns:
        OutputValidationResult with validation status and extracted content
    """
    errors = []
    warnings = []
    content = None

    # Check for output markers
    if "---OUTPUT---" not in raw_output:
        warnings.append("Missing ---OUTPUT--- marker (using full response)")
    if "---END OUTPUT---" not in raw_output:
        warnings.append("Missing ---END OUTPUT--- marker (using full response)")

    # Extract content between markers
    match = re.search(
        r'---OUTPUT---\s*\n(.*?)\n---END OUTPUT---',
        raw_output,
        re.DOTALL,
    )

    if match:
        content = match.group(1).strip()
    else:
        # Fall back to full response if no markers
        content = raw_output.strip()

    # Agent-specific validation
    if content:
        agent_errors = _validate_agent_specific(content, agent_type)
        errors.extend(agent_errors)

    return OutputValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        content=content,
    )


def _validate_agent_specific(content: str, agent_type: str) -> List[str]:
    """Validate content based on agent type."""
    errors = []

    if agent_type == "design":
        # Design agent should have structured sections
        if "##" not in content:
            errors.append("Design output should have markdown sections")

    elif agent_type == "code":
        # Code agent should have code blocks
        if "```" not in content:
            errors.append("Code output should contain code blocks")

    elif agent_type == "test":
        # Test agent should have test functions
        if "def test_" not in content and "test_" not in content.lower():
            errors.append("Test output should contain test functions")

    return errors
