# ClawCrew Updates

Recent feature additions and improvements.

---

## 2025-02 — Phase 4: Installation & Developer Experience

### PyPI Package Distribution

ClawCrew is now a proper Python package that can be installed via pip.

```bash
pip install clawcrew
```

**New Project Structure:**
```
src/clawcrew/
├── cli/           # Command-line interface
│   ├── main.py    # Entry point
│   ├── run.py     # Run single agent
│   ├── chain.py   # Chain multiple agents
│   ├── init.py    # Setup wizard
│   ├── system.py  # start/stop/status
│   └── github.py  # GitHub subcommands
├── core/          # Core functionality
│   ├── config.py  # Configuration management
│   ├── memory.py  # Agent memory system
│   └── llm.py     # OpenClaw LLM calls
└── utils/         # Utilities
    ├── github.py  # GitHub helpers
    ├── errors.py  # Error handling
    └── validators.py  # Validation utilities
```

---

### New CLI Commands

| Command | Description |
|---------|-------------|
| `clawcrew init` | Interactive setup wizard (Telegram, GitHub config) |
| `clawcrew start` | Start the OpenClaw gateway |
| `clawcrew stop` | Stop the gateway |
| `clawcrew status` | Show system and agent status |
| `clawcrew run <agent> -t "task"` | Run a single agent |
| `clawcrew chain "task" design code test` | Chain multiple agents with auto context |
| `clawcrew agents` | List available agents |
| `clawcrew show-memory -a <agent>` | Show agent memories |
| `clawcrew github analyze --url <repo>` | Analyze GitHub repo |
| `clawcrew github issues -r owner/repo` | List GitHub issues |

---

### Chain Command

New `chain` command runs multiple agents in sequence with **automatic context passing**:

```bash
clawcrew chain "Create a REST API for user management" design code test
```

**What happens:**
1. **DesignBot** creates API specification
2. **CodeBot** receives design output as context, implements code
3. **TestBot** receives design + code as context, writes tests
4. All outputs saved to `~/.openclaw/artifacts/<task_id>/`

---

### One-Click Installation

New install script for quick setup:

```bash
curl -sSL https://raw.githubusercontent.com/lanxindeng8/clawcrew/main/install.sh | bash
```

**Features:**
- Auto-detects OS (macOS/Linux)
- Installs dependencies (Python, pip, jq)
- Installs ClawCrew via pip
- Runs interactive configuration wizard

---

### Docker Deployment

Full Docker support for containerized deployment:

```bash
# Quick start
cp .env.example .env    # Configure Telegram credentials
docker-compose up -d    # Start ClawCrew

# Check logs
docker-compose logs -f
```

**Files:**
- `Dockerfile` — Python 3.11, jq, git, gh CLI
- `docker-compose.yml` — Volume mounts, health checks
- `.env.example` — Configuration template

---

### Error Handling & Validation

New utilities for better error handling:

```python
from clawcrew.utils import (
    ClawCrewError,
    validate_patch,
    validate_agent_output,
)

# Validate patch before applying
result = validate_patch(patch_content, repo_path)
if not result.valid:
    print(result.errors)

# Validate agent output format
result = validate_agent_output(response, "code")
if result.warnings:
    print(result.warnings)
```

---

### Homebrew Formula (macOS)

Install via Homebrew (when tap is published):

```bash
brew tap lanxindeng8/clawcrew
brew install clawcrew
```

---

### Dashboard Improvements

Multiple dashboard fixes and redesigns:
- Reflex-based dashboard with Linear/Vercel-style UI
- Real-time OpenClaw session log parsing
- Two-column agent card layout
- Glassmorphism design elements

---

## Key Files Changed

| File | Changes |
|------|---------|
| `pyproject.toml` | NEW — Package configuration |
| `src/clawcrew/**` | NEW — Package source code (18 files) |
| `install.sh` | NEW — One-click install script |
| `Dockerfile` | NEW — Docker image definition |
| `docker-compose.yml` | NEW — Container orchestration |
| `.env.example` | NEW — Environment template |
| `homebrew/clawcrew.rb` | NEW — Homebrew formula |

---

## 2024-02 — Phase 3: Repo-Aware Development

### Repo Mode Workflow

Added support for working with **external GitHub repositories**. Instead of outputting standalone files, agents now output **Unified Diff patches** that can be applied to existing codebases.

**Two Workflow Modes:**

| Mode | When | Output |
|------|------|--------|
| **Standalone** | No external repo | Complete files (`main.py`, `test_main.py`) |
| **Repo Mode** | Modifying existing repo | Unified Diff patches (`changes.patch`, `tests.patch`) |

**New Commands:**

```bash
# Analyze a repository (clone saved to artifacts)
~/.openclaw/bin/agent-cli.py summarize-repo \
  --url https://github.com/user/repo \
  --task-id <task_id>

# Read specific files with line numbers for precise modifications
~/.openclaw/bin/agent-cli.py read-files \
  --repo-path ~/.openclaw/artifacts/<task_id>/repo \
  --files "src/api.py,tests/test_api.py" \
  -o ~/.openclaw/artifacts/<task_id>/repo_context.md
```

**Agent Updates:**
- `DesignBot` — Outputs modification plans with exact file locations and line numbers
- `CodeBot` — Outputs Unified Diff patches (`git apply` compatible)
- `TestBot` — Outputs test patches following repo's existing test patterns

**Documentation:**
- [SOUL.md](workspace-orca/SOUL.md) — Repo Mode Workflow section
- [ClawCrew.md](workspace-orca/ClawCrew.md) — Repo Mode Workflow example

---

### Multi-Model Design Workflow

Users can now request designs from **multiple AI models** and have them synthesized into a final specification.

**Example User Request:**
```
Design a dashboard UI using grok and gemini, synthesize with gpt-4
```

**How It Works:**

1. **Parallel Design** — OrcaBot calls design agent with each specified model
2. **Synthesis** — Results combined using the synthesizer model
3. **Standard Flow** — Synthesized design used for code/test phases

**Supported Model IDs:**

| Provider | Model ID |
|----------|----------|
| Anthropic | `anthropic/claude-sonnet-4-5`, `anthropic/claude-opus-4-5` |
| OpenAI | `openai/gpt-4`, `openai/gpt-4-turbo` |
| Google | `google/gemini-pro`, `google/gemini-1.5-pro` |
| xAI | `xai/grok-2` |

**Usage:**
```bash
# OrcaBot automatically orchestrates:
~/.openclaw/bin/agent-cli.py run -a design -t "..." -m "xai/grok-2" -o design-grok.md
~/.openclaw/bin/agent-cli.py run -a design -t "..." -m "google/gemini-pro" -o design-gemini.md
~/.openclaw/bin/agent-cli.py run -a design -t "Synthesize..." -m "openai/gpt-4" \
  -c design-grok.md -c design-gemini.md -o design-final.md
```

**Documentation:**
- [SOUL.md](workspace-orca/SOUL.md) — Multi-Model Design Workflow section
- [ClawCrew.md](workspace-orca/ClawCrew.md) — Multi-Model Design Workflow section

---

### `read-files` Command

New CLI command to read repository files with line numbers, essential for Repo Mode.

```bash
~/.openclaw/bin/agent-cli.py read-files \
  --repo-path ./repo \
  --files "src/api.py,src/models.py,tests/test_api.py" \
  -o repo_context.md
```

**Features:**
- Line numbers for precise modification references
- Syntax highlighting hints (language detection)
- Multiple file support (comma-separated)
- Missing file handling with clear status

**Output Format:**
```markdown
## File: src/api.py

**Lines:** 150

```python
  1: from typing import Optional
  2:
  3: def existing_function():
...
```
```

---

## Key Files Changed

| File | Changes |
|------|---------|
| `bin/agent-cli.py` | Added `read-files` command, auto-keep clone with task_id |
| `workspace-orca/SOUL.md` | Repo Mode Workflow, Multi-Model Design Workflow |
| `workspace-orca/ClawCrew.md` | Repo Mode example, Multi-Model example, Model IDs table |
| `workspace-design/SOUL.md` | Repo Mode Design output format |
| `workspace-code/SOUL.md` | Unified Diff output format |
| `workspace-test/SOUL.md` | Repo Mode Testing, match repo patterns |

---

## Coming Soon

- [ ] `ensemble` command for automated multi-model workflows
- [ ] Workflow configuration files (YAML-based pipelines)
- [ ] Model performance tracking and comparison

---

*ClawCrew — Design. Code. Test. Deliver.*
