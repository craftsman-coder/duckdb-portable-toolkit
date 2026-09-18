@echo off
REM ============================================================
REM  DuckDB Toolkit - Verify Launcher (Windows)
REM  Runs verify.py to check that everything is installed.
REM ============================================================

cd /d "%~dp0"

REM ---- Prefer the portable Python (if installed) ----
set "PORTABLE=%~dp0runtime\python\python.exe"

if exist "%PORTABLE%" (
    "%PORTABLE%" verify.py %*
    set "RC=%ERRORLEVEL%"
    if %RC% NEQ 0 (
        echo.
        echo   Some checks failed. Run setup.bat to fix missing pieces.
        echo.
        pause
        exit /b %RC%
    )
    echo.
    echo   Everything looks good.
    echo.
    pause
    exit /b 0
)

REM ---- Fall back to system Python ----
set "PY="
where python  >nul 2>nul && set "PY=python"
if not defined PY where python3 >nul 2>nul && set "PY=python3"
if not defined PY where py      >nul 2>nul && set "PY=py"

if not defined PY (
    echo.
    echo   [ERROR] Neither portable nor system Python found.
    echo.
    echo   Run setup.bat first to install the portable Python.
    echo.
    pause
    exit /b 1
)

echo.
echo   [WARN] Portable Python not found. Using system Python:
echo     %PY%
echo.
echo   Run setup.bat to install the portable environment.
echo.

%PY% verify.py %*
set "RC=%ERRORLEVEL%"

if %RC% NEQ 0 (
    echo.
    echo   Some checks failed. Run setup.bat to fix missing pieces.
    echo.
    pause
    exit /b %RC%
)

echo.
echo   Everything looks good.
echo.
pause