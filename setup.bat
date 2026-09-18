@echo off
REM ============================================================
REM  DuckDB Toolkit - Setup Launcher (Windows)
REM  Runs setup.py with any arguments you pass.
REM ============================================================

cd /d "%~dp0"

REM ---- Find Python (try several names) ----
set "PY="
where python  >nul 2>nul && set "PY=python"
if not defined PY where python3 >nul 2>nul && set "PY=python3"
if not defined PY where py      >nul 2>nul && set "PY=py"

if not defined PY (
    echo.
    echo   [ERROR] Python not found in PATH.
    echo.
    echo   This toolkit needs a system Python 3.9+ to bootstrap
    echo   its own portable Python. After the first run, the
    echo   portable Python is used for everything.
    echo.
    echo   Install Python from:
    echo     https://www.python.org/downloads/
    echo.
    echo   Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

REM ---- Check Python version (3.9+) ----
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>nul
if errorlevel 1 (
    echo.
    echo   [ERROR] Python 3.9 or newer is required.
    %PY% --version
    echo.
    pause
    exit /b 1
)

REM ---- Run setup ----
%PY% setup.py %*

if errorlevel 1 (
    echo.
    echo   Setup failed. Please read the error above.
    echo.
    pause
    exit /b 1
)

echo.
echo   Setup complete.
echo   To launch JupyterLab, double-click start-jupyter.bat
echo.
pause