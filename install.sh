#!/usr/bin/env bash
# omni-agents Linux / macOS Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/TheCheepeer/omni-agents/main/install.sh | bash

set -e

echo "================================================="
echo "  omni-agents Installer (omni-agents CLI)"
echo "================================================="

# Check Python interpreter
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "[x] Python was not found on your system."
    echo "    Please install Python 3.10 or higher before proceeding:"
    echo "    https://www.python.org/downloads/"
    exit 1
fi

# Check recommended isolated package managers (uv > pipx > pip)
if command -v uv >/dev/null 2>&1; then
    echo "-> Installing via 'uv tool'..."
    uv tool install omni-agents-cli --force
elif command -v pipx >/dev/null 2>&1; then
    echo "-> Installing via 'pipx'..."
    pipx install omni-agents-cli --force
else
    echo "-> 'pipx' or 'uv' not found. Installing via user 'pip'..."
    $PYTHON_CMD -m pip install --upgrade --user omni-agents-cli
fi

echo ""
echo "[OK] omni-agents installed successfully!"
echo "     Run 'omni-agents' in any terminal to get started."
echo ""
