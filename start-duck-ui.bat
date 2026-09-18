@echo off
REM ============================================================
REM  DuckDB Toolkit - DuckDB UI Launcher (Windows)
REM  Offline DuckDB web UI via duck-ui (Docker)
REM ============================================================

cd /d "%~dp0"

REM Check Docker
where docker >nul 2>nul
if errorlevel 1 (
    echo.
    echo   [ERROR] Docker is not installed or not on PATH.
    echo.
    echo   duck-ui needs Docker. Install it from:
    echo     https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

REM Check if duck-ui container is already running
docker ps --filter "name=duck-ui" --format "{{.Names}}" | findstr /C:"duck-ui" >nul
if not errorlevel 1 (
    echo.
    echo   duck-ui is already running.
    echo   Opening http://localhost:5522 ...
    start "" "http://localhost:5522"
    exit /b 0
)

echo.
echo   Starting duck-ui (offline DuckDB web UI) ...
echo.
echo   First run: pulls the Docker image (~50 MB, needs internet once).
echo   After that: fully offline.
echo.
echo   Opening http://localhost:5522 in your browser.
echo.
echo   To stop: docker stop duck-ui
echo.

docker run -d --rm ^
    --name duck-ui ^
    -p 5522:5522 ^
    ghcr.io/caioricciuti/duck-ui:latest

timeout /t 3 /nobreak >nul
start "" "http://localhost:5522"

echo.
echo   duck-ui started. Press any key to close this window.
pause >nul
