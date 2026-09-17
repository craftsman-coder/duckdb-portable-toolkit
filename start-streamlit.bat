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
    echo   [ERROR] Python not found at:
    echo     %PY%
    echo.
    echo   Run setup.py first:
    echo     python setup.py
    echo.
    pause
    exit /b 1
)

REM ---- If user passed a dashboard name as argument, use it ----
if not "%~1"=="" (
    set "TARGET=%DASH_DIR%\%~1"
    if exist "!TARGET!" goto :run
    set "TARGET=%DASH_DIR%\%~1.py"
    if exist "!TARGET!" goto :run
    echo   [ERROR] Dashboard not found: %~1
    echo.
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
    set /a COUNT+=1
    set "FILE_!COUNT!=%%F"
    set "NAME_!COUNT!=%%~nF"
    echo   !COUNT!. %%~nF
)

if %COUNT%==0 (
    echo   No dashboards found in dashboards\
    echo.
    pause
    exit /b 1
)

echo.
echo   A. Run all dashboards (each on its own port)
echo   Q. Quit
echo.

set /p "CHOICE=  Choose a number, A, or Q: "

if /i "%CHOICE%"=="Q" exit /b 0
if /i "%CHOICE%"=="A" goto :run_all

REM ---- Validate numeric choice ----
set "VALID=0"
for /l %%I in (1,1,%COUNT%) do (
    if "%CHOICE%"=="%%I" set "VALID=1"
)
if "%VALID%"=="0" (
    echo.
    echo   Invalid choice. Press any key to try again.
    pause >nul
    goto :menu
)

set "TARGET=!FILE_%CHOICE%!"
set "NAME=!NAME_%CHOICE%!"

:run
echo.
echo   Starting Streamlit dashboard: %NAME%
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

:run_all
echo.
echo   Starting all dashboards on sequential ports ...
echo.

set "P=8501"
for /l %%I in (1,1,%COUNT%) do (
    set "F=!FILE_%%I!"
    set "N=!NAME_%%I!"
    echo   Starting !N! on port !P!
    start "Streamlit - !N!" cmd /c ^
        ""%PY%" -m streamlit run "!F!" --server.port !P! --server.headless true"
    set /a P+=1
)

echo.
echo   All dashboards started in separate windows.
echo   Close each window to stop the corresponding dashboard.
echo.
pause
exit /b 0