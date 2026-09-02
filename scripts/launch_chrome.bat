@echo off
REM ==============================================================================
REM Chrome Remote Debugging Mode Launcher for Windows (X-AI-Radar)
REM Port: 9223 | Profile: %USERPROFILE%\chrome_agent_profile
REM ==============================================================================

set PORT=9223
set PROFILE_DIR=%USERPROFILE%\chrome_agent_profile

echo ========================================================
echo 📡 [X-AI-Radar] Windows Chrome Launcher (Port: %PORT%)
echo ========================================================

REM 1. Check if port 9223 is already active
netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Chrome Remote Debugging is already running on port %PORT%.
    goto :done
)

REM 2. Detect Chrome installation path
set CHROME_EXE=
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set "CHROME_EXE=C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set "CHROME_EXE=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set "CHROME_EXE=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
)

if "%CHROME_EXE%"=="" (
    echo ❌ Google Chrome was not found in standard paths.
    echo Please install Chrome or modify this script with your custom path.
    pause
    exit /b 1
)

echo 🚀 Starting Chrome via: "%CHROME_EXE%"
if not exist "%PROFILE_DIR%" mkdir "%PROFILE_DIR%"

start "" "%CHROME_EXE%" --remote-debugging-port=%PORT% --remote-allow-origins="*" --user-data-dir="%PROFILE_DIR%" --no-first-run --no-default-browser-check https://x.com/home

timeout /t 3 /nobreak >nul

netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo 🎉 Chrome successfully launched on http://127.0.0.1:%PORT%
    echo 💡 Note: If not logged in, please complete a one-time login to X.com in the opened window.
) else (
    echo ⚠️ Chrome started. Please verify http://127.0.0.1:%PORT%/json/version
)

:done
echo ========================================================
