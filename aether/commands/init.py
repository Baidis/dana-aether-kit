"""Initialize command - scaffold a new Dana project."""

import typer
from pathlib import Path
from typing import List

DEFAULT_TEAM = [
    "Grok (lead)",
    "Benjamin (models)",
    "Harper (observability)",
    "Lucas (workflows)",
]

PROJECT_TEMPLATE = """project "{name}" {{
  team: {team}
  goals: "Build reliable trading / e-commerce agents"
}}
"""

AGENT_TEMPLATE = """# agents/{name_lower}.na
# Example: Domain-aware agent for crypto trading


def analyze_{name_lower}(symbol: str):
    return reason("Analyze market trends for the given symbol")


def pipeline_example_{name_lower}(input_data):
    return reason("Process input data")
"""


def init(
    name: str,
    team: List[str] = typer.Option(DEFAULT_TEAM, "--team", help="Team members"),
    with_env: bool = typer.Option(False, "--env", help="Create .env.example file"),
):
    """Initialize a new Dana project"""
    project_dir = Path(name)
    project_dir.mkdir(exist_ok=True)

    team_str = "[\n    " + ",\n    ".join(f'"{m}"' for m in team) + "\n  ]"
    (project_dir / "project.dana").write_text(
        PROJECT_TEMPLATE.format(name=name, team=team_str)
    )

    for folder in ["agents", "intents", "workflows"]:
        (project_dir / folder).mkdir(exist_ok=True)

    lower_name = name.replace(" ", "_").lower()
    (project_dir / "agents" / f"{lower_name}.na").write_text(
        AGENT_TEMPLATE.format(name=name.replace(" ", ""), name_lower=lower_name)
    )

    if with_env:
        env_example = Path(project_dir) / ".env.example"
        env_example.write_text("""# Dana API Keys - copy to .env and fill in
# Get keys from provider websites

# OpenRouter (recommended - cheap, many models)
# Get from: https://openrouter.ai/keys
OPENROUTER_API_KEY=

# OpenAI (optional)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=

# Anthropic (optional)
# Get from: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=

# Groq (optional - fast free tier)
# Get from: https://console.groq.com/keys
GROQ_API_KEY=

# Google (optional)
# Get from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=
""")
        typer.echo("✓ Created .env.example")

    typer.echo(f"Project '{name}' initialized! cd {name} && aether run project.dana")
    typer.echo("Or use: dana agents/" + f"{lower_name}.na")
