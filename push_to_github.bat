@echo off
setlocal
cd /d "%~dp0"
title Push PharmEasy Project to GitHub

echo ========================================================
echo       Push PharmEasy Project to Your GitHub
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

echo Select how you want to push to GitHub:
echo [1] Enter an existing GitHub repository URL (e.g. https://github.com/username/repo.git)
echo [2] Login with GitHub CLI and create a new repository automatically
echo.
set /p CHOICE="Enter choice (1 or 2): "

if "%CHOICE%"=="1" (
    echo.
    set /p REPO_URL="Paste your GitHub repository URL: "
    if "!REPO_URL!"=="" (
        echo Error: No URL entered.
        pause
        exit /b 1
    )
    "%GIT_EXE%" remote remove origin >nul 2>&1
    "%GIT_EXE%" remote add origin !REPO_URL!
    "%GIT_EXE%" branch -M main
    echo Pushing to GitHub...
    "%GIT_EXE%" push -u origin main
) else if "%CHOICE%"=="2" (
    echo.
    echo Opening GitHub CLI authentication...
    "%GH_EXE%" auth login -w -p https
    echo.
    set /p REPO_NAME="Enter new repo name [default: pharmeasy-clone]: "
    if "!REPO_NAME!"=="" set "REPO_NAME=pharmeasy-clone"
    echo Creating repository !REPO_NAME! and pushing...
    "%GH_EXE%" repo create !REPO_NAME! --public --source=. --remote=origin --push
) else (
    echo Invalid choice.
)

echo.
echo ========================================================
echo Done!
echo ========================================================
pause
