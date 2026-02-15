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

## Directory Structure

```
clawcrew/
├── bin/
│   └── agent-cli.py      # CLI tool
├── artifacts/            # Task outputs (gitignored)
│   └── <task-id>/
│       ├── design.md
│       ├── main.py
│       └── test_main.py
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

### Only OrcaBot is Registered

In OpenClaw config, only `orca` is registered as an agent. The other agents (design, code, test) are invoked via CLI and don't need registration.

### Artifacts are Gitignored

The `artifacts/` folder contains task outputs and is not committed to git. Each task creates a subdirectory with its task ID.

---

**ClawCrew** — Design. Code. Test. Deliver.
