# ClawCrew — Multi-Agent Development Team

ClawCrew is a CLI-based multi-agent system for OpenClaw. One orchestrator (OrcaBot) coordinates specialized agents to complete development tasks through a design → code → test workflow.

## Architecture

```
User Task
    │
    ▼
┌─────────────────────────────────────────────────┐
│  OrcaBot (Orchestrator)                         │
│  - Receives task from user                      │
│  - Breaks down into phases                      │
│  - Calls agents via CLI                         │
│  - Reviews outputs (quality gate)               │
│  - Delivers final result                        │
└─────────────────────────────────────────────────┘
    │           │           │
    ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ design  │ │  code   │ │  test   │
│ Agent   │ │ Agent   │ │ Agent   │
└─────────┘ └─────────┘ └─────────┘
    │           │           │
    ▼           ▼           ▼
artifacts/     artifacts/   artifacts/
design.md      main.py      test_main.py
```

## Agent Roster

| Agent | Role | Workspace | Specialty |
|-------|------|-----------|-----------|
| `orca` | Orchestrator | workspace-orca | Task breakdown, coordination, quality review |
| `design` | System Architect | workspace-design | API design, data models, specifications |
| `code` | Software Engineer | workspace-code | Implementation, clean code, type hints |
| `test` | QA Engineer | workspace-test | Unit tests, edge cases, coverage |
| `github` | GitHub Integration | workspace-github | Repo analysis, issues, PRs, GitHub workflows |

## CLI Usage

### Run an Agent

```bash
~/.openclaw/bin/agent-cli.py run -a <agent> -t "<task>" [-o <output>] [-c <context>]
```

**Options:**
| Flag | Long | Description |
|------|------|-------------|
| `-a` | `--agent` | Agent name: `design`, `code`, `test` |
| `-t` | `--task` | Task description |
| `-o` | `--output` | Output file path |
| `-c` | `--context` | Context file to include |
| `-m` | `--model` | Model override (default: claude-sonnet-4-5) |
| `-v` | `--verbose` | Show detailed output |
| `--no-memory` | | Skip memory loading/saving |

### Examples

```bash
# Design an API
~/.openclaw/bin/agent-cli.py run -a design \
  -t "Design a REST API for email validation with regex" \
  -o ~/.openclaw/artifacts/email/design.md

# Implement from design
~/.openclaw/bin/agent-cli.py run -a code \
  -t "Implement the email validator following the design" \
  -c ~/.openclaw/artifacts/email/design.md \
  -o ~/.openclaw/artifacts/email/validator.py

# Write tests
~/.openclaw/bin/agent-cli.py run -a test \
  -t "Write comprehensive tests for the email validator" \
  -c ~/.openclaw/artifacts/email/validator.py \
  -o ~/.openclaw/artifacts/email/test_validator.py
```

### Other Commands

```bash
# List available agents
~/.openclaw/bin/agent-cli.py list-agents

# Show agent's recent memories
~/.openclaw/bin/agent-cli.py show-memory -a design

# Clear agent's memories
~/.openclaw/bin/agent-cli.py clear-memory -a design --all
```

## GitHub Integration

GitHubBot manages all GitHub-related workflows: repository analysis, issues, and pull requests.

### Quick Reference

| Command | Description |
|---------|-------------|
| `summarize-repo` | Analyze repository structure and architecture |
| `list-issues` | List GitHub issues |
| `read-issue` | Read issue details with comments |
| `create-pr` | Create a Pull Request |
| `list-prs` | List Pull Requests |
| `read-pr` | Read PR details with diff |

### Example Workflow

```bash
# 1. Analyze the repo
~/.openclaw/bin/agent-cli.py summarize-repo \
  --url https://github.com/user/repo \
  --task-id task-001

# 2. Read an issue
~/.openclaw/bin/agent-cli.py read-issue -r user/repo -n 42 -o issue.md

# 3. Design → Code → PR
~/.openclaw/bin/agent-cli.py run -a design -t "Design fix" -c issue.md -o design.md
~/.openclaw/bin/agent-cli.py run -a code -t "Implement fix" -c design.md -o fix.py
~/.openclaw/bin/agent-cli.py create-pr -r user/repo -t "Fix #42" -H fix-branch
```

**Full documentation:** See `workspace-github/SOUL.md` for complete command reference.

## Workflow Example

**User Request:** "Create a Python function to validate email addresses"

### Phase 1: Design
```bash
~/.openclaw/bin/agent-cli.py run -a design \
  -t "Design a Python function to validate email addresses using regex. Include: function signature, validation rules, edge cases, error handling." \
  -o ~/.openclaw/artifacts/20240214-120000/design.md
```

**Output:** `design.md` with API spec, validation rules, edge cases

### Phase 2: Code
```bash
~/.openclaw/bin/agent-cli.py run -a code \
  -t "Implement the email validator following the design spec" \
  -c ~/.openclaw/artifacts/20240214-120000/design.md \
  -o ~/.openclaw/artifacts/20240214-120000/email_validator.py
```

**Output:** `email_validator.py` with implementation

### Phase 3: Test
```bash
~/.openclaw/bin/agent-cli.py run -a test \
  -t "Write unit tests for email_validator.py covering normal, edge, and error cases" \
  -c ~/.openclaw/artifacts/20240214-120000/email_validator.py \
  -o ~/.openclaw/artifacts/20240214-120000/test_email_validator.py
```

**Output:** `test_email_validator.py` with pytest tests

### Phase 4: Delivery

OrcaBot reviews all outputs and delivers to user:
- `design.md` — Specification
- `email_validator.py` — Implementation
- `test_email_validator.py` — Tests

---

## Repo Mode Workflow (External Repositories)

When working on an **existing GitHub repository**, use **Repo Mode**. Instead of creating standalone files, agents output **Unified Diff patches** that modify the existing codebase.

### Two Workflow Modes

| Mode | When to Use | Agent Output |
|------|-------------|--------------|
| **Standalone** | New code, no existing repo | Complete files (`main.py`, `test_main.py`) |
| **Repo Mode** | Modifying existing repo | Unified Diff patches (`changes.patch`, `tests.patch`) |

### Repo Mode Example

**User Request:** "Add a caching layer to https://github.com/user/api-server"

#### Step 1: Analyze Repository

```bash
# Clone and analyze (repo saved to artifacts/<task_id>/repo/)
~/.openclaw/bin/agent-cli.py summarize-repo \
  --url https://github.com/user/api-server \
  --task-id 20240215-100000
```

**Output:** `repo_summary.md` with architecture overview

#### Step 2: Read Relevant Files

```bash
# Extract files with line numbers for precise modifications
~/.openclaw/bin/agent-cli.py read-files \
  --repo-path ~/.openclaw/artifacts/20240215-100000/repo \
  --files "src/api.py,src/models.py,tests/test_api.py" \
  -o ~/.openclaw/artifacts/20240215-100000/repo_context.md
```

**Output:** `repo_context.md` with file contents and line numbers

#### Step 3: Design (Repo Mode)

```bash
~/.openclaw/bin/agent-cli.py run -a design \
  -t "Design a caching layer for this codebase. Output in Repo Mode format." \
  -c ~/.openclaw/artifacts/20240215-100000/repo_summary.md \
  -c ~/.openclaw/artifacts/20240215-100000/repo_context.md \
  -o ~/.openclaw/artifacts/20240215-100000/design.md
```

**Output:** `design.md` with modification plan (which files, which lines, what changes)

#### Step 4: Code (Output Diff)

```bash
~/.openclaw/bin/agent-cli.py run -a code \
  -t "Implement the caching layer. Output as unified diff." \
  -c ~/.openclaw/artifacts/20240215-100000/design.md \
  -c ~/.openclaw/artifacts/20240215-100000/repo_context.md \
  -o ~/.openclaw/artifacts/20240215-100000/changes.patch
```

**Output:** `changes.patch` in unified diff format

#### Step 5: Test (Output Diff)

```bash
~/.openclaw/bin/agent-cli.py run -a test \
  -t "Add tests following repo patterns. Output as unified diff." \
  -c ~/.openclaw/artifacts/20240215-100000/changes.patch \
  -c ~/.openclaw/artifacts/20240215-100000/repo_context.md \
  -o ~/.openclaw/artifacts/20240215-100000/tests.patch
```

**Output:** `tests.patch` in unified diff format

#### Step 6: Apply Patches & Create PR

```bash
cd ~/.openclaw/artifacts/20240215-100000/repo

# Verify patches apply cleanly
git apply --check ../changes.patch
git apply --check ../tests.patch

# Apply patches
git apply ../changes.patch
git apply ../tests.patch

# Create branch and commit
git checkout -b feature-caching
git add -A
git commit -m "Add caching layer"

# Create PR
~/.openclaw/bin/agent-cli.py create-pr \
  -r user/api-server \
  -t "Add caching layer" \
  -H feature-caching
```

### Repo Mode Artifacts

```
~/.openclaw/artifacts/<task_id>/
├── repo/                 # Cloned repository
├── repo_summary.md       # Architecture analysis
├── repo_context.md       # File contents with line numbers
├── design.md             # Modification plan
├── changes.patch         # Code changes (unified diff)
└── tests.patch           # Test changes (unified diff)
```

---

## Directory Structure

```
clawcrew/
├── bin/
│   └── agent-cli.py      # CLI tool
├── artifacts/            # Task outputs (gitignored)
│   └── <task-id>/
│       ├── design.md
│       ├── main.py
│       ├── test_main.py
│       └── repo_summary.md
├── workspace-orca/       # Orchestrator
│   ├── SOUL.md          # Personality & instructions
│   ├── ClawCrew.md      # This file
│   └── memory/          # Lessons learned
├── workspace-design/     # Design agent
│   ├── SOUL.md
│   └── memory/
├── workspace-code/       # Code agent
│   ├── SOUL.md
│   └── memory/
├── workspace-test/       # Test agent
│   ├── SOUL.md
│   └── memory/
├── workspace-github/     # GitHub integration
│   ├── SOUL.md
│   └── memory/
├── setup.sh             # Installation script
└── requirements.txt
```

## Memory System

Each agent maintains a memory of lessons learned in `memory/YYYY-MM-DD.md` files.

**Format:**
```markdown
### HH:MM:SS - task_id

**Task:** Brief description
**Output:** File path or stdout
**Lesson:** Key takeaway from this task

---
```

Memories are automatically:
- Loaded when running a task (last 7 days)
- Updated after task completion with a reflection

## Important Notes

### No Spawn!

ClawCrew uses **CLI calls**, not OpenClaw's sessions_spawn:

```bash
# CORRECT - Use CLI
~/.openclaw/bin/agent-cli.py run -a design -t "..."

# WRONG - Don't use spawn (will fail!)
@DesignBot design an API...
sessions_spawn("design", ...)
```

### All Agents are Registered

All 5 agents (orca, design, code, test, github) are registered in OpenClaw. OrcaBot receives Telegram messages and orchestrates the others via CLI.

### Artifacts are Gitignored

The `artifacts/` folder contains task outputs and is not committed to git. Each task creates a subdirectory with its task ID.

---

**ClawCrew** — Design. Code. Test. Deliver.
