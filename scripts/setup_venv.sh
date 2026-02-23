#!/bin/bash
# setup_venv.sh - Setup virtual environment with uv

set -e

PROJECT_DIR="${1:-.}"
PYTHON_VERSION="${2:-3.12}"

echo "Setting up virtual environment with Python $PYTHON_VERSION..."

# Create venv
uv venv "$PROJECT_DIR/.venv" --python "$PYTHON_VERSION"

# Activate and install
source "$PROJECT_DIR/.venv/bin/activate"

# Install aether in editable mode
uv pip install -e "$PROJECT_DIR"

# Install dana
uv pip install dana

echo "Done! Activate with: source $PROJECT_DIR/.venv/bin/activate"
