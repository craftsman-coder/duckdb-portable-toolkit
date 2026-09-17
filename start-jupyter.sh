#!/usr/bin/env bash
# ============================================================
#  Portable DuckDB Toolkit - Jupyter Launcher
#  Works on Linux, macOS, and Git Bash on Windows
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Find the venv's jupyter-lab executable ---
JUPYTER=""
if [ -x "$SCRIPT_DIR/runtime/venv/Scripts/jupyter-lab.exe" ]; then
    # Windows venv
    JUPYTER="$SCRIPT_DIR/runtime/venv/Scripts/jupyter-lab.exe"
elif [ -x "$SCRIPT_DIR/runtime/venv/bin/jupyter-lab" ]; then
    # Linux / macOS venv
    JUPYTER="$SCRIPT_DIR/runtime/venv/bin/jupyter-lab"
fi

if [ -z "$JUPYTER" ]; then
    echo
    echo "  [ERROR] JupyterLab not found."
    echo "  Checked:"
    echo "    $SCRIPT_DIR/runtime/venv/Scripts/jupyter-lab.exe"
    echo "    $SCRIPT_DIR/runtime/venv/bin/jupyter-lab"
    echo
    echo "  Run setup first:"
    echo "    python setup.py"
    echo
    read -p "  Press Enter to exit..."
    exit 1
fi

echo
echo "  Starting JupyterLab ..."
echo "  The browser will open automatically."
echo
echo "  To stop: press Ctrl+C twice."
echo

exec "$JUPYTER"