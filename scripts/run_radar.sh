#!/usr/bin/env bash

# ==============================================================================
# X-AI-Radar Environment Checker & Runner Helper
# ==============================================================================

PORT=9223
CONFIG_FILE="$(dirname "$0")/../config.yaml"

echo "========================================================"
echo "📡 X-AI-Radar Environment Checker"
echo "========================================================"

# 1. Validate configuration file existence
if [ -f "$CONFIG_FILE" ]; then
    echo "✅ Configuration found at $CONFIG_FILE"
else
    echo "❌ Missing config.yaml at $CONFIG_FILE"
    exit 1
fi

# 2. Check if Chrome Remote Debugging port 9223 is active
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Chrome CDP Port $PORT is active and listening."
else
    echo "⚠️ Chrome CDP Port $PORT is NOT active."
    echo "👉 Running scripts/launch_chrome.sh to start browser..."
    "$(dirname "$0")/launch_chrome.sh"
fi

echo "--------------------------------------------------------"
echo "✨ Ready for Antigravity Browser Subagent execution."
echo "👉 In Antigravity Chat, type: /x-ai-radar"
echo "👉 Or schedule daily: /schedule (Cron: 15 8 * * *)"
echo "========================================================"
