#!/usr/bin/env bash
# ============================================================
#  DuckDB Toolkit - Verify Launcher (Linux / macOS / Git Bash)
#  Runs verify.py to check that everything is installed.
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ---- Prefer the portable Python (if installed) ----
PORTABLE=""
if [ -x "$SCRIPT_DIR/runtime/python/python.exe" ]; then
    PORTABLE="$SCRIPT_DIR/runtime/python/python.exe"
elif [ -x "$SCRIPT_DIR/runtime/python/bin/python3" ]; then
    PORTABLE="$SCRIPT_DIR/runtime/python/bin/python3"
elif [ -x "$SCRIPT_DIR/runtime/python/bin/python" ]; then
    PORTABLE="$SCRIPT_DIR/runtime/python/bin/python"
fi

if [ -n "$PORTABLE" ]; then
    "$PORTABLE" verify.py "$@"
    RC=$?

    echo
    if [ $RC -ne 0 ]; then
        echo "  Some checks failed. Run ./setup.sh to fix missing pieces."
        echo
        read -p "  Press Enter to exit..."
        exit $RC
    fi

    echo "  Everything looks good."
    echo
    exit 0
fi

# ---- Fall back to system Python ----
PY=""
if command -v python3 >/dev/null 2>&1; then
    PY="python3"
elif command -v python >/dev/null 2>&1; then
    PY="python"
fi

if [ -z "$PY" ]; then
    echo
    echo "  [ERROR] Neither portable nor system Python found."
    echo
    echo "  Run ./setup.sh first to install the portable Python."
    echo
    read -p "  Press Enter to exit..."
    exit 1
fi

echo
echo "  [WARN] Portable Python not found. Using system Python:"
echo "    $PY"
echo
echo "  Run ./setup.sh to install the portable environment."
echo

"$PY" verify.py "$@"
RC=$?

echo
if [ $RC -ne 0 ]; then
    echo "  Some checks failed. Run ./setup.sh to fix missing pieces."
    echo
    read -p "  Press Enter to exit..."
    exit $RC
fi

echo "  Everything looks good."
echo