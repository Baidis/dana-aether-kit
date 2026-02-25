"""Config command - manage API keys."""

import os
from pathlib import Path
from typing import Optional

import typer

from aether.utils import load_env

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
            load_env(env_file)
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

            typer.echo("\nRun Dana with: aether run <file.na>")
        else:
            typer.echo(f"\n=== Configure {provider} ===")
            typer.echo(f"Get key from: {info['url']}")
            typer.echo(f"Set with: aether config -p {provider} -k 'YOUR-KEY-HERE'")
            typer.echo(f"Environment variable: {info['env']}")
            if info.get("models"):
                typer.echo(f"Example models: {', '.join(info['models'][:3])}")
        return

    typer.echo(
        """
=== Dana API Key Configuration ===

Where the key goes: .env file in your project directory

Supported providers:
"""
    )
    for name, info in PROVIDER_INFO.items():
        key = os.getenv(info["env"])
        status = "✓ Set" if key else "✗ Not set"
        typer.echo(f"  {name}: {status}")

    typer.echo(
        """
Quick setup:
  1. Get API key from provider's website
  2. Run: aether config -p <provider> -k 'YOUR-KEY'
  3. Creates/updates .env file automatically

Example with OpenRouter (recommended - cheap, many models):
  aether config -p openrouter -k 'sk-or-v1-...'
"""
    )
