@echo off
setlocal enabledelayedexpansion
REM ============================================================
REM  Portable DuckDB Toolkit - Streamlit Launcher (Windows)
REM ============================================================

cd /d "%~dp0"

set "PY=%~dp0runtime\python\python.exe"
set "DASH_DIR=%~dp0dashboards"
set "PORT=8501"

if not exist "%PY%" (
    echo.
    echo   [ERROR] Portable Python not found at:
    echo     %PY%
    echo.
    echo   Run setup.py first.
    echo.
    pause
    exit /b 1
)

REM ---- If a dashboard name was passed as argument, use it ----
if not "%~1"=="" (
    set "TARGET=%DASH_DIR%\%~1"
    if exist "!TARGET!" goto :run
    set "TARGET=%DASH_DIR%\%~1.py"
    if exist "!TARGET!" goto :run
    echo   [ERROR] Dashboard not found: %~1
    pause
    exit /b 1
)

REM ---- Interactive menu ----
:menu
cls
echo.
echo ============================================================
echo   Available Streamlit dashboards
echo ============================================================
echo.

set "COUNT=0"
for %%F in ("%DASH_DIR%\*.py") do (
    set "FNAME=%%~nF"
    REM Skip files that start with underscore (_common, __init__, etc.)
    if not "!FNAME:~0,1!"=="_" (
        set /a COUNT+=1
        set "FILE_!COUNT!=%%F"
        set "NAME_!COUNT!=%%~nF"
        echo   !COUNT!. %%~nF
    )
)

if %COUNT%==0 (
    echo   No dashboards found in dashboards\
    echo.
    pause
    exit /b 1
)

echo.
echo   Q. Quit
echo.

set /p "CHOICE=  Choose a number or Q: "

if /i "%CHOICE%"=="Q" exit /b 0

set "VALID=0"
for /l %%I in (1,1,%COUNT%) do (
    if "%CHOICE%"=="%%I" set "VALID=1"
)
if "%VALID%"=="0" (
    echo.
    echo   Invalid choice.
    pause >nul
    goto :menu
)

set "TARGET=!FILE_%CHOICE%!"
set "NAME=!NAME_%CHOICE%!"

:run
echo.
echo   Starting Streamlit: %NAME%
echo   URL: http://localhost:%PORT%
echo.
echo   Press Ctrl+C twice to stop.
echo.

"%PY%" -m streamlit run "%TARGET%" ^
    --server.port %PORT% ^
    --server.headless true ^
    --browser.gatherUsageStats false

pause
exit /b 0