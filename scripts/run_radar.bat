@echo off
REM ==============================================================================
REM X-AI-Radar Windows Environment Checker & Manual Runner
REM ==============================================================================

set PORT=9223

echo ========================================================
echo 📡 [X-AI-Radar] Windows Quick Runner
echo ========================================================

REM 1. Check Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python is not found in PATH. Please install Python 3.10+.
    pause
    exit /b 1
)

REM 2. Check Chrome Port 9223
netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ⚠️ Chrome CDP Port %PORT% is not active.
    echo 👉 Launching Chrome Debugging Mode...
    call "%~dp0launch_chrome.bat"
)

echo 🚀 Executing X-AI-Radar Collection Engine...
python "%~dp0collector.py"

echo ========================================================
echo 🎉 Execution finished.
pause
