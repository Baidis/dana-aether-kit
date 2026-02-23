import typer
import os
import yaml
from pathlib import Path
from typing import List, Optional

try:
    from dotenv import load_dotenv

    def _load_env(path: str):
        load_dotenv(path)
except ImportError:

    def _load_env(path: str):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip("'\"")


app = typer.Typer()


DEFAULT_TEAM = [
    "Grok (lead)",
    "Benjamin (models)",
    "Harper (observability)",
    "Lucas (workflows)",
]

PROVIDER_INFO = {
    "openrouter": {
        "env": "OPENROUTER_API_KEY",
        "url": "https://openrouter.ai/keys",
        "models": ["openrouter:gpt-4o-mini", "openrouter:gpt-4o"],
    },
    "openai": {
        "env": "OPENAI_API_KEY",
        "url": "https://platform.openai.com/api-keys",
        "models": ["openai:gpt-4o", "openai:gpt-4o-mini"],
    },
    "anthropic": {
        "env": "ANTHROPIC_API_KEY",
        "url": "https://console.anthropic.com/settings/keys",
        "models": ["anthropic:claude-3-5-sonnet"],
    },
    "groq": {
        "env": "GROQ_API_KEY",
        "url": "https://console.groq.com/keys",
        "models": ["groq:llama3-70b"],
    },
    "google": {
        "env": "GOOGLE_API_KEY",
        "url": "https://aistudio.google.com/app/apikey",
        "models": ["google:gemini-1.5-pro"],
    },
}


PROJECT_TEMPLATE = """
project "{name}" {{
  team: {team}
  goals: "Build reliable trading / e-commerce agents"
}}
"""


AGENT_TEMPLATE = """
# agents/{name_lower}.na
# Example: Domain-aware agent for crypto trading


def analyze_{name_lower}(symbol: str):
    return reason("Analyze market trends for the given symbol")


def pipeline_example_{name_lower}(input_data):
    return reason("Process input data")
"""


@app.command()
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
    (agent_file := project_dir / "agents" / f"{lower_name}.na").write_text(
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
        typer.echo(f"✓ Created .env.example")

    typer.echo(f"Project '{name}' initialized! cd {name} && dana start")
    typer.echo("Try: agent MarketWatcher in REPL or file")


@app.command()
def coordinate(
    task: str,
    dana_intent: bool = typer.Option(
        False, "--dana-intent", help="Output ready-to-use Dana intent block"
    ),
):
    """Simple coordinator: prints Dana-style intent + suggested CLI prompts"""
    typer.echo(f"Coordinating task: {task}")

    if dana_intent:
        typer.echo("\nDana intent block (paste into .na file):")
        print(f'''intent "{task}":
    # Agent implementation goes here
    # Runtime will plan & execute
    
    def handle_{task.replace(" ", "_").lower()}():
        # Your implementation
        return reason("Process {task}")
''')
        return

    typer.echo("\nDana intent block suggestion:")
    print(f'intent "{task}":\n    // paste implementation here\n')

    typer.echo("Suggested splits for your CLIs:")
    print("- Claude Pro: Lead architecture & complex reasoning")
    print(f"  claude 'Design agent for: {task}'")
    print("- Gemini Pro: Fast code gen & tests")
    print(f"  gemini 'Implement Dana agent for: {task}'")
    print("- OpenCode MiniMax: Bulk / repetitive parts")
    print(f"  opencode --model=minimax 'Generate tests for: {task}'")
    print("- Grok: Creative / edge cases")
    print(f"  grok 'Explore alternatives for: {task}'")


@app.command()
def config(
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        "-p",
        help="Provider to configure (openrouter, openai, anthropic, groq, google)",
    ),
    api_key: Optional[str] = typer.Option(None, "--key", "-k", help="API key to set"),
    show: bool = typer.Option(False, "--show", help="Show current API key status"),
    env_file: Optional[str] = typer.Option(
        None, "--env", "-e", help="Path to .env file to load"
    ),
):
    """Configure LLM API keys for Dana"""
    if env_file:
        if os.path.exists(env_file):
            _load_env(env_file)
            typer.echo(f"✓ Loaded environment from {env_file}")
        else:
            typer.echo(f"Error: File not found: {env_file}")
        return

    if show:
        typer.echo("\n=== API Key Status ===")
        for name, info in PROVIDER_INFO.items():
            key = os.getenv(info["env"])
            if key:
                masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
                typer.echo(f"✓ {name}: {masked}")
            else:
                typer.echo(f"✗ {name}: Not set")
        return

    if provider:
        if provider not in PROVIDER_INFO:
            typer.echo(f"Unknown provider: {provider}")
            typer.echo(f"Available: {', '.join(PROVIDER_INFO.keys())}")
            return
        info = PROVIDER_INFO[provider]
        if api_key:
            os.environ[info["env"]] = api_key

            env_path = Path(".env")
            if env_path.exists():
                with open(env_path, "a") as f:
                    f.write(f"\n{info['env']}={api_key}\n")
                typer.echo(f"✓ Set {info['env']} and appended to .env")
            else:
                with open(env_path, "w") as f:
                    f.write(f"{info['env']}={api_key}\n")
                typer.echo(f"✓ Created .env with {info['env']}")

            typer.echo(f"\nRun Dana with: aether.py run <file.na>")
        else:
            typer.echo(f"\n=== Configure {provider} ===")
            typer.echo(f"Get key from: {info['url']}")
            typer.echo(f"Set with: aether.py config -p {provider} -k 'YOUR-KEY-HERE'")
            typer.echo(f"Environment variable: {info['env']}")
            if info.get("models"):
                typer.echo(f"Example models: {', '.join(info['models'][:3])}")
        return

    typer.echo("""
=== Dana API Key Configuration ===

Where the key goes: .env file in your project directory

Supported providers:
""")
    for name, info in PROVIDER_INFO.items():
        key = os.getenv(info["env"])
        status = "✓ Set" if key else "✗ Not set"
        typer.echo(f"  {name}: {status}")

    typer.echo("""
Quick setup:
  1. Get API key from provider's website
  2. Run: aether.py config -p <provider> -k 'YOUR-KEY'
  3. Creates/updates .env file automatically

Example with OpenRouter (recommended - cheap, many models):
  aether.py config -p openrouter -k 'sk-or-v1-...'
""")


@app.command()
def run(file: str):
    """Run a Dana .na file with .env loaded"""
    env_path = Path(".env")
    if env_path.exists():
        _load_env(".env")
        typer.echo("✓ Loaded .env")
    else:
        typer.echo("⚠ No .env file found")

    import subprocess

    result = subprocess.run(["dana", file], env=os.environ)
    raise typer.Exit(code=result.returncode)


if __name__ == "__main__":
    app()
