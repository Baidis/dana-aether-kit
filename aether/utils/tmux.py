"""Tmux orchestration utilities for aether coordinate --launch."""

import shutil
import subprocess
from typing import Dict


def detect_cli_tools() -> Dict[str, str]:
    """Return a dict of {cli_name: full_path} for CLIs found in $PATH."""
    candidates = ["claude", "gemini", "opencode", "grok"]
    return {name: path for name in candidates if (path := shutil.which(name))}


def create_session(name: str) -> bool:
    """Create a new tmux session (or reuse if it already exists).

    Returns True if the session was freshly created, False if reused.
    """
    exists = subprocess.run(
        ["tmux", "has-session", "-t", name],
        capture_output=True,
    ).returncode == 0

    if not exists:
        subprocess.run(
            ["tmux", "new-session", "-d", "-s", name],
            check=True,
        )
        return True
    return False


def create_named_pane(session: str, role_name: str, first: bool = False) -> str:
    """Create a named window/pane in *session* for *role_name*.

    Uses tmux windows (one window per role) so each has a named tab.
    Returns the target identifier ``session:role_name``.
    """
    target = f"{session}:{role_name}"

    if first:
        # Rename the initial window that was created with the session
        subprocess.run(
            ["tmux", "rename-window", "-t", f"{session}:0", role_name],
            check=True,
        )
    else:
        subprocess.run(
            ["tmux", "new-window", "-t", session, "-n", role_name],
            check=True,
        )

    return target


def send_prompt(pane: str, cli_tool: str, prompt: str) -> None:
    """Send ``cli_tool "prompt"`` to a tmux pane via send-keys."""
    # Escape single quotes in the prompt
    safe_prompt = prompt.replace("'", "'\\''")
    command = f"{cli_tool} '{safe_prompt}'"
    subprocess.run(
        ["tmux", "send-keys", "-t", pane, command, "Enter"],
        check=True,
    )


def broadcast(session: str, message: str) -> None:
    """Send *message* as plain text to every window in *session*."""
    result = subprocess.run(
        ["tmux", "list-windows", "-t", session, "-F", "#{window_index}"],
        capture_output=True,
        text=True,
    )
    for idx in result.stdout.strip().splitlines():
        target = f"{session}:{idx}"
        subprocess.run(
            ["tmux", "send-keys", "-t", target, message, "Enter"],
            check=True,
        )


def attach_session(name: str) -> None:
    """Attach the current terminal to *name* (blocks until detached)."""
    subprocess.run(["tmux", "attach-session", "-t", name])


def kill_session(name: str) -> None:
    """Kill the named tmux session if it exists."""
    subprocess.run(
        ["tmux", "kill-session", "-t", name],
        capture_output=True,
    )


def tmux_available() -> bool:
    """Return True if tmux is on $PATH."""
    return shutil.which("tmux") is not None
