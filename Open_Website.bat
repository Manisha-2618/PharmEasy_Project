@echo off
title Open PharmEasy Website
cd /d "%~dp0"

REM Check if server is already running on port 5000
netstat -ano | findstr ":5000 " >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo PharmEasy server is already running!
    echo Opening http://127.0.0.1:5000 in your browser...
    start http://127.0.0.1:5000
) else (
    echo Starting server and launching browser...
    call run.bat
)

