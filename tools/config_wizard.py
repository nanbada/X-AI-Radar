#!/usr/bin/env python3
"""
==============================================================================
⚙️ X-AI-Radar & Edu-Blog Radar Interactive Configuration Wizard
==============================================================================
Easily manage search topics, target sources, and notification channels.
"""

import html
import json
import os
import sys
import urllib.parse
import urllib.request
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
ENV_PATH = os.path.join(BASE_DIR, ".env")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
    print("💾 Saved changes to config.yaml!")

def load_env():
    env_vars = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars

def save_env(env_vars):
    lines = [
        "# ==============================================================================",
        "# X-AI-Radar & Edu-Blog Radar Secret Credentials (Git Ignored)",
        "# ==============================================================================",
        ""
    ]
    for k, v in env_vars.items():
        lines.append(f'{k}="{v}"')
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("💾 Saved credentials to .env!")

def show_current_settings():
    cfg = load_config()
    env_vars = load_env()
    print("\n" + "="*65)
    print("📋 CURRENT ACTIVE CONFIGURATION & CHANNELS")
    print("="*65)
    print("📡 [1. X-AI-Radar Search Queries]")
    for i, q in enumerate(cfg.get("browser", {}).get("search_queries", []), 1):
        print(f"  {i}. {q}")
    
    print("\n🏷️ [2. Topic Boost Keywords (+150 pts)]")
    kws = cfg.get("topics", {}).get("boost_keywords", [])
    print(f"  {', '.join(kws[:12])} ... ({len(kws)} total)")
    
    print("\n🚫 [3. Exclude Noise Keywords]")
    ex_kws = cfg.get("topics", {}).get("exclude_keywords", [])
    print(f"  {', '.join(ex_kws[:10])} ... ({len(ex_kws)} total)")

    print("\n🔔 [4. Notification & Webhook Endpoints]")
    tg_ai = env_vars.get("TELEGRAM_BOT_TOKEN") or "(Not configured)"
    tg_ai_id = env_vars.get("TELEGRAM_CHAT_ID") or "(Not configured)"
    tg_edu = env_vars.get("EDU_TELEGRAM_BOT_TOKEN") or "(Not configured)"
    tg_edu_id = env_vars.get("EDU_TELEGRAM_CHAT_ID") or "(Not configured)"
    slack = env_vars.get("SLACK_WEBHOOK_URL") or "(Not configured)"
    discord = env_vars.get("DISCORD_WEBHOOK_URL") or "(Not configured)"
    
    print(f"  • AI Tech Telegram Bot Token:     {tg_ai[:12]}... (Chat ID: {tg_ai_id})")
    print(f"  • Edu-Blog Telegram Bot Token:    {tg_edu[:12]}... (Chat ID: {tg_edu_id})")
    print(f"  • Slack Webhook:                  {slack if slack != '(Not configured)' else 'Off'}")
    print(f"  • Discord Webhook:                {discord if discord != '(Not configured)' else 'Off'}")
    print("="*65 + "\n")

def manage_search_queries():
    cfg = load_config()
    queries = cfg.get("browser", {}).get("search_queries", [])
    while True:
        print("\n--- 📡 Manage X.com Search Queries ---")
        for i, q in enumerate(queries, 1):
            print(f"  [{i}] {q}")
        print("  [A] Add New Query")
        print("  [D] Delete a Query")
        print("  [B] Back to Main Menu")
        
        choice = input("\nSelect an option: ").strip().upper()
        if choice == "A":
            print("\n💡 Tip: You can use search operators like min_faves:50, lang:en, OR, AND")
            new_q = input("Enter search query or full URL: ").strip()
            if new_q:
                if not new_q.startswith("http"):
                    new_q = "https://x.com/search?q=" + urllib.parse.quote(new_q) + "&f=live"
                queries.append(new_q)
                cfg["browser"]["search_queries"] = queries
                save_config(cfg)
        elif choice == "D":
            idx = input("Enter index to delete: ").strip()
            try:
                idx = int(idx) - 1
                if 0 <= idx < len(queries):
                    removed = queries.pop(idx)
                    cfg["browser"]["search_queries"] = queries
                    save_config(cfg)
                    print(f"🗑️ Removed: {removed}")
            except:
                print("Invalid index.")
        elif choice == "B":
            break

def manage_keywords():
    cfg = load_config()
    boost = cfg.get("topics", {}).get("boost_keywords", [])
    exclude = cfg.get("topics", {}).get("exclude_keywords", [])
    
    while True:
        print("\n--- 🏷️ Manage Boost & Exclude Keywords ---")
        print(f"  [1] Add Boost Keyword (Current: {len(boost)} keywords)")
        print(f"  [2] Add Exclude/Negative Keyword (Current: {len(exclude)} keywords)")
        print("  [B] Back")
        
        choice = input("\nSelect an option: ").strip()
        if choice == "1":
            kw = input("Enter keyword to boost (+150 pts): ").strip()
            if kw and kw not in boost:
                boost.append(kw)
                cfg["topics"]["boost_keywords"] = boost
                save_config(cfg)
        elif choice == "2":
            kw = input("Enter keyword to exclude/filter out: ").strip()
            if kw and kw not in exclude:
                exclude.append(kw)
                cfg["topics"]["exclude_keywords"] = exclude
                save_config(cfg)
        elif choice.upper() == "B":
            break

def manage_notification_channels():
    env_vars = load_env()
    while True:
        print("\n--- 🔔 Manage Notification & Webhook Channels ---")
        print("  [1] Set AI Tech Telegram Bot (@Radar4All_bot)")
        print("  [2] Set Edu-Blog Telegram Bot (@edunewsradar_bot)")
        print("  [3] Set Slack Webhook URL")
        print("  [4] Set Discord Webhook URL")
        print("  [5] Test Channel Delivery")
        print("  [B] Back")
        
        choice = input("\nSelect an option: ").strip()
        if choice == "1":
            token = input("Enter AI Telegram Bot Token: ").strip()
            chat_id = input("Enter Target Chat ID: ").strip()
            if token: env_vars["TELEGRAM_BOT_TOKEN"] = token
            if chat_id: env_vars["TELEGRAM_CHAT_ID"] = chat_id
            save_env(env_vars)
        elif choice == "2":
            token = input("Enter Edu Telegram Bot Token: ").strip()
            chat_id = input("Enter Target Chat ID: ").strip()
            if token: env_vars["EDU_TELEGRAM_BOT_TOKEN"] = token
            if chat_id: env_vars["EDU_TELEGRAM_CHAT_ID"] = chat_id
            save_env(env_vars)
        elif choice == "3":
            url = input("Enter Slack Webhook URL (leave empty to disable): ").strip()
            env_vars["SLACK_WEBHOOK_URL"] = url
            save_env(env_vars)
        elif choice == "4":
            url = input("Enter Discord Webhook URL (leave empty to disable): ").strip()
            env_vars["DISCORD_WEBHOOK_URL"] = url
            save_env(env_vars)
        elif choice == "5":
            test_notifications(env_vars)
        elif choice.upper() == "B":
            break

def test_notifications(env_vars):
    print("\n🧪 Sending test pings...")
    
    # 1. AI Telegram
    tg_token = env_vars.get("TELEGRAM_BOT_TOKEN")
    tg_chat = env_vars.get("TELEGRAM_CHAT_ID")
    if tg_token and tg_chat:
        try:
            url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
            payload = json.dumps({"chat_id": tg_chat, "text": "✅ [Test] X-AI-Radar Tech Bot connected successfully!"}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as res:
                print("  ✅ AI Tech Telegram Bot: OK!")
        except Exception as e:
            print(f"  ❌ AI Tech Telegram Bot failed: {e}")
            
    # 2. Edu Telegram
    edu_token = env_vars.get("EDU_TELEGRAM_BOT_TOKEN")
    edu_chat = env_vars.get("EDU_TELEGRAM_CHAT_ID")
    if edu_token and edu_chat:
        try:
            url = f"https://api.telegram.org/bot{edu_token}/sendMessage"
            payload = json.dumps({"chat_id": edu_chat, "text": "✅ [Test] Edu-Blog Radar Bot connected successfully!"}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as res:
                print("  ✅ Edu-Blog Telegram Bot: OK!")
        except Exception as e:
            print(f"  ❌ Edu-Blog Telegram Bot failed: {e}")

def main():
    while True:
        print("\n========================================================")
        print("⚙️ X-AI-Radar & Edu-Blog Radar Configuration Wizard")
        print("========================================================")
        print("  [1] 📋 View Current Active Configuration")
        print("  [2] 📡 Manage X.com Search Queries & Sources")
        print("  [3] 🏷️ Manage Boost & Exclude Keywords")
        print("  [4] 🔔 Configure Telegram / Slack / Discord Webhooks")
        print("  [5] 🧪 Test All Active Notification Channels")
        print("  [Q] Exit Wizard")
        print("========================================================")
        
        choice = input("Enter your choice: ").strip().upper()
        if choice == "1":
            show_current_settings()
        elif choice == "2":
            manage_search_queries()
        elif choice == "3":
            manage_keywords()
        elif choice == "4":
            manage_notification_channels()
        elif choice == "5":
            test_notifications(load_env())
        elif choice in ["Q", "EXIT", "QUIT"]:
            print("👋 Wizard closed.")
            break

if __name__ == "__main__":
    main()
