---
title: Team Knowledge Index
updated: 2026-02-18
summary: Master manifest for ClawCrew shared knowledge discovery.
---

# Team Knowledge Index

## Quick Reference

| Topic | File | Tags | Updated |
|-------|------|------|---------|
| Deployment Procedures | runbooks/deploy.md | deploy, ops, onboarding | 2026-02-18 |
| Agent Workflow | conventions/agent-workflow.md | code, workflow, onboarding | 2026-02-18 |

## Current Project Status

### Active Services

| Service | Port | Command | Status |
|---------|------|---------|--------|
| ClawCrew Dashboard | 3001 (web) / 8002 (API) | `reflex run` | Active |
| MarketVisualizer | 8080 | `PYTHONPATH=../../src python run_web.py` | Active |
| (Reserved) | 8000 | — | Occupied |

### Infrastructure

- **Machine**: Tailscale IP `100.102.200.46`
- **BTC Monitor**: `scripts/btc_dive_monitor.py` (Binance US WebSocket)

## Tag Definitions

- `arch` — Architecture decisions and diagrams
- `api` — API specs, contracts, endpoints
- `deploy` — Deployment procedures
- `code` — Code-related standards
- `test` — Testing patterns and requirements
- `ops` — Operations and incidents
- `onboarding` — Essential context for new tasks
- `workflow` — Process and delegation patterns

## Auto-Include Rules

<!-- OrcaBot uses these to auto-select context -->
- CodeBot tasks: [code, arch, api]
- TestBot tasks: [test, api, code]
- DesignBot tasks: [arch, api]
- Deploy tasks: [deploy, ops]
- All tasks: [onboarding] (if file <10KB)

## Knowledge Locations

```
~/.openclaw/team-knowledge/
├── INDEX.md                 # This file
├── architecture/            # System architecture docs
├── runbooks/                # Operational procedures
│   └── deploy.md            # Deploy checklist
├── conventions/             # Team standards
│   └── agent-workflow.md    # OrcaBot delegation patterns
├── lessons/                 # Post-mortems & learnings
└── context/                 # Sprint/project state
```

## Adding New Knowledge

1. Create document in appropriate directory
2. Add YAML frontmatter with `title`, `tags`, `updated`, `summary`
3. Update this INDEX.md with new entry in Quick Reference table
4. Keep files under 15KB for auto-include efficiency
