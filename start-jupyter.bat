@echo off
REM ============================================================
REM  Portable DuckDB Toolkit - Jupyter Launcher (Windows)
REM ============================================================

cd /d "%~dp0"

REM Cache tiktoken files locally so Jupyter AI works offline
set "TIKTOKEN_CACHE_DIR=%~dp0runtime\tiktoken_cache"
set "JUPYTER_CONFIG_DIR=%~dp0runtime\jupyter_config"

set "PY=%~dp0runtime\python\python.exe"

if not exist "%PY%" (
    echo.
    echo   [ERROR] Portable Python not found at:
    echo     %PY%
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

"%PY%" -m jupyterlab

pause
