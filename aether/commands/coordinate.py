"""Coordinate command - task splitting and tmux orchestration for multi-CLI teams."""

import json
import re
from pathlib import Path
from typing import Optional

import typer

from aether.utils import tmux as _tmux


_DEFAULT_ROLES_PATH = Path(".aether") / "roles.json"


def _load_roles(roles_path: Path) -> dict:
    if not roles_path.exists():
        typer.echo(f"⚠ roles.json not found at {roles_path}  (using built-in defaults)")
        return {
            "researcher": {"description": "Gathers domain knowledge.", "cli": "gemini"},
            "analyst": {"description": "Finds patterns and insights.", "cli": "claude"},
            "critic": {"description": "Reviews outputs for gaps.", "cli": "claude"},
            "integrator": {"description": "Merges outputs into final deliverable.", "cli": "opencode"},
        }
    return json.loads(roles_path.read_text())


def _outcome_brief(role: str, description: str, task: str) -> str:
    """Generate an outcome-focused brief for a role — never prescriptive."""
    return (
        f"[{role.upper()}] Task: {task}\n\n"
        f"Your role: {description}\n\n"
        f"Deliver a clear, concrete outcome relevant to your expertise. "
        f"Do not wait for instructions on *how* — you are the expert. "
        f"Return your findings when ready."
    )


def coordinate(
    task: str,
    launch: bool = typer.Option(
        False, "--launch", "-l", help="Open a tmux session with one pane per role"
    ),
    roles: Optional[Path] = typer.Option(
        None, "--roles", help="Path to roles.json override (default: .aether/roles.json)"
    ),
    dana_intent: bool = typer.Option(
        False, "--dana-intent", help="Output a ready-to-use Dana intent block"
    ),
):
    """Coordinate a task across multi-CLI agent teams"""
    roles_path = roles or _DEFAULT_ROLES_PATH
    all_roles = _load_roles(roles_path)

    # Strip coordinator from worker roles
    worker_roles = {k: v for k, v in all_roles.items() if k != "coordinator"}

    if dana_intent:
        typer.echo("\nDana intent block (paste into .na file):")
        print(
            f'intent "{task}":\n'
            f'    def handle_{re.sub(r"[^a-z0-9]+", "_", task.lower()).strip("_")}():\n'
            f'        return reason("Process {task}")\n'
        )
        return

    typer.echo(f"\nCoordinating: {task}\n")

    briefs: dict[str, str] = {}
    for role, meta in worker_roles.items():
        brief = _outcome_brief(role, meta.get("description", ""), task)
        briefs[role] = brief

    if not launch:
        # Print mode — just show what would be dispatched
        for role, meta in worker_roles.items():
            cli = meta.get("cli") or "(no CLI configured)"
            typer.echo(f"── {role} [{cli}]")
            typer.echo(f"   {briefs[role].splitlines()[0]}")
        typer.echo(
            "\nTip: add --launch to open a tmux session with one pane per role."
        )
        return

    # ------------------------------------------------------------------
    # Launch mode — tmux orchestration
    # ------------------------------------------------------------------
    if not _tmux.tmux_available():
        typer.echo("✗ tmux not found in $PATH — cannot use --launch")
        raise typer.Exit(1)

    available_clis = _tmux.detect_cli_tools()
    session = "dana-dev"

    typer.echo(f"Launching tmux session '{session}' …")
    _tmux.create_session(session)

    for i, (role, meta) in enumerate(worker_roles.items()):
        cli = meta.get("cli")
        pane = _tmux.create_named_pane(session, role, first=(i == 0))

        if cli and cli in available_clis:
            _tmux.send_prompt(pane, cli, briefs[role])
        elif cli:
            typer.echo(f"  ⚠ CLI '{cli}' not found for role '{role}' — pane opened but idle")
        else:
            typer.echo(f"  ℹ Role '{role}' has no CLI configured — pane opened but idle")

    # Open coordinator pane last so the user lands there
    _tmux.create_named_pane(session, "coordinator")
    typer.echo(f"\n✓ Session '{session}' ready — {len(worker_roles)} worker panes launched")
    typer.echo("  Attaching to coordinator pane …")

    _tmux.attach_session(session)
