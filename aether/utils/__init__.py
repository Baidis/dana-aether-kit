"""Utility functions for Aether CLI."""

import os
from typing import Optional

try:
    from dotenv import load_dotenv

    def load_env(path: str = ".env") -> bool:
        """Load environment variables from .env file."""
        if os.path.exists(path):
            load_dotenv(path)
            return True
        return False
except ImportError:

    def load_env(path: str = ".env") -> bool:
        """Load environment variables from .env file (fallback)."""
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip().strip("'\"")
            return True
        return False


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable."""
    return os.getenv(key, default)


def check_dana_available() -> bool:
    """Check if Dana is installed and available."""
    import shutil

    return shutil.which("dana") is not None
