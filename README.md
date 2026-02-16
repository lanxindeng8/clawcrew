# ClawCrew.md

> 🦞 A framework for building collaborative AI agent teams on OpenClaw

---

## 🎯 What is ClawCrew?

ClawCrew is a **framework** for creating multi-agent teams that collaborate on tasks. Instead of one AI doing everything, you define specialized agents with focused roles, and an orchestrator coordinates their work.

**Each agent evolves independently.** You can train and tune each agent's capabilities separately — refine the designer's taste, sharpen the coder's style, improve the tester's coverage. They grow as individuals.

**You're the manager.** In Telegram (or any IM), you talk to the orchestrator and watch every agent work in real-time. Jump in anytime — give feedback, correct course, or let them run. Define team workflows and standards, then step back and let them deliver. It's like running a team or a company, except your employees are AI.

**The magic:** Each agent's capabilities are defined by its workspace — `SOUL.md`, `AGENTS.md`, skills, and tools. Change the workspace, change the agent.

**Watch them work in real-time — right in your chat.**

---

## 💡 Core Concept

```
┌──────────────────────────────────────────────────────────────┐
│                     ClawCrew Framework                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   Orchestrator Agent (workspace_orca/)                       │
│   ├── SOUL.md       → Personality & rules                    │
│   ├── AGENTS.md     → Behavior guidelines                    │
│   ├── ClawCrew.md   → Team structure & roles  ⭐             │
│   └── skills/       → Available capabilities                 │
│                                                              │
│         │ spawns                                             │
│         ▼                                                    │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│   │   Agent A    │  │   Agent B    │  │   Agent C    │      │
│   │ workspace_A/ │  │ workspace_B/ │  │ workspace_C/ │      │
│   └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│   Each agent = unique workspace = unique capabilities        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

> 📄 **[ClawCrew.md](https://clawcrew.md)** — The team definition file lives in the orchestrator's workspace.  
> It describes all roles, workflows, and standards for your agent team.  

**Key insight:** The framework doesn't define what agents do — **workspaces do**.

---

## 🎨 Example Teams

### 1. Software Dev Team

```
🦑 OrcaBot (Orchestrator)
    ├── 🎨 DesignBot  → API design, types, specs
    ├── 💻 CodeBot    → Implementation
    └── 🧪 TestBot    → Testing, coverage
```

**Use case:** Automated code generation with quality gates

---

### 2. Research Team

```
📚 ResearchLead (Orchestrator)
    ├── 🔍 SearchBot   → Web research, data gathering
    ├── 📊 AnalystBot  → Data analysis, insights
    └── ✍️ WriterBot   → Report writing, summaries
```

**Use case:** Deep research with structured output

---

### 3. Content Team

```
🎬 ContentLead (Orchestrator)
    ├── 💡 IdeaBot      → Brainstorming, concepts
    ├── ✏️ DraftBot     → Writing first drafts
    ├── 🔍 EditorBot    → Review, polish, fact-check
    └── 📊 AnalyzerBot  → Monitor engagement (clicks, replies, shares)
```

**Use case:** Blog posts, marketing copy, documentation with performance tracking

---

### 4. Customer Support Team

```
🎯 SupportLead (Orchestrator)
    ├── 🔍 TriageBot   → Categorize, prioritize
    ├── 💬 ReplyBot    → Draft responses
    └── 📈 EscalateBot → Complex issue handling
```

**Use case:** Automated support ticket handling

---

## 👥 Software Dev Team (Full Example)

This example shows a complete software development crew.

### Team Structure

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                    🦑 OrcaBot                           │
│                   (Orchestrator)                        │
│                                                         │
│    "I break down tasks, delegate work, and ensure      │
│     quality at every step."                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │           │   │           │   │           │
    │ 🎨 Design │   │ 💻 Code   │   │ 🧪 Test   │
    │    Bot    │   │    Bot    │   │    Bot    │
    │           │   │           │   │           │
    └───────────┘   └───────────┘   └───────────┘
```

### Agent Roles

| Agent | Role | Deliverables |
|-------|------|--------------|
| 🦑 **OrcaBot** | Orchestrator | Task breakdown, quality gates, final delivery |
| 🎨 **DesignBot** | Architect | API specs, types, edge cases |
| 💻 **CodeBot** | Engineer | Implementation, docstrings |
| 🧪 **TestBot** | QA | Unit tests, coverage report |

### Workflow

```
USER REQUEST
     │
     ▼
┌─────────────────────┐
│  PHASE 1: DESIGN    │  OrcaBot → spawns → DesignBot
│  Output: API spec   │  OrcaBot reviews → ✅
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  PHASE 2: CODE      │  OrcaBot → spawns → CodeBot
│  Output: module.py  │  OrcaBot reviews → ✅
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  PHASE 3: TEST      │  OrcaBot → spawns → TestBot
│  Output: tests.py   │  OrcaBot reviews → ✅
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  FINAL DELIVERY 🚀  │
│  • Code + Tests     │
│  • 100% coverage    │
│  • Documentation    │
└─────────────────────┘
```

---

## 🚀 Getting Started

> **Prerequisites:** OpenClaw already installed and configured.  
> See [OpenClaw docs](https://docs.openclaw.ai) for installation.

### Step 1: Create Telegram Bot

Only need **1 bot** for all agents.

1. Message [@BotFather](https://t.me/BotFather) → `/newbot`
2. Get your bot token
3. **Important:** Disable privacy mode
   - `/mybots` → Select your bot → Bot Settings → Group Privacy → **Turn off**
   - This lets the bot see all messages in groups

### Step 2: Create Telegram Group

1. Create a group called "OpenClaw Dev" (or any name)
2. Add your bot to the group
3. Get the group's `chat_id`

### Step 3: Clone & Configure

```bash
git clone https://github.com/lanxindeng8/clawcrew
cd clawcrew
```

### Step 4: Set Up Workspaces

```bash
./setup.sh
```

### Step 5: Start the Crew

```bash
openclaw gateway restart
```

### Step 6: Send a Task

In your Telegram group:
```
Create a Python module to calculate distance between two points
```

---

## 🛠 Build Your Own Team

### 1. Define Your Orchestrator

Create `workspace-orchestrator/SOUL.md`:
```markdown
# SOUL.md

You are the team lead. When you receive a task:
1. Break it into phases
2. Spawn the right agent for each phase
3. Review each deliverable
4. Deliver final results
```

### 2. Define Specialized Agents

Create `workspace-agent-a/SOUL.md`:
```markdown
# SOUL.md

You are a specialist in [SKILL].
When given a task:
1. Focus only on your expertise
2. Deliver high-quality output
3. Report back to the orchestrator
```

### 3. Configure Routing

Set up OpenClaw to route to your orchestrator.

### 4. Run Your Team

Send a task and watch your custom team collaborate!

---

## 🔗 GitHub Integration

ClawCrew includes built-in GitHub integration via the `agent-cli.py` tool, powered by the `github_utils.py` module.

### Repository Analysis

Analyze any GitHub repository or local directory to understand its architecture before development tasks.

```bash
# Analyze a public GitHub repo
./bin/agent-cli.py summarize-repo --url https://github.com/pallets/flask

# Analyze a specific branch
./bin/agent-cli.py summarize-repo -u https://github.com/user/repo -b develop

# Analyze a private repo (with PAT)
./bin/agent-cli.py summarize-repo -u https://github.com/user/private-repo --pat ghp_xxx

# Or use environment variable
export GITHUB_PAT=ghp_xxx
./bin/agent-cli.py summarize-repo -u https://github.com/user/private-repo

# Analyze local directory
./bin/agent-cli.py summarize-repo --path ~/projects/my-app
```

**What it analyzes:**
- 📁 File tree structure (depth-limited, skips noise like `node_modules`, `.git`)
- 📄 Documentation (README, CONTRIBUTING, ARCHITECTURE)
- ⚙️ Config files (package.json, pyproject.toml, Cargo.toml, etc.)
- 🚀 Entry points (main.py, index.js, main.go, etc.)
- 🔧 Core source files (from src/, lib/, pkg/, app/)

### Issue Management

Read and list GitHub issues to use as context for development tasks.

```bash
# List open issues
./bin/agent-cli.py list-issues -r user/repo

# Filter by label
./bin/agent-cli.py list-issues -r user/repo -l bug

# Read a specific issue with comments
./bin/agent-cli.py read-issue -r user/repo -n 123 --comments -o issue.md
```

### Pull Request Workflow

Create, list, and read PRs directly from the CLI.

```bash
# Create a PR
./bin/agent-cli.py create-pr -r user/repo -t "Add feature X" -H feature-branch

# List open PRs
./bin/agent-cli.py list-prs -r user/repo

# Read PR with diff
./bin/agent-cli.py read-pr -r user/repo -n 42 --diff -o pr.md
```

### `github_utils.py` Module

The underlying utility module provides:

| Function | Description |
|----------|-------------|
| `get_github_token()` | Get PAT from `--pat` flag, `GITHUB_PAT`, or `GH_TOKEN` env |
| `parse_github_url()` | Parse HTTPS/SSH GitHub URLs into (owner, repo, clone_url) |
| `clone_repository()` | Shallow clone with branch and PAT support |
| `generate_file_tree()` | ASCII tree representation with depth limit |
| `find_key_files()` | Locate docs, configs, entry points, core files |
| `read_file_safe()` | Read files with size limits (100KB default) |
| `build_repo_context()` | Assemble full context for LLM analysis |

**Configuration constants:**
- `MAX_FILE_SIZE` = 100KB per file
- `MAX_TOTAL_CONTENT` = 500KB total context
- `MAX_TREE_DEPTH` = 4 levels
- `MAX_FILES_PER_CATEGORY` = 5 files

### Full Workflow Example

```bash
# 1. Analyze the target repo
./bin/agent-cli.py summarize-repo \
  --url https://github.com/user/repo \
  --task-id task-001

# 2. Read the issue to implement
./bin/agent-cli.py read-issue -r user/repo -n 42 -o ~/.openclaw/artifacts/task-001/issue.md

# 3. Design the solution using repo + issue context
./bin/agent-cli.py run -a design \
  -t "Design a fix for this issue" \
  -c ~/.openclaw/artifacts/task-001/repo_summary.md \
  -c ~/.openclaw/artifacts/task-001/issue.md \
  -o ~/.openclaw/artifacts/task-001/design.md

# 4. Implement the fix
./bin/agent-cli.py run -a code \
  -t "Implement the fix following the design" \
  -c ~/.openclaw/artifacts/task-001/design.md \
  -o ~/.openclaw/artifacts/task-001/fix.py

# 5. Create a PR
./bin/agent-cli.py create-pr \
  -r user/repo \
  -t "Fix #42: Issue title" \
  -f ~/.openclaw/artifacts/task-001/design.md \
  -H fix-branch
```

---

## 🔮 Roadmap

### Current
- [x] Multi-agent orchestration pattern
- [x] Software Dev Team example
- [x] Quality gates between phases
- [x] Real-time chat visibility

### Framework Core (Next)

**Team Management**
- [ ] Easy onboarding — add new agents with simple config
- [ ] Role templates — pre-defined SOUL.md for common roles
- [ ] Hot reload — update agent capabilities without restart

**Team Collaboration**
- [ ] Shared context — team members access common knowledge base
- [ ] Internal handoffs — structured data passing between agents
- [ ] Team memory — persistent learnings across sessions

**Team Operations**
- [ ] Workflow editor — define pipelines visually
- [ ] Progress tracking — see task status across agents
- [ ] Quality metrics — success rates, iteration counts, costs

### Multi-Team (Future)

- [ ] Team-to-team communication
- [ ] Shared resource pools
- [ ] Cross-team orchestration
- [ ] Organization-level policies

### Software Dev Team (Priority)

Since this is the most common use case for developers:

**GitHub Integration**
- [x] Repo onboarding — Orca reads new repo, summarizes architecture, shares with team
- [x] Issue → Task — GitHub issues automatically become team tasks
- [x] PR workflow — CodeBot creates PR, TestBot validates, Orca merges
- [ ] Code review — team reviews external PRs

**Dev Workflow**
- [ ] Multi-file projects — coordinate changes across files
- [ ] Dependency awareness — understand imports and relationships
- [ ] Incremental builds — work on existing codebases
- [ ] CI/CD hooks — trigger builds, handle failures

---

## 📄 License

MIT License — See [LICENSE](LICENSE)

---

## 🔗 Links

- **Website:** [clawcrew.md](https://clawcrew.md)
- **GitHub:** [github.com/lanxindeng8/clawcrew](https://github.com/lanxindeng8/clawcrew)
- **OpenClaw:** [openclaw.ai](https://openclaw.ai)
- **Discord:** [discord.gg/clawd](https://discord.gg/clawd)

---

*Built with 🦞 OpenClaw — Your personal AI assistant*
