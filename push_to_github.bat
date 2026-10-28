@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Push PharmEasy Project to GitHub (Manisha-2618)

echo ========================================================
echo       Push PharmEasy Project to GitHub (Manisha-2618)
echo ========================================================
echo.

REM Set Git and GH executable paths
set "GIT_EXE=git"
if exist "%LOCALAPPDATA%\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd\git.exe" (
    set "GIT_EXE=%LOCALAPPDATA%\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd\git.exe"
)

set "GH_EXE=gh"
if exist "%LOCALAPPDATA%\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe" (
    set "GH_EXE=%LOCALAPPDATA%\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin\gh.exe"
)

echo Target Profile: https://github.com/Manisha-2618
echo.
echo Choose an option:
echo [1] Login via GitHub CLI (Recommended - 1-Click Web Authorization)
echo [2] Push using Personal Access Token (PAT)
echo [3] Push to existing remote repository
echo.
set /p CHOICE="Enter choice (1, 2, or 3): "

if "%CHOICE%"=="1" (
    echo.
    echo ----------------------------------------------------
    echo Step 1: Authorizing GitHub in your browser...
    echo (A browser window will open, or copy the one-time code shown)
    echo ----------------------------------------------------
    "%GH_EXE%" auth login --web --git-protocol https
    echo.
    echo ----------------------------------------------------
    echo Step 2: Creating repository 'PharmEasy_Project' and pushing...
    echo ----------------------------------------------------
    "%GH_EXE%" repo create PharmEasy_Project --public --source=. --remote=origin --push
    if !ERRORLEVEL! neq 0 (
        echo.
        echo If the repository already exists, pushing directly:
        "%GIT_EXE%" push -u origin main
    )
) else if "%CHOICE%"=="2" (
    echo.
    echo Create a token at: https://github.com/settings/tokens (Select 'repo' scope)
    set /p PAT="Paste your GitHub Personal Access Token: "
    if "!PAT!"=="" (
        echo Error: No token provided.
        pause
        exit /b 1
    )
    echo Configuring authenticated remote...
    "%GIT_EXE%" remote set-url origin https://Manisha-2618:!PAT!@github.com/Manisha-2618/PharmEasy_Project.git
    echo Pushing code to GitHub...
    "%GIT_EXE%" push -u origin main
    REM Reset URL so token is not left in plain text remote config
    "%GIT_EXE%" remote set-url origin https://github.com/Manisha-2618/PharmEasy_Project.git
) else if "%CHOICE%"=="3" (
    echo Pushing code to origin...
    "%GIT_EXE%" push -u origin main
) else (
    echo Invalid choice.
)

echo.
echo ========================================================
echo Process finished! Check: https://github.com/Manisha-2618/PharmEasy_Project
echo ========================================================
pause
