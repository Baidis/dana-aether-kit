# Contributing to Aether

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone the repo
git clone https://github.com/yourname/dana-aether-kit
cd dana-aether-kit

# Setup venv
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Adding New Commands

1. Create a new file in `aether/commands/`
2. Implement your command function
3. Import and register in `aether/cli.py`

## Adding Agent Templates

Add templates to `templates/agents/` directory.

## Code Style

- Use Ruff for linting
- Type hints preferred
- Docstrings for public functions

## Testing

```bash
pytest tests/
```

## Reporting Issues

Please include:
- Python version
- Dana version
- Steps to reproduce
- Error messages
