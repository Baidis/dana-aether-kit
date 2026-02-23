"""Tests for Aether CLI."""

import os
import tempfile
from pathlib import Path

from aether.commands.init import init


def test_init_creates_project():
    """Test that init creates the expected project structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)

        # Mock typer would be needed for full test
        # This is a placeholder
        pass
