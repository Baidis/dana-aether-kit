"""Run command - execute Dana files with .env loaded."""

import os
import subprocess
from pathlib import Path
from typing import Optional

import typer

from aether.utils import load_env


def run(
    file: Optional[str] = typer.Argument(
        None, help="Dana file to run (default: project.dana)"
    ),
):
    """Run a Dana .na or .dana file with .env loaded"""
    target = file or "project.dana"

    if not Path(target).exists():
        typer.echo(f"✗ File not found: {target}")
        if target == "project.dana":
            typer.echo("  Run `aether init <name>` first, or pass a file path.")
        raise typer.Exit(1)

    env_path = Path(".env")
    if env_path.exists():
        load_env(".env")
        typer.echo("✓ Loaded .env")
    else:
        typer.echo("⚠ No .env file found")

    result = subprocess.run(["dana", target], env=os.environ)
    raise typer.Exit(code=result.returncode)
