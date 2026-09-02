@echo off
REM ==============================================================================
REM X-AI-Radar & Edu-Blog Radar One-Click Windows Installer
REM ==============================================================================

echo ========================================================
echo 📡 [X-AI-Radar] Windows Environment Setup & Installer
echo ========================================================

REM 1. Verify Python installation
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python 3.10+ is required but not found in PATH.
    echo 👉 Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python detected.

REM 2. Initialize .env from .env.example if missing
if not exist "%~dp0.env" (
    if exist "%~dp0.env.example" (
        copy "%~dp0.env.example" "%~dp0.env" >nul
        echo 📝 Created .env configuration file from template.
    )
)

REM 3. Install required Python packages
echo 📦 Installing required Python dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r "%~dp0requirements.txt"

if %ERRORLEVEL% equ 0 (
    echo ✅ Dependencies successfully installed.
) else (
    echo ⚠️ Dependency installation encountered warnings.
)

echo.
echo ========================================================
echo 🎉 Setup completed successfully!
echo 👉 Launch Chrome Debugger: scripts\launch_chrome.bat
echo 👉 Run AI Tech Radar:      python radar.py --ai
echo 👉 Run Edu-Blog Radar:     python radar.py --edu
echo 👉 Run Everything:         run.bat
echo ========================================================
pause
