"""Run command - execute Dana files with .env loaded."""

import os
import subprocess
from pathlib import Path

import typer

from aether.utils import load_env


def run(file: str):
    """Run a Dana .na file with .env loaded"""
    env_path = Path(".env")
    if env_path.exists():
        load_env(".env")
        typer.echo("✓ Loaded .env")
    else:
        typer.echo("⚠ No .env file found")

    result = subprocess.run(["dana", file], env=os.environ)
    raise typer.Exit(code=result.returncode)
