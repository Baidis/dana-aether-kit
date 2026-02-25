"""Lock commands - file locking for multi-agent coordination."""

from typing import Optional

import typer

from aether.utils import lockfile


def lock(
    file: str,
    role: str = typer.Option(..., "--role", "-r", help="Role acquiring the lock"),
    cli: Optional[str] = typer.Option(None, "--cli", help="CLI tool used by this role"),
):
    """Acquire a file lock for a role"""
    acquired = lockfile.acquire(file, role=role, cli_tool=cli)
    if acquired:
        typer.echo(f"✓ Lock acquired: {file}  [{role}]")
    else:
        info = lockfile.is_locked(file)
        if info:
            age_min = info["age_seconds"] // 60
            typer.echo(
                f"✗ Already locked: {file}  "
                f"[role={info['role']}  age={age_min}m]"
            )
        else:
            typer.echo(f"✗ Could not acquire lock: {file}")
        raise typer.Exit(1)


def unlock(file: str):
    """Release a file lock"""
    info = lockfile.release(file)
    if info:
        typer.echo(f"✓ Lock released: {file}  [was held by {info['role']}]")
    else:
        typer.echo(f"⚠ No lock found for: {file}")


def locks():
    """Show all active file locks"""
    active = lockfile.list_locks()
    if not active:
        typer.echo("No active locks.")
        return

    typer.echo(f"{'FILE':<40}  {'ROLE':<12}  {'CLI':<12}  AGE")
    typer.echo("-" * 72)
    for info in sorted(active, key=lambda x: x["age_seconds"]):
        age_min = info["age_seconds"] // 60
        age_sec = info["age_seconds"] % 60
        cli_str = info.get("cli") or "-"
        typer.echo(
            f"{info['file']:<40}  {info['role']:<12}  {cli_str:<12}  "
            f"{age_min}m {age_sec}s"
        )
