@echo off
REM ==============================================================================
REM X-AI-Radar & Edu-Blog Radar Windows Root Runner
REM ==============================================================================

python "%~dp0radar.py" %*
if %ERRORLEVEL% neq 0 (
    echo.
    echo ⚠️ Execution encountered an issue.
    pause
)
