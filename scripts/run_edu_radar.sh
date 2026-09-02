#!/usr/bin/env bash
echo "🎓 [Edu-Blog Radar] Generating Today's Top 3 Educational Blog Items..."
python3 "$(dirname "$0")/edu_collector.py"
