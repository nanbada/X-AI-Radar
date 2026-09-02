#!/usr/bin/env python3
"""
==============================================================================
📦 Multi-OS Release Packaging Module for X-AI-Radar & Edu-Blog Radar
==============================================================================
Creates isolated, production-ready distribution archives for:
  - Windows (ZIP archive with run.bat, install.bat, launch_chrome.bat)
  - macOS (TAR.GZ archive with run.sh, install.sh, launch_chrome.sh)
  - Linux (TAR.GZ archive with systemd / cron integration)
"""

import argparse
import json
import os
import shutil
import sys
import tarfile
import zipfile
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(BASE_DIR, "dist")
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

VERSION = config.get("project", {}).get("version", "2.2.0")
APP_NAME = "X-AI-Radar"

# Files and directories to include in release packages
CORE_FILES = [
    "radar.py",
    "requirements.txt",
    ".env.example",
    "config.yaml",
    "README.md",
    "README_KO.md",
    "AGENTS.md",
    "SKILL.md",
]

CORE_DIRS = [
    "templates",
    "scripts",
]

EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".env",
    "history.json",
    ".DS_Store",
    "*.log"
]

def clean_dist():
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR, exist_ok=True)

def should_exclude(path):
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*") and path.endswith(pattern[1:]):
            return True
        elif pattern in path:
            return True
    return False

def build_staging_dir(target_os):
    staging_name = f"{APP_NAME}-v{VERSION}-{target_os}"
    staging_path = os.path.join(DIST_DIR, staging_name)
    os.makedirs(staging_path, exist_ok=True)
    
    # 1. Copy Core Files
    for f in CORE_FILES:
        src = os.path.join(BASE_DIR, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(staging_path, f))
            
    # 2. Copy Core Dirs
    for d in CORE_DIRS:
        src_dir = os.path.join(BASE_DIR, d)
        dst_dir = os.path.join(staging_path, d)
        if os.path.exists(src_dir):
            shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
            
    # 3. Create clean data & reports placeholder dirs
    os.makedirs(os.path.join(staging_path, "data"), exist_ok=True)
    with open(os.path.join(staging_path, "data", ".gitkeep"), "w") as f:
        pass
    os.makedirs(os.path.join(staging_path, "reports"), exist_ok=True)
    with open(os.path.join(staging_path, "reports", ".gitkeep"), "w") as f:
        pass

    # 4. OS-specific files
    if target_os == "windows":
        for script in ["run.bat", "install.bat"]:
            src = os.path.join(BASE_DIR, script)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(staging_path, script))
    else:
        for script in ["run.sh", "install.sh"]:
            src = os.path.join(BASE_DIR, script)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(staging_path, script))
                os.chmod(os.path.join(staging_path, script), 0o755)

    return staging_path, staging_name

def package_windows():
    print("📦 [1/3] Packaging Windows Release (x64)...")
    staging_path, staging_name = build_staging_dir("windows-x64")
    zip_path = os.path.join(DIST_DIR, f"{staging_name}.zip")
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(staging_path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, DIST_DIR)
                zipf.write(full_path, rel_path)
                
    shutil.rmtree(staging_path)
    print(f"  ✅ Created: {zip_path} ({os.path.getsize(zip_path):,} bytes)")
    return zip_path

def package_macos():
    print("📦 [2/3] Packaging macOS Release (Universal)...")
    staging_path, staging_name = build_staging_dir("macos-universal")
    tar_path = os.path.join(DIST_DIR, f"{staging_name}.tar.gz")
    
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(staging_path, arcname=staging_name)
        
    shutil.rmtree(staging_path)
    print(f"  ✅ Created: {tar_path} ({os.path.getsize(tar_path):,} bytes)")
    return tar_path

def package_linux():
    print("📦 [3/3] Packaging Linux Release (x64)...")
    staging_path, staging_name = build_staging_dir("linux-x64")
    tar_path = os.path.join(DIST_DIR, f"{staging_name}.tar.gz")
    
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(staging_path, arcname=staging_name)
        
    shutil.rmtree(staging_path)
    print(f"  ✅ Created: {tar_path} ({os.path.getsize(tar_path):,} bytes)")
    return tar_path

def generate_manifest(packages):
    manifest_path = os.path.join(DIST_DIR, "RELEASE_MANIFEST.json")
    manifest = {
        "project": APP_NAME,
        "version": VERSION,
        "release_packages": [
            {
                "file": os.path.basename(p),
                "size_bytes": os.path.getsize(p),
                "path": p
            } for p in packages
        ]
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"📋 Manifest generated: {manifest_path}")

def main():
    parser = argparse.ArgumentParser(description="Multi-OS Release Packager")
    parser.add_argument("--os", choices=["all", "windows", "macos", "linux"], default="all", help="Target OS to package")
    args = parser.parse_args()
    
    print(f"🚀 Starting Multi-OS Release Packaging for {APP_NAME} (v{VERSION})...")
    clean_dist()
    
    packages = []
    if args.os in ["all", "windows"]:
        packages.append(package_windows())
    if args.os in ["all", "macos"]:
        packages.append(package_macos())
    if args.os in ["all", "linux"]:
        packages.append(package_linux())
        
    generate_manifest(packages)
    print("\n🎉 Multi-OS Release Packaging successfully completed! Check dist/ directory.")

if __name__ == "__main__":
    main()
