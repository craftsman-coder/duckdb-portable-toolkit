#!/usr/bin/env bash
# ============================================================
#  Portable DuckDB Toolkit - Jupyter Launcher
#  Works on Linux, macOS, and Git Bash on Windows
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Cache tiktoken files locally so Jupyter AI works offline
export TIKTOKEN_CACHE_DIR="$SCRIPT_DIR/runtime/tiktoken_cache"
export JUPYTER_CONFIG_DIR="$SCRIPT_DIR/runtime/jupyter_config"

# Find the portable Python
PY=""
if [ -x "$SCRIPT_DIR/runtime/python/python.exe" ]; then
    PY="$SCRIPT_DIR/runtime/python/python.exe"
elif [ -x "$SCRIPT_DIR/runtime/python/bin/python3" ]; then
    PY="$SCRIPT_DIR/runtime/python/bin/python3"
elif [ -x "$SCRIPT_DIR/runtime/python/bin/python" ]; then
    PY="$SCRIPT_DIR/runtime/python/bin/python"
fi

if [ -z "$PY" ]; then
    echo
    echo "  [ERROR] Portable Python not found."
    echo "  Checked:"
    echo "    runtime/python/python.exe"
    echo "    runtime/python/bin/python3"
    echo "    runtime/python/bin/python"
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

exec "$PY" -m jupyterlab
