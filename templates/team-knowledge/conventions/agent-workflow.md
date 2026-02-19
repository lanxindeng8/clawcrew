---
title: Agent Workflow Conventions
tags: [code, workflow, onboarding]
updated: 2026-02-18
author: OrcaBot
summary: OrcaBot delegation patterns and specialist bot conventions for ClawCrew.
---

# Agent Workflow Conventions

## Overview

OrcaBot orchestrates tasks by delegating to specialist bots. This document defines the conventions for effective delegation and knowledge sharing.

## Agent Roles

| Agent | Role | Expertise |
|-------|------|-----------|
| OrcaBot | Orchestrator | Task decomposition, delegation, knowledge curation |
| CodeBot | Implementer | Writing production code, following specs |
| TestBot | Quality | Writing tests, validation, edge cases |
| DesignBot | Architect | System design, API contracts, data models |

## Delegation Patterns

### Standard Delegation

```bash
# Using knowledge-aware delegation (preferred)
./scripts/orca-delegate.sh <agent> "<task>"

# Direct delegation (no auto-context)
./scripts/agent-cli.py <agent> "<task>"

# With explicit context files
./scripts/agent-cli.py <agent> -c path/to/context.md "<task>"
```

### Context Selection

OrcaBot automatically includes relevant knowledge based on:

1. **Target agent** — CodeBot gets code/arch/api tags
2. **Task keywords** — "deploy" triggers deploy/ops tags
3. **Onboarding** — Always included if <10KB

### Task Format

When delegating, provide:

```
1. Clear objective (what to achieve)
2. Reference to design doc or spec (if applicable)
3. Constraints or requirements
4. Expected output format
```

Example:
```
"Implement the BTC dive monitor from btc-dive-design.md. 
Output a single-file Python script with all dependencies."
```

## Specialist Bot Conventions

### Receiving Context

When you receive context files from OrcaBot:

1. **Scan headers** — Check `tags` and `summary` in YAML frontmatter
2. **Apply conventions** — Code style, testing patterns, architecture
3. **Check lessons** — Look for relevant past incidents in lessons/
4. **Note gaps** — If you need more context, say so in your response

### Output Format

Wrap deliverables in markers for easy extraction:

```
---OUTPUT---
[Your complete output here]
---END OUTPUT---
```

### Reporting Lessons

If you learn something during a task:

1. Note it in your response under "Lessons Learned"
2. OrcaBot will decide whether to create a knowledge doc
3. Don't create knowledge docs directly — that's OrcaBot's job

## Knowledge Flow

```
Task Request → OrcaBot (selects context) → Specialist Bot
                                                ↓
                                          Task Output
                                                ↓
OrcaBot reviews ← Lessons noted ← Deliverable + Notes
       ↓
Creates/updates knowledge docs if needed
```

## File Locations

| Type | Location |
|------|----------|
| Shared knowledge | `~/.openclaw/team-knowledge/` |
| Task artifacts | `~/.openclaw/artifacts/` |
| Agent workspaces | `~/.openclaw/workspaces/<agent>/` |
| ClawCrew repo | `~/projects/clawcrew/` |

## Best Practices

### For OrcaBot

- Decompose complex tasks before delegating
- Include relevant context, but cap at 5 files
- Review specialist output for lessons to capture
- Keep INDEX.md updated

### For Specialists

- Follow the spec exactly; note deviations
- Apply conventions from context files
- Report blockers early
- Keep outputs self-contained

### For Everyone

- Knowledge flows up: raw → lessons → runbooks
- Small files (<15KB) get auto-included
- Tag documents appropriately for discovery
- Update timestamps when editing
