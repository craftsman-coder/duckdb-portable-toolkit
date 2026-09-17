#!/usr/bin/env bash
# ============================================================
#  Portable DuckDB Toolkit - Streamlit Launcher
#  Works on Linux, macOS, and Git Bash on Windows
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DASH_DIR="$SCRIPT_DIR/dashboards"
PORT=8501

# --- Find the portable python ---
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

# --- If a dashboard name was passed as argument, run it directly ---
if [ -n "$1" ]; then
    TARGET=""
    if [ -f "$DASH_DIR/$1" ]; then
        TARGET="$DASH_DIR/$1"
    elif [ -f "$DASH_DIR/$1.py" ]; then
        TARGET="$DASH_DIR/$1.py"
    else
        echo "  [ERROR] Dashboard not found: $1"
        exit 1
    fi
    NAME="$(basename "$TARGET" .py)"
    run_one "$TARGET" "$NAME"
    exit 0
fi

run_one() {
    local file="$1"
    local name="$2"
    echo
    echo "  Starting Streamlit: $name"
    echo "  URL: http://localhost:$PORT"
    echo
    echo "  Press Ctrl+C twice to stop."
    echo
    exec "$PY" -m streamlit run "$file" \
        --server.port "$PORT" \
        --server.headless true \
        --browser.gatherUsageStats false
}

# --- Interactive menu ---
while true; do
    clear 2>/dev/null || true
    echo
    echo "============================================================"
    echo "  Available Streamlit dashboards"
    echo "============================================================"
    echo

    # Collect dashboards into an array
    FILES=()
    while IFS= read -r -d '' f; do
        FILES+=("$f")
    done < <(find "$DASH_DIR" -maxdepth 1 -name "*.py" -type f -print0 | sort -z)

    COUNT=${#FILES[@]}

    if [ "$COUNT" -eq 0 ]; then
        echo "  No dashboards found in dashboards/"
        echo
        read -p "  Press Enter to exit..."
        exit 1
    fi

    for i in "${!FILES[@]}"; do
        n=$((i + 1))
        name="$(basename "${FILES[$i]}" .py)"
        printf "  %2d. %s\n" "$n" "$name"
    done

    echo
    echo "  A. Run all dashboards (each on its own port)"
    echo "  Q. Quit"
    echo

    read -p "  Choose a number, A, or Q: " CHOICE

    if [ "$CHOICE" = "Q" ] || [ "$CHOICE" = "q" ]; then
        exit 0
    fi

    if [ "$CHOICE" = "A" ] || [ "$CHOICE" = "a" ]; then
        echo
        echo "  Starting all dashboards on sequential ports ..."
        echo
        P=8501
        for f in "${FILES[@]}"; do
            name="$(basename "$f" .py)"
            echo "  Starting $name on port $P"
            "$PY" -m streamlit run "$f" \
                --server.port "$P" \
                --server.headless true \
                --browser.gatherUsageStats false \
                > "/tmp/streamlit-$name.log" 2>&1 &
            P=$((P + 1))
        done
        echo
        echo "  All dashboards started in the background."
        echo "  Logs: /tmp/streamlit-*.log"
        echo
        echo "  To stop all: pkill -f 'streamlit run'"
        echo
        read -p "  Press Enter to return to the menu..."
        continue
    fi

    # Validate number
    if ! [[ "$CHOICE" =~ ^[0-9]+$ ]]; then
        echo "  Invalid choice."
        sleep 1
        continue
    fi

    IDX=$((CHOICE - 1))
    if [ "$IDX" -lt 0 ] || [ "$IDX" -ge "$COUNT" ]; then
        echo "  Invalid choice."
        sleep 1
        continue
    fi

    FILE="${FILES[$IDX]}"
    NAME="$(basename "$FILE" .py)"
    run_one "$FILE" "$NAME"
done