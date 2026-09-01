#!/usr/bin/env python3
"""
Multi-Channel Webhook Notifier for X-AI-Radar
Dispatches Top 3 Daily Highlights to Slack, Discord, and Telegram endpoints.
Supports loading secrets securely from local .env or config.yaml.
"""

import html
import json
import os
import sys
import urllib.request
import yaml

def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars

def send_notifications(summary_data):
    """
    Reads webhook configurations and sends formatted alerts.
    """
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    if not os.path.exists(config_path):
        return
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    notify_cfg = config.get("notifications", {})
    if not notify_cfg.get("enabled", False):
        return
        
    env_vars = load_env_file()
    webhooks = notify_cfg.get("webhooks", {})
    slack_url = env_vars.get("SLACK_WEBHOOK_URL") or webhooks.get("slack")
    discord_url = env_vars.get("DISCORD_WEBHOOK_URL") or webhooks.get("discord")
    tg_token = env_vars.get("TELEGRAM_BOT_TOKEN") or webhooks.get("telegram_bot_token")
    tg_chat_id = env_vars.get("TELEGRAM_CHAT_ID") or webhooks.get("telegram_chat_id")
    
    top_posts = summary_data.get("top_posts", [])[:3]
    today_str = summary_data.get("date", "Today")
    report_file = summary_data.get("report_file", "")
    
    # Compose Plain / Markdown Text for Slack & Discord
    lines = [
        f"📡 *[X-AI-Radar] AI & Agents Daily Radar ({today_str})*",
        f"🔗 Full Report: `{report_file}`",
        "───────────────────────────────"
    ]
    for i, p in enumerate(top_posts, 1):
        m = p.get("parsedMetrics", {})
        lines.append(f"*{i}. {p.get('handle')}* (Score: {p.get('heatScore'):,}) | {m.get('views',0):,} Views")
        lines.append(f"> {p.get('text', '')[:140].replace(chr(10), ' ')}...")
        lines.append(f"<{p.get('tweetUrl')}|View Tweet>\n")
        
    msg_text = "\n".join(lines)
    
    # 1. Slack Webhook Dispatch
    if slack_url and slack_url.startswith("http"):
        try:
            payload = json.dumps({"text": msg_text}).encode("utf-8")
            req = urllib.request.Request(slack_url, data=payload, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5)
            print("✅ Sent notification to Slack.")
        except Exception as e:
            print(f"⚠️ Slack notification error: {e}", file=sys.stderr)
            
    # 2. Discord Webhook Dispatch
    if discord_url and discord_url.startswith("http"):
        try:
            payload = json.dumps({"content": msg_text.replace("*", "**")}).encode("utf-8")
            req = urllib.request.Request(discord_url, data=payload, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5)
            print("✅ Sent notification to Discord.")
        except Exception as e:
            print(f"⚠️ Discord notification error: {e}", file=sys.stderr)
            
    # 3. Telegram Bot Dispatch (HTML Mode for robust parsing)
    if tg_token and tg_chat_id:
        try:
            tg_lines = [
                f"📡 <b>[X-AI-Radar] AI &amp; Agents Daily Radar ({html.escape(today_str)})</b>",
                f"📁 <i>Report: {html.escape(os.path.basename(report_file))}</i>",
                "───────────────────────────────"
            ]
            for i, p in enumerate(top_posts, 1):
                m = p.get("parsedMetrics", {})
                badge = p.get("badge", "✨ NEW")
                handle = html.escape(str(p.get("handle", "@user")))
                snippet = html.escape(str(p.get("text", "")[:130]).replace("\n", " "))
                url = p.get("tweetUrl") or f"https://x.com/{handle.replace('@', '')}"
                
                tg_lines.append(f"<b>{i}. {handle}</b> <code>[{badge}]</code> (Score: {p.get('heatScore'):,})")
                tg_lines.append(f"👁 {m.get('views', 0):,} Views | ❤️ {m.get('likes', 0):,} Likes | 🔖 {m.get('bookmarks', 0):,} BMs")
                tg_lines.append(f"💬 <i>\"{snippet}...\"</i>")
                tg_lines.append(f"🔗 <a href=\"{url}\">View on X</a>\n")
                
            tg_html = "\n".join(tg_lines)
            
            tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
            payload = json.dumps({
                "chat_id": tg_chat_id,
                "text": tg_html,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }).encode("utf-8")
            req = urllib.request.Request(tg_url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as res:
                print("✅ Live Report dispatched successfully to Telegram!")
        except Exception as e:
            print(f"⚠️ Telegram notification error: {e}", file=sys.stderr)

if __name__ == "__main__":
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    sample_report = {
        "date": today_str,
        "report_file": f"reports/x-ai-radar-{today_str}.md",
        "top_posts": [
            {
                "handle": "@farzyness",
                "heatScore": 6466.0,
                "badge": "🚀 RISING",
                "text": "The ultimate Grok @bot set up for me is to filter EVERYTHING through one agent and hide everything else. Master agent coordinates specialized sub-agents...",
                "tweetUrl": "https://x.com/farzyness/status/2094810782697398294",
                "parsedMetrics": {"views": 69000, "likes": 332, "bookmarks": 42}
            }
        ]
    }
    send_notifications(sample_report)
