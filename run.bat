@echo off
setlocal enabledelayedexpansion
title PharmEasy Web Server

cd /d "%~dp0"

echo ========================================================
echo  Starting PharmEasy Pharmacy E-Commerce Web Application
echo ========================================================

REM Look for real Python executable first to avoid 0-byte Windows Store alias
set "PY_CMD="

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) else if exist "%ProgramFiles%\Python312\python.exe" (
    set "PY_CMD=%ProgramFiles%\Python312\python.exe"
) else if exist "%ProgramFiles%\Python311\python.exe" (
    set "PY_CMD=%ProgramFiles%\Python311\python.exe"
) else (
    py -3 --version >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set "PY_CMD=py -3"
    ) else (
        set "PY_CMD=python"
    )
)

echo Using Python: !PY_CMD!

REM Initialize & seed database if needed
"!PY_CMD!" database\seed_data.py

echo.
echo ========================================================
echo  Opening http://127.0.0.1:5000 in your browser...
echo  Flask Web Server Running!
echo  Press Ctrl+C in this window to stop the server.
echo ========================================================
echo.

REM Automatically open website in default browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

"!PY_CMD!" app.py

pause
