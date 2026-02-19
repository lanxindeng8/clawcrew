# ClawCrew — Quick Reference

> **Primary documentation is in `SOUL.md`** — this file contains supplementary info only.

## Architecture

```
User → OrcaBot → design/code/test agents → artifacts/
```

## Supported Models

| Provider | Model ID |
|----------|----------|
| Anthropic | `anthropic/claude-sonnet-4-5`, `anthropic/claude-opus-4-5` |
| OpenAI | `openai/gpt-4`, `openai/gpt-4-turbo` |
| Google | `google/gemini-pro`, `google/gemini-1.5-pro` |
| xAI | `xai/grok-2` |

## Multi-Model Design (Optional)

When user requests multiple perspectives:

```bash
# Parallel design with different models
~/.openclaw/bin/agent-cli.py run -a design -t "Design X" -m "xai/grok-2" -o design-grok.md
~/.openclaw/bin/agent-cli.py run -a design -t "Design X" -m "google/gemini-pro" -o design-gemini.md

# Synthesize
~/.openclaw/bin/agent-cli.py run -a design -t "Synthesize these designs" \
  -c design-grok.md -c design-gemini.md -o design-final.md
```

## Memory System

Each agent has persistent memory in `workspace-<agent>/memory/YYYY-MM-DD.md`.
- Auto-loaded: last 7 days
- Auto-saved: after each task

```bash
~/.openclaw/bin/agent-cli.py show-memory -a code   # View
~/.openclaw/bin/agent-cli.py clear-memory -a code  # Clear
```

## Directory Layout

```
~/.openclaw/
├── bin/agent-cli.py
├── artifacts/<task-id>/
├── team-knowledge/repos/<repo>.md
├── workspace-orca/
├── workspace-design/
├── workspace-code/
└── workspace-test/
```

---
*See SOUL.md for complete CLI reference and workflows.*
