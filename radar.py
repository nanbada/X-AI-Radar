#!/usr/bin/env python3
"""
==============================================================================
📡 X-AI-Radar & Edu-Blog Radar Unified CLI Orchestrator
==============================================================================
Usage:
    python radar.py [OPTIONS]

Options:
    --all, -A       Run both AI Tech Radar and Edu-Blog Radar sequentially (Default)
    --ai, -a        Run AI & Tech Intelligence Radar (X + GitHub + HN)
    --edu, -e       Run Educational & Parent Blog Radar (Naver Edu Trends)
    --browser, -b   Launch Chrome in Remote Debugging Mode (Port 9223)
    --help, -h      Show this help message
"""

import argparse
import os
import subprocess
import sys
import platform

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

def launch_browser():
    """Launches Chrome in Remote Debugging Mode based on current OS."""
    current_os = platform.system().lower()
    print("🚀 [Radar CLI] Launching Chrome Remote Debugging (Port: 9223)...")
    if "windows" in current_os:
        bat_script = os.path.join(SCRIPTS_DIR, "launch_chrome.bat")
        subprocess.run(["cmd.exe", "/c", bat_script])
    else:
        sh_script = os.path.join(SCRIPTS_DIR, "launch_chrome.sh")
        subprocess.run(["bash", sh_script])

def run_ai_radar():
    """Runs the AI & Tech Intelligence Radar."""
    print("\n" + "="*60)
    print("📡 [1/2] Running X-AI-Radar (AI & Tech Intelligence)...")
    print("="*60)
    script_path = os.path.join(SCRIPTS_DIR, "collector.py")
    subprocess.run([sys.executable, script_path])

def run_edu_radar():
    """Runs the Educational & Parent Blog Radar."""
    print("\n" + "="*60)
    print("🎓 [2/2] Running Edu-Blog Radar (Elementary/Middle Blog Ideation)...")
    print("="*60)
    script_path = os.path.join(SCRIPTS_DIR, "edu_collector.py")
    subprocess.run([sys.executable, script_path])

def main():
    parser = argparse.ArgumentParser(
        description="📡 X-AI-Radar & Edu-Blog Radar Unified CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python radar.py --all         # Run both intelligence radars
  python radar.py --ai          # Run AI & Tech Radar only
  python radar.py --edu         # Run Edu-Blog Radar only
  python radar.py --browser     # Launch Debugging Chrome
        """
    )
    parser.add_argument("--all", "-A", action="store_true", help="Run both AI and Edu radars (Default)")
    parser.add_argument("--ai", "-a", action="store_true", help="Run AI & Tech Intelligence Radar")
    parser.add_argument("--edu", "-e", action="store_true", help="Run Educational Blog Radar")
    parser.add_argument("--browser", "-b", action="store_true", help="Launch Chrome Remote Debugging Mode")
    
    args = parser.parse_args()
    
    if args.browser:
        launch_browser()
        return

    if args.ai:
        run_ai_radar()
    elif args.edu:
        run_edu_radar()
    else:
        # Default: Run both or when --all is specified
        run_ai_radar()
        run_edu_radar()

if __name__ == "__main__":
    main()
