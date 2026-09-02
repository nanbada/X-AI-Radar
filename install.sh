#!/usr/bin/env bash
# ==============================================================================
# X-AI-Radar & Edu-Blog Radar One-Click macOS / Linux Installer
# ==============================================================================

set -e

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================================"
echo "📡 [X-AI-Radar] macOS / Linux Environment Setup"
echo "========================================================"

# 1. Check Python
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "❌ Python 3.10+ is required. Please install Python."
    exit 1
fi

echo "✅ Python detected: $($PYTHON_CMD --version)"

# 2. Permissions
chmod +x "$BASE_DIR"/radar.py "$BASE_DIR"/run.sh "$BASE_DIR"/scripts/*.sh "$BASE_DIR"/scripts/*.py 2>/dev/null || true

# 3. Initialize .env
if [ ! -f "$BASE_DIR/.env" ] && [ -f "$BASE_DIR/.env.example" ]; then
    cp "$BASE_DIR/.env.example" "$BASE_DIR/.env"
    echo "📝 Created .env configuration file from template."
fi

# 4. Install dependencies
echo "📦 Installing required Python dependencies..."
$PYTHON_CMD -m pip install --quiet -r "$BASE_DIR/requirements.txt"

echo "========================================================"
echo "🎉 Setup completed successfully!"
echo "👉 Launch Chrome Debugger: ./scripts/launch_chrome.sh"
echo "👉 Run AI Tech Radar:      python3 radar.py --ai"
echo "👉 Run Edu-Blog Radar:     python3 radar.py --edu"
echo "👉 Run Everything:         ./run.sh"
echo "========================================================"
