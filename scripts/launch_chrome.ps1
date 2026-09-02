# ==============================================================================
# Chrome Remote Debugging Mode Launcher for Windows PowerShell (X-AI-Radar)
# Port: 9223 | Profile: $HOME\chrome_agent_profile
# ==============================================================================

$port = 9223
$profileDir = "$HOME\chrome_agent_profile"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "📡 [X-AI-Radar] Windows PowerShell Chrome Launcher" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Check if port is already listening
$activeConn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($activeConn) {
    Write-Host "✅ Chrome Remote Debugging is already running on port $port." -ForegroundColor Green
    exit 0
}

# 2. Locate Chrome
$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

$chromeExe = $chromePaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $chromeExe) {
    Write-Host "❌ Google Chrome was not found in standard paths." -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Launching Chrome from: $chromeExe" -ForegroundColor Yellow
if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

$arguments = @(
    "--remote-debugging-port=$port",
    "--remote-allow-origins=*",
    "--user-data-dir=$profileDir",
    "--no-first-run",
    "--no-default-browser-check",
    "https://x.com/home"
)

Start-Process -FilePath $chromeExe -ArgumentList $arguments

Start-Sleep -Seconds 2

$activeConn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($activeConn) {
    Write-Host "🎉 Chrome successfully launched on http://127.0.0.1:$port" -ForegroundColor Green
    Write-Host "💡 Note: If not logged in, please complete a one-time login to X.com in the opened browser window." -ForegroundColor Yellow
} else {
    Write-Host "⚠️ Chrome process started. Please verify http://127.0.0.1:$port/json/version" -ForegroundColor Yellow
}
