# Dana-Aether-Kit

Scaffolding & coordination helpers for [Dana](https://github.com/ai-native-group/dana) agent-native projects and multi-CLI teams (Claude, Gemini, OpenCode, Grok).

## Why Dana?

Dana is an agent-native programming language from the AI Alliance that treats LLM reasoning as a first-class operation via `reason()`. Instead of wiring together API calls manually, you write plain functions and let the runtime handle prompt construction, model selection, and retries. This kit gives you a CLI to scaffold projects, coordinate multi-agent workflows, and manage file locking — so you spend time on agent logic, not boilerplate.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or standard `venv`
- [Dana](https://github.com/ai-native-group/dana) runtime

## Quickstart

```bash
# Clone and setup
git clone https://github.com/yourname/dana-aether-kit my-project
cd my-project

# Create venv with Python 3.12
uv venv --python 3.12
source .venv/bin/activate

# Install
uv pip install -e .

# Configure API key
aether config -p openrouter -k 'sk-or-v1-...'

# Initialize a project
aether init "MyTradingBot" --env
cd MyTradingBot
cp .env.example .env
# Edit .env with your key

# Run
aether run
```

## Commands

| Command | Description |
|---|---|
| `aether init <name>` | Scaffold a new Dana project from templates |
| `aether agent "<intent>"` | Generate a new `.na` agent file from an intent string |
| `aether run [file]` | Run a Dana file with `.env` loaded (defaults to `project.dana`) |
| `aether coordinate "<task>"` | Print outcome-focused briefs per role |
| `aether coordinate "<task>" --launch` | Open a tmux session with one pane per role |
| `aether lock <file> --role <name>` | Acquire a file lock for a role |
| `aether unlock <file>` | Release a file lock |
| `aether locks` | Show all active locks with age and role |
| `aether config -p <provider> -k <key>` | Set API keys |

### Examples

```bash
# Create a project and generate an agent
aether init "ResearchBot" --env
aether agent "Daily tech news summariser" --output ResearchBot/agents/news.na

# Coordinate a task (print mode — no tmux needed)
aether coordinate "Add a dark mode toggle"

# Coordinate with tmux orchestration (requires tmux + CLI tools)
aether coordinate "Add a dark mode toggle" --launch

# File locking for multi-agent workflows
aether lock src/Toggle.tsx --role frontend
aether locks
aether unlock src/Toggle.tsx
```

## Project Structure

After `aether init "MyBot"`:

```
MyBot/
├── project.dana          # Entry point — run with `aether run`
├── agents/
│   └── mybot.na          # Generated agent skeleton
├── intents/              # Optional intent files
├── workflows/            # Optional workflow definitions
├── .aether/
│   └── roles.json        # Editable role configuration
└── .env.example          # API key template (with --env)
```

## Agent Roles

Every project ships a `.aether/roles.json` that the coordinator reads to assign panes and CLIs. Edit it to match your domain:

```json
{
  "coordinator": { "description": "Orchestration only.", "cli": null },
  "researcher":  { "description": "Gathers domain knowledge.", "cli": "gemini" },
  "analyst":     { "description": "Finds patterns and insights.", "cli": "claude" },
  "critic":      { "description": "Reviews outputs for gaps.", "cli": "claude" },
  "integrator":  { "description": "Merges outputs into final deliverable.", "cli": "opencode" }
}
```

## Scripts

| Script | Description |
|---|---|
| `scripts/launch_tmux.sh` | Standalone tmux launcher — reads `.aether/roles.json` and opens one pane per role. Driven programmatically by `aether coordinate --launch`. |
| `scripts/setup_venv.sh` | One-command bootstrap: creates a Python 3.12 venv and installs the package. |

## Examples

| Example | Description |
|---|---|
| `examples/crypto_signal_pipeline/` | Three chained agents: sentiment + risk → BUY/SELL/HOLD signal |
| `examples/research_agent/` | Single agent that researches a topic and saves a markdown summary |

## Supported LLM Providers

- OpenRouter (recommended — broad model coverage, competitive pricing)
- OpenAI
- Anthropic
- Groq
- Google Gemini

Default model: `openrouter:gpt-4o-mini`

## Troubleshooting

| Symptom | Fix |
|---|---|
| `aether: command not found` | Run `pip install -e .` or `uv pip install -e .` |
| `dana: command not found` | Dana not installed — see the Dana docs |
| `reason()` returns `None` | Check your API key is set correctly in `.env` |
| Python version error | Requires Python 3.12+; use `uv venv --python 3.12` |
| tmux session won't open | Install tmux: `sudo apt install tmux` or `brew install tmux` |

## Limitations

- Dana is early-stage; available domain packages are limited
- LLM API costs apply for every `reason()` call
- `aether coordinate --launch` requires tmux and at least one supported CLI tool installed

## Use This Template

Click **"Use this template"** on GitHub (Settings → General → Template repository) to start a fresh project without the git history.

## License

MIT
