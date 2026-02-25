"""Tests for Aether CLI."""

import os
import time
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from aether.cli import app
from aether.utils import lockfile


runner = CliRunner()


# ── Helpers ──────────────────────────────────────────────────────────────────


def run_in_tmpdir(fn):
    """Decorator: run test function with cwd changed to a fresh temp dir."""
    import functools

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        original = Path.cwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            try:
                return fn(*args, tmp=Path(tmpdir), **kwargs)
            finally:
                os.chdir(original)

    return wrapper


# ── init ─────────────────────────────────────────────────────────────────────


def test_init_creates_project():
    with tempfile.TemporaryDirectory() as tmpdir:
        original = Path.cwd()
        os.chdir(tmpdir)
        try:
            result = runner.invoke(app, ["init", "TestBot"])
            assert result.exit_code == 0, result.output

            base = Path(tmpdir) / "TestBot"
            assert base.is_dir()
            assert (base / "agents").is_dir()
            assert (base / "intents").is_dir()
            assert (base / "workflows").is_dir()
            assert (base / "project.dana").exists()
            assert (base / "agents" / "testbot.na").exists()
            assert (base / ".aether" / "roles.json").exists()
        finally:
            os.chdir(original)


def test_init_with_env():
    with tempfile.TemporaryDirectory() as tmpdir:
        original = Path.cwd()
        os.chdir(tmpdir)
        try:
            result = runner.invoke(app, ["init", "TestBot", "--env"])
            assert result.exit_code == 0, result.output
            assert (Path(tmpdir) / "TestBot" / ".env.example").exists()
            assert "OPENROUTER_API_KEY" in (
                Path(tmpdir) / "TestBot" / ".env.example"
            ).read_text()
        finally:
            os.chdir(original)


def test_init_placeholders_substituted():
    """project.dana and agent .na file must not contain raw {{ }} placeholders."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original = Path.cwd()
        os.chdir(tmpdir)
        try:
            runner.invoke(app, ["init", "My Project"])
            base = Path(tmpdir) / "My Project"
            project_text = (base / "project.dana").read_text()
            agent_text = (base / "agents" / "my_project.na").read_text()
            assert "{{" not in project_text
            assert "{{" not in agent_text
            assert "my_project" in project_text
        finally:
            os.chdir(original)


# ── coordinate ───────────────────────────────────────────────────────────────


def test_coordinate_output():
    result = runner.invoke(app, ["coordinate", "Add dark mode toggle"])
    assert result.exit_code == 0
    output = result.output
    # Should mention role names or CLI hints
    assert "researcher" in output or "analyst" in output or "critic" in output


def test_coordinate_dana_intent():
    result = runner.invoke(app, ["coordinate", "add caching", "--dana-intent"])
    assert result.exit_code == 0
    assert "intent" in result.output


# ── agent ─────────────────────────────────────────────────────────────────────


def test_agent_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        original = Path.cwd()
        os.chdir(tmpdir)
        try:
            result = runner.invoke(app, ["agent", "BTC daily sentiment assessor"])
            assert result.exit_code == 0, result.output
            expected = Path(tmpdir) / "agents" / "btc_daily_sentiment_assessor.na"
            assert expected.exists()
            content = expected.read_text()
            assert "btc_daily_sentiment_assessor" in content
            assert "reason(" in content
        finally:
            os.chdir(original)


def test_agent_custom_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir) / "custom_agent.na"
        result = runner.invoke(
            app, ["agent", "Market analyser", "--output", str(dest)]
        )
        assert result.exit_code == 0, result.output
        assert dest.exists()


def test_agent_refuses_overwrite():
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir) / "existing.na"
        dest.write_text("# existing")
        result = runner.invoke(app, ["agent", "test", "--output", str(dest)])
        assert result.exit_code != 0


# ── lockfile ──────────────────────────────────────────────────────────────────


def test_lockfile_acquire_release():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        fp = "src/Toggle.tsx"

        assert lockfile.acquire(fp, role="frontend", cli_tool="claude", project_root=root)
        info = lockfile.is_locked(fp, project_root=root)
        assert info is not None
        assert info["role"] == "frontend"

        # Second acquire should fail
        assert not lockfile.acquire(fp, role="backend", project_root=root)

        released = lockfile.release(fp, project_root=root)
        assert released is not None
        assert released["role"] == "frontend"

        assert lockfile.is_locked(fp, project_root=root) is None


def test_lockfile_stale_expiry():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        fp = "src/stale.ts"

        # Acquire with a 1-second stale threshold
        acquired = lockfile.acquire(fp, role="analyst", project_root=root)
        assert acquired

        # Manually patch the lock file to be in the past
        from datetime import datetime, timezone, timedelta
        lp = list((root / ".aether" / "locks").glob("*.lock"))[0]
        import json
        data = json.loads(lp.read_text())
        data["acquired"] = (
            datetime.now(timezone.utc) - timedelta(seconds=3600)
        ).isoformat()
        data["stale_after"] = 1  # 1 second
        lp.write_text(json.dumps(data))

        # Should be treated as expired
        assert lockfile.is_locked(fp, project_root=root) is None
        # Should now be acquirable again
        assert lockfile.acquire(fp, role="new_role", project_root=root)


def test_lockfile_list_locks():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        lockfile.acquire("a.na", role="r1", project_root=root)
        lockfile.acquire("b.na", role="r2", project_root=root)
        locks = lockfile.list_locks(project_root=root)
        assert len(locks) == 2
        roles = {l["role"] for l in locks}
        assert roles == {"r1", "r2"}
