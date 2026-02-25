# Dana-Aether-Kit Improvement Plan

Turn the repo from a working prototype (~70%) into a polished, ready-to-use template repo. Based on current codebase state and Grok's recommendations.

## Current State (Observed in Codebase)

| Area | Status |
|---|---|
| CLI: [init](file:///home/james/Documents/dana-aether-kit/aether/commands/init.py#33-84), [run](file:///home/james/Documents/dana-aether-kit/aether/commands/run.py#12-23), [config](file:///home/james/Documents/dana-aether-kit/aether/commands/config.py#40-127), [coordinate](file:///home/james/Documents/dana-aether-kit/aether/commands/coordinate.py#6-41) | ✅ Working |
| [templates/.env.example](file:///home/james/Documents/dana-aether-kit/templates/.env.example) | ✅ Present |
| [templates/agents/btc_sentiment.na](file:///home/james/Documents/dana-aether-kit/templates/agents/btc_sentiment.na) | ✅ Present |
| [templates/project.dana](file:///home/james/Documents/dana-aether-kit/templates/project.dana) | ⚠️ Hardcodes `btc_sentiment` — not generic |
| [aether/commands/init.py](file:///home/james/Documents/dana-aether-kit/aether/commands/init.py) | ⚠️ Uses inline string templates, ignores `templates/` folder |
| [tests/test_cli.py](file:///home/james/Documents/dana-aether-kit/tests/test_cli.py) | ⚠️ Placeholder only (`pass`) |
| [examples/crypto_signal_pipeline/](file:///home/james/Documents/dana-aether-kit/examples/crypto_signal_pipeline) | ⚠️ Only 2 agents, no chained signal output |
| [scripts/launch_tmux.sh](file:///home/james/Documents/dana-aether-kit/scripts/launch_tmux.sh) | ✅ Exists but undocumented in README |
| GitHub Actions | ❌ Missing |
| `aether agent` command | ❌ Missing |
| Coordinator tmux launch (`--launch` flag) | ❌ Missing |
| File lock system (`aether lock/unlock`) | ❌ Missing |

---

## Phase 1 — Core CLI & Template Fix (High Impact)

> [!NOTE]
> Phases are ordered by priority. Phase 2 (Coordinator) is the biggest new feature addition.

### [aether/commands/init.py](file:///home/james/Documents/dana-aether-kit/aether/commands/init.py) → Copy from `templates/`
Currently [init](file:///home/james/Documents/dana-aether-kit/aether/commands/init.py#33-84) writes files from inline Python strings, completely ignoring the `templates/` directory. Fix it to copy actual template files so edits to templates are reflected in new projects.

**Change**: Use `shutil.copytree` / `shutil.copy2` to copy `templates/` into the new project dir, then do a find-and-replace for `{{project_name}}` placeholder.

#### [MODIFY] [init.py](file:///home/james/Documents/dana-aether-kit/aether/commands/init.py)
- Replace inline string templates with template-file copying logic
- Add `{{project_name}}` / `{{agent_name}}` placeholder substitution
- Keep `--team` and `--env` options

#### [MODIFY] [templates/project.dana](file:///home/james/Documents/dana-aether-kit/templates/project.dana)
- Replace hardcoded `btc_sentiment` import with `{{agent_name}}` placeholder

#### [MODIFY] [templates/agents/btc_sentiment.na](file:///home/james/Documents/dana-aether-kit/templates/agents/btc_sentiment.na)
- Rename to `example.na` (generic) with `{{agent_name}}` placeholder and a richer `reason()` example with context, type hints, and comments

---

### New `aether agent` command
High-value addition: generates a new [.na](file:///home/james/Documents/dana-aether-kit/templates/agents/btc_sentiment.na) file from an intent string.

```bash
aether agent "BTC daily sentiment assessor"
# → creates agents/btc_daily_sentiment_assessor.na
```

#### [NEW] [agent.py](file:///home/james/Documents/dana-aether-kit/aether/commands/agent.py)
- Accept `intent: str` positional arg
- Optional `--output` / `-o` to set output path (default: `agents/<slug>.na`)
- Generate a well-commented [.na](file:///home/james/Documents/dana-aether-kit/templates/agents/btc_sentiment.na) file with `reason()` call seeded from the intent string

#### [MODIFY] [cli.py](file:///home/james/Documents/dana-aether-kit/aether/cli.py)
- Register new `agent` command

---

### `aether run` — default to [project.dana](file:///home/james/Documents/dana-aether-kit/templates/project.dana)
Currently `file: str` is required. Make it optional with a sensible default.

#### [MODIFY] [run.py](file:///home/james/Documents/dana-aether-kit/aether/commands/run.py)
- Change `file: str` → `file: Optional[str] = "project.dana"`
- Print a helpful message if [project.dana](file:///home/james/Documents/dana-aether-kit/templates/project.dana) doesn't exist

---

---

## Phase 2 — Coordinator: Roles, Tmux Orchestration & File Locking ⭐ NEW

### Core Philosophy (Non-Negotiable)

> [!IMPORTANT]
> **The user only ever talks to the Coordinator.** The Coordinator is the single point of contact — it never executes work itself, only orchestrates. It treats every worker agent as a world-class expert and assigns **outcome-focused tasks**, then steps back. It actively listens to agent feedback, synthesises outputs, and keeps the project on track. It never tells experts *how* to do their job.

This avoids the classic anti-pattern of a weak PM over-directing strong specialists. The Coordinator's value is **alignment, conflict resolution, and momentum** — nothing more.

---

### 2a — Project-Defined Agent Roles

Every project defines its own roles. The template ships **starter roles** so you can begin immediately — real projects override or extend these to match their domain.

**Starter roles** (shipped in `templates/.aether/roles.json`):

| Role | Responsibility | Default CLI |
|---|---|---|
| `coordinator` | Orchestration only — never executes | (user-facing, no CLI) |
| `researcher` | Gathers domain knowledge & sources | `gemini` |
| `analyst` | Processes research, finds patterns | `claude` |
| `critic` | Reviews outputs, finds gaps & risks | `claude` |
| `integrator` | Merges outputs into final deliverable | `opencode` |

Projects replace these with domain-specific roles. A web project example:

| Role | Responsibility | CLI |
|---|---|---|
| `coordinator` | Orchestration | (user) |
| `frontend` | UI components & UX | `claude` |
| `backend` | API, DB, services | `opencode` |
| `qa` | Tests & validation | `gemini` |

#### [NEW] `templates/.aether/roles.json`
```json
{
  "coordinator": { "description": "Orchestration only. Assigns outcome-focused tasks, never implementation steps.", "cli": null },
  "researcher":  { "description": "Expert at gathering authoritative domain knowledge.", "cli": "gemini" },
  "analyst":     { "description": "Identifies patterns and actionable insights from research.", "cli": "claude" },
  "critic":      { "description": "Reviews all outputs. Finds gaps, risks, and contradictions.", "cli": "claude" },
  "integrator":  { "description": "Merges agent outputs into the final deliverable.", "cli": "opencode" }
}
```

The Coordinator reads `roles.json` to know which panes to open, which CLIs to assign, and what expertise to expect from each role's output.

#### [MODIFY] [init.py](file:///home/james/Documents/dana-aether-kit/aether/commands/init.py)
- Copy `.aether/roles.json` from templates during `aether init` so every new project has its own editable role config from day one

---

### 2b — Coordinator Tmux Orchestration

The Coordinator reads `roles.json`, opens a tmux session with one named pane per role, seeds each with the right CLI + an **outcome-focused brief**, then parks in the `coordinator` pane so the user can read agent outputs and issue new directives.

**Outcome-focused vs prescriptive (the key distinction):**
- ✅ `"Produce a sentiment score (–1 to +1) and a 2-sentence rationale for BTC/USD as of today."`
- ❌ `"Use VADER, call the /news endpoint, and return JSON with a 'score' key."`

The Coordinator generates the *what*, never the *how*.

**Flow:**
```bash
aether coordinate "Add a dark mode toggle to the app" --launch
```
1. Reads `.aether/roles.json` from the current project
2. Generates **outcome briefs** per role (not implementation steps)
3. Creates `dana-dev` tmux session — one named pane per role
4. Detects available CLIs in `$PATH`; warns if a role's required CLI is missing
5. Dispatches each pane: `<cli-tool> "<outcome brief>"` via `tmux send-keys`
6. User lands in `coordinator` pane to read outputs and reply

#### [NEW] [tmux.py](file:///home/james/Documents/dana-aether-kit/aether/utils/tmux.py)
- `create_session(name)` — create or reuse tmux session
- `create_named_pane(session, role_name)` — one pane per role
- `send_prompt(pane, cli_tool, prompt)` — dispatch via `tmux send-keys`
- `detect_cli_tools()` — `{cli: path}` dict of available tools
- `broadcast(session, message)` — send message to all panes (e.g. "Stand by, pivoting")
- `kill_session(name)` — teardown

#### [MODIFY] [coordinate.py](file:///home/james/Documents/dana-aether-kit/aether/commands/coordinate.py)
- Add `--launch / -l` — activates tmux orchestration (without it: print prompts, unchanged)
- Add `--roles` — path to `roles.json` override (default: `.aether/roles.json`)
- Coordinator generates outcome briefs per role; never generates implementation instructions

#### [MODIFY] [launch_tmux.sh](file:///home/james/Documents/dana-aether-kit/scripts/launch_tmux.sh)
- Accept `$ROLES_JSON` so `aether coordinate --launch` can drive it programmatically
- Keep usable standalone for manual sessions

---

### 2c — File Lock System

Prevents two agents editing the same file simultaneously. Coordinator checks locks before any dispatch and uses lock-release events to trigger **cross-role notifications** without micromanaging the receiving agent.

**Lock format** — `.aether/locks/<encoded-path>.lock` (JSON):
```json
{ "role": "frontend", "cli": "claude", "file": "src/ui/Toggle.tsx", "acquired": "2026-02-24T13:47:00Z" }
```

**Cross-role coordination — no micromanagement:**

| Step | Who | Action |
|---|---|---|
| 1 | frontend (claude) | Acquires lock on `Toggle.tsx`, builds dark mode toggle |
| 2 | frontend (claude) | Releases lock — work complete |
| 3 | Coordinator | Detects release → determines backend may be affected |
| 4 | Coordinator → backend | `"Frontend delivered a dark mode toggle. Ensure theme persistence works correctly with the new state."` |
| 5 | backend (opencode) | Acquires lock on `api/theme.ts`, decides its own approach |

The Coordinator tells backend **what outcome is needed** — never which function to call or how to structure the response.

#### [NEW] [lockfile.py](file:///home/james/Documents/dana-aether-kit/aether/utils/lockfile.py)
- `acquire(filepath, role, cli_tool)` → `True/False`
- `release(filepath)` → deletes lock, returns metadata for coordinator
- `is_locked(filepath)` → lock info or `None`
- `list_locks(project_root)` → all active locks
- Stale lock auto-expiry (configurable, default 30 min)

#### [NEW] [lock.py](file:///home/james/Documents/dana-aether-kit/aether/commands/lock.py)
- `aether lock <file> --role <name>` — acquire
- `aether unlock <file>` — release
- `aether locks` — show all active locks with age and owning role

#### [MODIFY] [cli.py](file:///home/james/Documents/dana-aether-kit/aether/cli.py)
- Register `lock`, `unlock`, `locks` commands

---

## Phase 3 — Tests

#### [MODIFY] [test_cli.py](file:///home/james/Documents/dana-aether-kit/tests/test_cli.py)
Replace the single placeholder with real tests:
- [test_init_creates_project](file:///home/james/Documents/dana-aether-kit/tests/test_cli.py#10-18) — call [init()](file:///home/james/Documents/dana-aether-kit/aether/commands/init.py#33-84) in a temp dir, assert folders + files exist
- `test_init_with_env` — assert [.env.example](file:///home/james/Documents/dana-aether-kit/templates/.env.example) is created with `--env`
- `test_coordinate_output` — call [coordinate()](file:///home/james/Documents/dana-aether-kit/aether/commands/coordinate.py#6-41), capture stdout, assert CLI hints appear
- `test_agent_creates_file` — call the new `agent` command, assert [.na](file:///home/james/Documents/dana-aether-kit/templates/agents/btc_sentiment.na) file is created
- `test_lockfile_acquire_release` — test lock acquire, conflict detection, and release
- `test_lockfile_stale_expiry` — test that stale locks are auto-expired

---

## Phase 4 — Examples

#### [MODIFY] [examples/crypto_signal_pipeline/](file:///home/james/Documents/dana-aether-kit/examples/crypto_signal_pipeline)
Add a third chained agent (`signal_generator.na`) that consumes sentiment + risk outputs and produces a final BUY/SELL/HOLD signal. Update [project.dana](file:///home/james/Documents/dana-aether-kit/templates/project.dana) to chain all three.

#### [NEW] `examples/research_agent/`
A non-crypto example: a simple research agent that uses `reason()` to summarize a topic and save to a markdown file. Shows generality of the kit beyond trading.

---

## Phase 5 — README Polish

#### [MODIFY] [README.md](file:///home/james/Documents/dana-aether-kit/README.md)

Add the following sections:

**Why Dana?** — 2-3 sentences + link to official AI Alliance / Dana docs.

**Scripts** — Document [scripts/launch_tmux.sh](file:///home/james/Documents/dana-aether-kit/scripts/launch_tmux.sh) (parallel agent dev) and [scripts/setup_venv.sh](file:///home/james/Documents/dana-aether-kit/scripts/setup_venv.sh) (one-command bootstrap).

**Troubleshooting** table:

| Symptom | Fix |
|---|---|
| `aether: command not found` | Run `pip install -e .` or `uv pip install -e .` |
| `dana: command not found` | Dana not installed: see Dana docs |
| `reason()` returns None | Check API key is set in `.env` |
| Python version error | Requires Python 3.12+; use `uv venv --python 3.12` |

**Limitations** — Note Dana is early-stage, limited domain packages, LLM API costs apply.

**Use this template** — Note the GitHub "Use this template" button (after enabling in Settings).

---

## Phase 6 — GitHub Actions CI

#### [NEW] [.github/workflows/ci.yml](file:///home/james/Documents/dana-aether-kit/.github/workflows/ci.yml)
```yaml
name: CI
on: [push, pull_request]
jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e ".[dev]"
      - run: ruff check aether/
      - run: pytest tests/ -v
```

---

## Verification Plan

### Automated Tests
```bash
# After changes:
pip install -e ".[dev]"
pytest tests/ -v
ruff check aether/
```

### Manual CLI Flow
```bash
# Fresh test in /tmp
cd /tmp && mkdir test-aether && cd test-aether
aether init "TestBot" --env
ls TestBot/               # → agents/ intents/ workflows/ project.dana .env.example
aether agent "Market analyzer" --output TestBot/agents/market.na
aether run                # → defaults to project.dana

# Coordinator: print mode (no tmux needed)
aether coordinate "Add dark mode toggle"

# Coordinator: launch mode (requires tmux + at least one of claude/opencode/gemini installed)
aether coordinate "Add dark mode toggle" --launch --project ./TestBot
# → tmux session dana-dev opens with named panes

# File locking
aether lock TestBot/agents/market.na --agent frontend
aether locks              # → shows active locks
aether unlock TestBot/agents/market.na
```

### Repo Settings (Manual)
- GitHub → Settings → General → ✅ Template repository
- GitHub → Settings → Topics: [dana](file:///home/james/Documents/dana-aether-kit/templates/project.dana), [agents](file:///home/james/Documents/dana-aether-kit/templates/agents), `llm`, `ai-alliance`, `python`, `scaffolding`
