"""Initialize command - scaffold a new Dana project."""

import shutil
from pathlib import Path
from typing import List

import typer

# Directory containing the shipped templates (sibling of this package)
_TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"

DEFAULT_TEAM = [
    "Grok (lead)",
    "Benjamin (models)",
    "Harper (observability)",
    "Lucas (workflows)",
]


def _apply_placeholders(text: str, project_name: str, agent_name: str) -> str:
    return (
        text.replace("{{project_name}}", project_name)
        .replace("{{agent_name}}", agent_name)
    )


def _slug(name: str) -> str:
    """Convert a human name to a snake_case slug."""
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def init(
    name: str,
    team: List[str] = typer.Option(DEFAULT_TEAM, "--team", help="Team members"),
    with_env: bool = typer.Option(False, "--env", help="Copy .env.example"),
):
    """Initialize a new Dana project from templates"""
    project_dir = Path(name)
    project_dir.mkdir(exist_ok=True)

    agent_name = _slug(name)
    project_name = name

    # ------------------------------------------------------------------
    # Directories
    # ------------------------------------------------------------------
    for folder in ("agents", "intents", "workflows"):
        (project_dir / folder).mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    # project.dana — copy template, substitute placeholders
    # ------------------------------------------------------------------
    src_project = _TEMPLATES_DIR / "project.dana"
    dst_project = project_dir / "project.dana"
    raw = src_project.read_text()
    dst_project.write_text(_apply_placeholders(raw, project_name, agent_name))

    # ------------------------------------------------------------------
    # agents/<slug>.na — copy example.na template
    # ------------------------------------------------------------------
    src_agent = _TEMPLATES_DIR / "agents" / "example.na"
    dst_agent = project_dir / "agents" / f"{agent_name}.na"
    raw = src_agent.read_text()
    dst_agent.write_text(_apply_placeholders(raw, project_name, agent_name))

    # ------------------------------------------------------------------
    # .aether/ — roles config
    # ------------------------------------------------------------------
    aether_dir = project_dir / ".aether"
    aether_dir.mkdir(exist_ok=True)
    shutil.copy2(_TEMPLATES_DIR / ".aether" / "roles.json", aether_dir / "roles.json")

    # ------------------------------------------------------------------
    # .env.example (optional)
    # ------------------------------------------------------------------
    if with_env:
        src_env = _TEMPLATES_DIR / ".env.example"
        shutil.copy2(src_env, project_dir / ".env.example")
        typer.echo("✓ Created .env.example")

    typer.echo(f"✓ Project '{name}' initialized in {project_dir}/")
    typer.echo(f"  cd {name} && aether run")
