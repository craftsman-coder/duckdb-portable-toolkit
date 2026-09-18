#!/usr/bin/env bash
# ============================================================
#  DuckDB Toolkit - DuckDB UI Launcher (Linux / macOS / Git Bash)
#  Offline DuckDB web UI via duck-ui (Docker)
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Docker
if ! command -v docker >/dev/null 2>&1; then
    echo
    echo "  [ERROR] Docker is not installed or not on PATH."
    echo
    echo "  duck-ui needs Docker. Install it from:"
    echo "    https://www.docker.com/products/docker-desktop"
    echo
    exit 1
fi

# Check if already running
if docker ps --filter "name=duck-ui" --format "{{.Names}}" | grep -q "duck-ui"; then
    echo
    echo "  duck-ui is already running."
    echo "  Opening http://localhost:5522 ..."
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:5522" >/dev/null 2>&1 &
    elif command -v open >/dev/null 2>&1; then
        open "http://localhost:5522" >/dev/null 2>&1 &
    fi
    exit 0
fi

echo
echo "  Starting duck-ui (offline DuckDB web UI) ..."
echo
echo "  First run: pulls the Docker image (~50 MB, needs internet once)."
echo "  After that: fully offline."
echo
echo "  Opening http://localhost:5522 in your browser."
echo
echo "  To stop: docker stop duck-ui"
echo

docker run -d --rm     --name duck-ui     -p 5522:5522     ghcr.io/caioricciuti/duck-ui:latest

sleep 3
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:5522" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
    open "http://localhost:5522" >/dev/null 2>&1 &
fi

echo
echo "  duck-ui started."
