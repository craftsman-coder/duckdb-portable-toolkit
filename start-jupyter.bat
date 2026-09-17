@echo off
REM ============================================================
REM  Portable DuckDB Toolkit - Jupyter Launcher (Windows)
REM ============================================================

cd /d "%~dp0"

set "VENV=%~dp0runtime\venv\Scripts"

if not exist "%VENV%\jupyter-lab.exe" (
    echo.
    echo   [ERROR] JupyterLab not found.
    echo   Expected at: %VENV%\jupyter-lab.exe
    echo.
    echo   Run setup first:
    echo     python setup.py
    echo.
    pause
    exit /b 1
)

echo.
echo   Starting JupyterLab ...
echo   The browser will open automatically.
echo.
echo   To stop: press Ctrl+C twice in this window.
echo.

"%VENV%\jupyter-lab.exe"

pause