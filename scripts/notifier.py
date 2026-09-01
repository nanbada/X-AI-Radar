#!/usr/bin/env python3
"""
Multi-Channel Webhook Notifier for X-AI-Radar
Dispatches Top 3 Daily Highlights to Slack, Discord, and Telegram endpoints.
"""

import json
import os
import sys
import urllib.request
import yaml

def send_notifications(summary_data):
    """
    Reads webhook configurations and sends formatted markdown alerts.
    """
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    if not os.path.exists(config_path):
        return
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    notify_cfg = config.get("notifications", {})
    if not notify_cfg.get("enabled", False):
        return
        
    webhooks = notify_cfg.get("webhooks", {})
    slack_url = webhooks.get("slack")
    discord_url = webhooks.get("discord")
    tg_token = webhooks.get("telegram_bot_token")
    tg_chat_id = webhooks.get("telegram_chat_id")
    
    top_posts = summary_data.get("top_posts", [])[:3]
    today_str = summary_data.get("date", "Today")
    report_file = summary_data.get("report_file", "")
    
    # Compose notification text payload
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
            
    # 3. Telegram Bot Dispatch
    if tg_token and tg_chat_id:
        try:
            tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
            payload = json.dumps({
                "chat_id": tg_chat_id,
                "text": msg_text,
                "parse_mode": "Markdown"
            }).encode("utf-8")
            req = urllib.request.Request(tg_url, data=payload, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5)
            print("✅ Sent notification to Telegram.")
        except Exception as e:
            print(f"⚠️ Telegram notification error: {e}", file=sys.stderr)

if __name__ == "__main__":
    sample = {
        "date": "2026-09-02",
        "report_file": "reports/x-ai-radar-2026-09-02.md",
        "top_posts": [
            {
                "handle": "@elonmusk",
                "heatScore": 27616.7,
                "text": "Automatic token optimization to lower your Grok @Bot cost will be added soon",
                "tweetUrl": "https://x.com/elonmusk",
                "parsedMetrics": {"views": 4000000}
            }
        ]
    }
    send_notifications(sample)
