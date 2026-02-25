"""File lock system for multi-agent coordination.

Lock files are stored as JSON under .aether/locks/ relative to the
project root.  The encoded path uses URL-percent-style encoding so that
any file path maps to a safe filename.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import quote


# Default stale-lock threshold in seconds (30 minutes)
DEFAULT_STALE_SECONDS = 30 * 60

_LOCK_DIR_NAME = Path(".aether") / "locks"


def _lock_path(project_root: Path, filepath: str) -> Path:
    """Return the .lock file path for *filepath* inside *project_root*."""
    encoded = quote(filepath, safe="")
    return project_root / _LOCK_DIR_NAME / f"{encoded}.lock"


def _lock_dir(project_root: Path) -> Path:
    d = project_root / _LOCK_DIR_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def acquire(
    filepath: str,
    role: str,
    cli_tool: Optional[str] = None,
    project_root: Optional[Path] = None,
) -> bool:
    """Attempt to acquire a lock on *filepath* for *role*.

    Returns True if the lock was acquired, False if already held.
    Auto-expires stale locks before checking.
    """
    root = project_root or Path.cwd()
    lp = _lock_path(root, filepath)
    _lock_dir(root)

    # Auto-expire stale lock
    if lp.exists():
        info = json.loads(lp.read_text())
        acquired_ts = datetime.fromisoformat(info["acquired"])
        age = (datetime.now(timezone.utc) - acquired_ts).total_seconds()
        stale_after = info.get("stale_after", DEFAULT_STALE_SECONDS)
        if age > stale_after:
            lp.unlink()
        else:
            return False  # Lock is still valid

    payload = {
        "role": role,
        "cli": cli_tool,
        "file": filepath,
        "acquired": datetime.now(timezone.utc).isoformat(),
        "stale_after": DEFAULT_STALE_SECONDS,
    }
    lp.write_text(json.dumps(payload, indent=2))
    return True


def release(
    filepath: str,
    project_root: Optional[Path] = None,
) -> Optional[dict]:
    """Release the lock on *filepath*.

    Returns the lock metadata (useful for coordinator cross-role
    notifications), or None if no lock existed.
    """
    root = project_root or Path.cwd()
    lp = _lock_path(root, filepath)

    if not lp.exists():
        return None

    info = json.loads(lp.read_text())
    lp.unlink()
    return info


def is_locked(
    filepath: str,
    project_root: Optional[Path] = None,
) -> Optional[dict]:
    """Return lock info dict if *filepath* is locked (and not stale), else None."""
    root = project_root or Path.cwd()
    lp = _lock_path(root, filepath)

    if not lp.exists():
        return None

    info = json.loads(lp.read_text())
    acquired_ts = datetime.fromisoformat(info["acquired"])
    age = (datetime.now(timezone.utc) - acquired_ts).total_seconds()
    stale_after = info.get("stale_after", DEFAULT_STALE_SECONDS)

    if age > stale_after:
        lp.unlink()
        return None

    info["age_seconds"] = int(age)
    return info


def list_locks(project_root: Optional[Path] = None) -> list:
    """Return a list of all active (non-stale) lock info dicts."""
    root = project_root or Path.cwd()
    lock_dir = root / _LOCK_DIR_NAME

    if not lock_dir.exists():
        return []

    locks = []
    for lf in lock_dir.glob("*.lock"):
        try:
            info = json.loads(lf.read_text())
            acquired_ts = datetime.fromisoformat(info["acquired"])
            age = (datetime.now(timezone.utc) - acquired_ts).total_seconds()
            stale_after = info.get("stale_after", DEFAULT_STALE_SECONDS)

            if age > stale_after:
                lf.unlink()
                continue

            info["age_seconds"] = int(age)
            locks.append(info)
        except (json.JSONDecodeError, KeyError):
            continue

    return locks
