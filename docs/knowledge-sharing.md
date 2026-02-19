# ClawCrew Shared Knowledge — Design Specification

## Overview

A file-based convention for sharing knowledge across ClawCrew agents, enabling OrcaBot to automatically discover and inject relevant context when delegating tasks to specialist bots.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ~/.openclaw/team-knowledge/                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ INDEX.md    │  │ architecture│  │ runbooks/   │              │
│  │ (manifest)  │  │ /           │  │             │              │
│  └──────┬──────┘  └─────────────┘  └─────────────┘              │
│         │                                                        │
└─────────┼────────────────────────────────────────────────────────┘
          │
    ┌─────▼─────┐
    │  OrcaBot  │ ── reads INDEX.md, selects relevant docs
    └─────┬─────┘
          │ delegates with: agent-cli.py -c <knowledge-files>
          ▼
    ┌───────────┬───────────┬───────────┐
    │ CodeBot   │ TestBot   │ DesignBot │
    │ (receives │ (receives │ (receives │
    │  context) │  context) │  context) │
    └───────────┴───────────┴───────────┘
```

## Directory Structure

```
~/.openclaw/
├── team-knowledge/              # Shared knowledge base (NEW)
│   ├── INDEX.md                 # Master manifest for discovery
│   ├── architecture/            # System architecture docs
│   │   ├── overview.md
│   │   ├── data-models.md
│   │   └── api-contracts.md
│   ├── runbooks/                # Operational procedures
│   │   ├── deploy.md
│   │   ├── rollback.md
│   │   └── incident-response.md
│   ├── conventions/             # Team standards
│   │   ├── code-style.md
│   │   ├── testing.md
│   │   └── git-workflow.md
│   ├── lessons/                 # Post-mortems & learnings
│   │   ├── 2026-02-18-api-timeout.md
│   │   └── 2026-02-15-db-migration.md
│   └── context/                 # Project-specific context
│       ├── current-sprint.md
│       └── tech-debt.md
│
├── artifacts/                   # Existing: task outputs (unchanged)
│
└── workspaces/
    ├── orca/                    # OrcaBot workspace
    │   └── MEMORY.md            # OrcaBot's personal memory
    ├── code/                    # CodeBot workspace
    ├── test/                    # TestBot workspace
    └── design/                  # DesignBot workspace
```

## File Conventions

### INDEX.md — Master Manifest

The discovery hub. OrcaBot reads this to find relevant knowledge.

```markdown
# Team Knowledge Index

## Quick Reference
| Topic | File | Tags | Updated |
|-------|------|------|---------|
| System Architecture | architecture/overview.md | arch, onboarding | 2026-02-15 |
| API Contracts | architecture/api-contracts.md | api, backend | 2026-02-18 |
| Deploy Process | runbooks/deploy.md | deploy, ops | 2026-02-10 |
| Code Style Guide | conventions/code-style.md | code, style | 2026-02-01 |
| Testing Standards | conventions/testing.md | test, qa | 2026-02-05 |
| Current Sprint | context/current-sprint.md | sprint, tasks | 2026-02-18 |

## Tag Definitions
- `arch` — Architecture decisions and diagrams
- `api` — API specs, contracts, endpoints
- `deploy` — Deployment procedures
- `code` — Code-related standards
- `test` — Testing patterns and requirements
- `ops` — Operations and incidents
- `onboarding` — Essential context for new tasks

## Auto-Include Rules
<!-- OrcaBot uses these to auto-select context -->
- CodeBot tasks: [code, arch, api]
- TestBot tasks: [test, api, code]
- DesignBot tasks: [arch, api]
- Deploy tasks: [deploy, ops]
- All tasks: [onboarding] (if file <10KB)
```

### Knowledge Document Format

Each knowledge doc follows a standard header:

```markdown
---
title: System Architecture Overview
tags: [arch, onboarding]
updated: 2026-02-15
author: OrcaBot
summary: High-level system architecture for the ClawCrew platform.
---

# System Architecture Overview

[Content here...]
```

### Lessons Learned Format

```markdown
---
title: API Timeout Incident
tags: [lessons, api, ops]
date: 2026-02-18
severity: medium
summary: API timeouts caused by missing connection pooling.
---

# API Timeout Incident — 2026-02-18

## What Happened
[Brief description]

## Root Cause
[Technical details]

## Resolution
[What fixed it]

## Lessons
- Always configure connection pool limits
- Add timeout monitoring alerts

## Action Items
- [ ] Add pool config to deploy checklist
- [x] Update runbooks/deploy.md
```

## OrcaBot Knowledge Discovery

### Selection Algorithm

```python
def select_knowledge_for_task(task_description: str, target_agent: str) -> list[str]:
    """
    OrcaBot uses this logic to pick relevant knowledge files.
    Returns list of file paths to pass via -c flag.
    """
    index = parse_index("~/.openclaw/team-knowledge/INDEX.md")
    selected = []
    
    # 1. Auto-include based on target agent
    agent_tags = {
        "code": ["code", "arch", "api"],
        "test": ["test", "api", "code"],
        "design": ["arch", "api"],
    }
    auto_tags = agent_tags.get(target_agent, [])
    
    # 2. Keyword matching from task description
    task_tags = extract_tags_from_task(task_description)
    # e.g., "deploy the API" → ["deploy", "api"]
    
    # 3. Always include onboarding if small
    all_tags = set(auto_tags + task_tags + ["onboarding"])
    
    # 4. Select matching files, cap at 5 to avoid context bloat
    for entry in index.entries:
        if entry.tags & all_tags:
            if get_file_size(entry.file) < 15_000:  # <15KB
                selected.append(entry.file)
        if len(selected) >= 5:
            break
    
    return selected
```

### OrcaBot Delegation Pattern

When OrcaBot delegates a task:

```bash
# OrcaBot internally runs:
./agent-cli.py code \
  -c ~/.openclaw/team-knowledge/architecture/overview.md \
  -c ~/.openclaw/team-knowledge/conventions/code-style.md \
  -c ~/.openclaw/team-knowledge/context/current-sprint.md \
  "Implement the BTC dive monitor from btc-dive-design.md"
```

### ORCA_DELEGATE Helper Script

Add to ClawCrew repo: `scripts/orca-delegate.sh`

```bash
#!/bin/bash
# Usage: orca-delegate.sh <agent> "<task>"
# Automatically includes relevant knowledge files

AGENT=$1
TASK=$2
KNOWLEDGE_DIR="$HOME/.openclaw/team-knowledge"

# Parse INDEX.md and select files (simplified grep-based)
select_knowledge() {
    local agent=$1
    local task=$2
    local files=()
    
    # Agent-specific auto-includes
    case $agent in
        code) tags="code|arch|api" ;;
        test) tags="test|api|code" ;;
        design) tags="arch|api" ;;
        *) tags="onboarding" ;;
    esac
    
    # Find matching files from INDEX.md
    grep -E "\| ($tags)" "$KNOWLEDGE_DIR/INDEX.md" | \
        awk -F'|' '{print $3}' | \
        tr -d ' ' | \
        head -5 | \
        while read -r file; do
            echo "-c $KNOWLEDGE_DIR/$file"
        done
}

CONTEXT_FLAGS=$(select_knowledge "$AGENT" "$TASK")

# Execute delegation
./agent-cli.py "$AGENT" $CONTEXT_FLAGS "$TASK"
```

## Specialist Bot Consumption

### Reading Injected Context

When specialist bots receive context via `-c`, they see it in their system prompt. They should:

1. **Acknowledge context**: Briefly note what knowledge was provided
2. **Apply conventions**: Follow code style, testing standards, etc.
3. **Reference lessons**: Check if any lessons apply to the task
4. **Stay consistent**: Match architectural patterns

### AGENTS.md Addition for Specialists

Add to each specialist's AGENTS.md:

```markdown
## Shared Knowledge

When you receive context files from OrcaBot:

1. **Scan headers** — Check `tags` and `summary` in YAML frontmatter
2. **Apply conventions** — Code style, testing patterns, git workflow
3. **Check lessons** — Look for relevant past incidents
4. **Note gaps** — If you need more context, say so in your response

Knowledge comes from: `~/.openclaw/team-knowledge/`
```

## Knowledge Lifecycle

### Creation Flow

```
1. Lesson learned during task
        ↓
2. Specialist bot notes it in task output
        ↓
3. OrcaBot reviews output, creates/updates knowledge doc
        ↓
4. OrcaBot updates INDEX.md with new entry
```

### OrcaBot Knowledge Maintenance

Add to OrcaBot's HEARTBEAT.md:

```markdown
## Weekly Knowledge Review
- [ ] Check lessons/ for items >30 days old → archive or promote to runbooks
- [ ] Verify INDEX.md entries still exist
- [ ] Check context/current-sprint.md is up to date
```

### Knowledge Promotion Path

```
Task Output → lessons/*.md → runbooks/*.md or conventions/*.md
     ↑              ↑                    ↑
  (raw notes)  (structured)      (permanent reference)
```

## ClawCrew Integration

### Repository Changes

```
~/projects/clawcrew/
├── scripts/
│   ├── agent-cli.py            # Existing
│   ├── orca-delegate.sh        # NEW: Knowledge-aware delegation
│   └── knowledge-init.sh       # NEW: Initialize team-knowledge dir
├── templates/
│   └── team-knowledge/         # NEW: Template structure
│       ├── INDEX.md
│       ├── architecture/.gitkeep
│       ├── runbooks/.gitkeep
│       ├── conventions/.gitkeep
│       ├── lessons/.gitkeep
│       └── context/.gitkeep
└── docs/
    └── knowledge-sharing.md    # NEW: This design doc
```

### knowledge-init.sh

```bash
#!/bin/bash
# Initialize team-knowledge directory from templates

KNOWLEDGE_DIR="$HOME/.openclaw/team-knowledge"
TEMPLATE_DIR="$(dirname "$0")/../templates/team-knowledge"

if [ -d "$KNOWLEDGE_DIR" ]; then
    echo "team-knowledge already exists at $KNOWLEDGE_DIR"
    exit 0
fi

cp -r "$TEMPLATE_DIR" "$KNOWLEDGE_DIR"
echo "Initialized team-knowledge at $KNOWLEDGE_DIR"
```

## Configuration

### Environment Variables (Optional)

```bash
# Override default location
export CLAWCREW_KNOWLEDGE_DIR="$HOME/.openclaw/team-knowledge"

# Max context files to include
export CLAWCREW_MAX_CONTEXT=5

# Max file size for auto-include (bytes)
export CLAWCREW_MAX_CONTEXT_SIZE=15000
```

## Example Workflow

### Scenario: Deploy Task with Lessons

1. **OrcaBot receives**: "Deploy the BTC dive monitor to production"

2. **OrcaBot reads INDEX.md**, selects:
   - `runbooks/deploy.md` (tag: deploy)
   - `architecture/overview.md` (tag: onboarding)
   - `lessons/2026-02-18-api-timeout.md` (tag: deploy, recent)

3. **OrcaBot delegates**:
   ```bash
   ./scripts/orca-delegate.sh code "Deploy BTC dive monitor per runbooks/deploy.md"
   ```

4. **CodeBot receives** context files, sees:
   - Deploy checklist from runbook
   - Connection pooling lesson from incident
   - System architecture for context

5. **CodeBot applies** lessons, avoids past mistakes

6. **CodeBot completes**, notes any new learnings

7. **OrcaBot reviews** output, creates `lessons/2026-02-19-btc-deploy.md` if needed

---

## Summary

| Component | Location | Purpose |
|-----------|----------|---------|
| INDEX.md | team-knowledge/ | Discovery manifest with tags |
| architecture/ | team-knowledge/ | System design docs |
| runbooks/ | team-knowledge/ | Operational procedures |
| conventions/ | team-knowledge/ | Team standards |
| lessons/ | team-knowledge/ | Post-mortems |
| context/ | team-knowledge/ | Current sprint/project state |
| orca-delegate.sh | clawcrew/scripts/ | Auto-selects knowledge for delegation |
| knowledge-init.sh | clawcrew/scripts/ | Initializes directory structure |

**Key Principle**: Knowledge flows from task outputs → lessons → runbooks/conventions. OrcaBot curates; specialists consume.
