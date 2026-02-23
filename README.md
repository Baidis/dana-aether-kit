# Dana-Aether-Kit

Scaffolding & coordination helpers for Dana agent-native projects + multi-CLI teams (Claude, Gemini, OpenCode, Grok).

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or venv
- Dana package

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

# Initialize project
aether init "MyTradingBot" --env
cd MyTradingBot
cp .env.example .env
# Edit .env with your key

# Run
aether run project.dana
```

## Commands

- `aether init <name>` - Create new Dana project
- `aether coordinate <task>` - Task splitting for multi-agent teams
- `aether config -p <provider> -k <key>` - Set API keys
- `aether run <file.na>` - Run Dana file with .env loaded

## Supported LLM Providers

- OpenRouter (recommended)
- OpenAI
- Anthropic
- Groq
- Google Gemini

## Dana Config Notes

- Default model: `openrouter:gpt-4o-mini`
- Fallback: local Ollama

## Extending

Add new commands in `aether/commands/`. See CONTRIBUTING.md for details.

## License

MIT
