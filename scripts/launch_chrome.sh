#!/usr/bin/env bash

# ==============================================================================
# Chrome Remote Debugging Mode Launcher for X-AI-Radar
# Port: 9223 | Profile: $HOME/chrome_agent_profile
# ==============================================================================

PORT=9223
PROFILE_DIR="$HOME/chrome_agent_profile"

# Check if port 9223 is already open and listening
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Chrome Remote Debugging is already running on port $PORT."
    exit 0
fi

echo "🚀 Launching Chrome in Remote Debugging mode (Port: $PORT)..."
mkdir -p "$PROFILE_DIR"

OS="$(uname -s)"
case "$OS" in
    Darwin*)
        # macOS
        /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
            --remote-debugging-port=$PORT \
            --remote-allow-origins="*" \
            --user-data-dir="$PROFILE_DIR" \
            --no-first-run \
            --no-default-browser-check \
            https://x.com/home >/dev/null 2>&1 &
        ;;
    Linux*)
        # Linux
        google-chrome \
            --remote-debugging-port=$PORT \
            --remote-allow-origins="*" \
            --user-data-dir="$PROFILE_DIR" \
            --no-first-run \
            https://x.com/home >/dev/null 2>&1 &
        ;;
    CYGWIN*|MINGW*|MSYS*)
        # Windows / Git Bash
        "/c/Program Files/Google/Chrome/Application/chrome.exe" \
            --remote-debugging-port=$PORT \
            --remote-allow-origins="*" \
            --user-data-dir="C:\\chrome_agent_profile" \
            https://x.com/home &
        ;;
    *)
        echo "❌ Unsupported operating system: $OS"
        exit 1
        ;;
esac

sleep 2
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "🎉 Chrome successfully launched on http://127.0.0.1:$PORT"
    echo "💡 Note: If not logged in, please complete a one-time login in the opened window."
else
    echo "⚠️ Chrome process initiated. Please check http://127.0.0.1:$PORT/json/version"
fi
