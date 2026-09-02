@echo off
REM ==============================================================================
REM Edu-Blog Radar Windows One-Click Runner
REM ==============================================================================

echo ========================================================
echo 🎓 [Edu-Blog Radar] Elementary & Middle School Blog Scout
echo ========================================================

python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python is not found in PATH.
    pause
    exit /b 1
)

echo 🚀 Generating Today's Top 3 Educational Blog Items...
python "%~dp0edu_collector.py"

echo ========================================================
echo 🎉 Execution completed. Telegram notification dispatched.
pause
