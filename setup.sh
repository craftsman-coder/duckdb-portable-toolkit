#!/usr/bin/env bash
# ============================================================
#  DuckDB Toolkit - Setup Launcher (Linux / macOS / Git Bash)
#  Runs setup.py with any arguments you pass.
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ---- Find Python ----
PY=""
if command -v python3 >/dev/null 2>&1; then
    PY="python3"
elif command -v python >/dev/null 2>&1; then
    PY="python"
fi

if [ -z "$PY" ]; then
    echo
    echo "  [ERROR] Python not found in PATH."
    echo
    echo "  This toolkit needs a system Python 3.9+ to bootstrap"
    echo "  its own portable Python. After the first run, the"
    echo "  portable Python is used for everything."
    echo
    echo "  Install Python:"
    echo "    Debian/Ubuntu : sudo apt install python3"
    echo "    Fedora        : sudo dnf install python3"
    echo "    Arch          : sudo pacman -S python"
    echo "    macOS         : brew install python"
    echo
    read -p "  Press Enter to exit..."
    exit 1
fi

# ---- Check Python version (3.9+) ----
if ! "$PY" -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    echo
    echo "  [ERROR] Python 3.9 or newer is required."
    "$PY" --version
    echo
    read -p "  Press Enter to exit..."
    exit 1
fi

# ---- Run setup ----
"$PY" setup.py "$@"

echo
echo "  Setup complete."
echo "  To launch JupyterLab, run: ./start-jupyter.sh"
echo