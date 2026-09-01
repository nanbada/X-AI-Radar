#!/usr/bin/env python3
"""
Multi-Channel Webhook Notifier for X-AI-Radar
Dispatches Top 3 Daily Highlights to Slack, Discord, and Telegram endpoints.
Translates foreign language posts into natural Korean for the user.
"""

import html
import json
import os
import sys
import urllib.parse
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

def translate_to_korean(text):
    """
    Translates English / foreign text into Korean using fast, zero-dependency translation.
    """
    if not text:
        return ""
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ko&dt=t&q=" + urllib.parse.quote(text[:300])
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
        with urllib.request.urlopen(req, timeout=4) as res:
            data = json.loads(res.read().decode("utf-8"))
            return "".join([part[0] for part in data[0] if part[0]])
    except Exception as e:
        print(f"⚠️ Translation fallback ({e})", file=sys.stderr)
        return text

def send_notifications(summary_data):
    """
    Reads webhook configurations and sends formatted alerts with Korean translation.
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
    
    # 1. Slack / Discord Markdown Text (with Korean Translation)
    lines = [
        f"📡 *[X-AI-Radar] AI & Agents 데일리 핫이슈 ({today_str})*",
        f"📁 전체 리포트: `{os.path.basename(report_file)}`",
        "───────────────────────────────"
    ]
    for i, p in enumerate(top_posts, 1):
        m = p.get("parsedMetrics", {})
        badge = p.get("badge", "✨ NEW")
        raw_text = p.get("text", "")[:160]
        ko_text = translate_to_korean(raw_text).replace("\n", " ")
        
        lines.append(f"*{i}. {p.get('handle')}* `[{badge}]` (점수: {p.get('heatScore'):,})")
        lines.append(f"• 지표: {m.get('views',0):,} Views | {m.get('likes',0):,} Likes | {m.get('bookmarks',0):,} BMs")
        lines.append(f"> 🇰🇷 *요약*: {ko_text}")
        lines.append(f"<{p.get('tweetUrl')}|원문 트윗 보기>\n")
        
    msg_text = "\n".join(lines)
    
    if slack_url and slack_url.startswith("http"):
        try:
            payload = json.dumps({"text": msg_text}).encode("utf-8")
            req = urllib.request.Request(slack_url, data=payload, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5)
            print("✅ Sent notification to Slack.")
        except Exception as e:
            print(f"⚠️ Slack notification error: {e}", file=sys.stderr)
            
    if discord_url and discord_url.startswith("http"):
        try:
            payload = json.dumps({"content": msg_text.replace("*", "**")}).encode("utf-8")
            req = urllib.request.Request(discord_url, data=payload, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5)
            print("✅ Sent notification to Discord.")
        except Exception as e:
            print(f"⚠️ Discord notification error: {e}", file=sys.stderr)
            
    # 2. Telegram Bot Dispatch (HTML Mode with Korean Translation)
    if tg_token and tg_chat_id:
        try:
            tg_lines = [
                f"📡 <b>[X-AI-Radar] 오늘의 AI &amp; Agents 핫이슈 요약 ({html.escape(today_str)})</b>",
                f"📁 <i>전체 리포트: {html.escape(os.path.basename(report_file))}</i>",
                "───────────────────────────────"
            ]
            for i, p in enumerate(top_posts, 1):
                m = p.get("parsedMetrics", {})
                badge = p.get("badge", "✨ NEW")
                handle = html.escape(str(p.get("handle", "@user")))
                raw_text = str(p.get("text", "")[:160])
                ko_text = html.escape(translate_to_korean(raw_text).replace("\n", " "))
                url = p.get("tweetUrl") or f"https://x.com/{handle.replace('@', '')}"
                
                tg_lines.append(f"<b>{i}. {handle}</b> <code>[{badge}]</code> (열도 점수: {p.get('heatScore'):,})")
                tg_lines.append(f"👁 {m.get('views', 0):,} Views | ❤️ {m.get('likes', 0):,} Likes | 🔖 {m.get('bookmarks', 0):,} BMs")
                tg_lines.append(f"🇰🇷 <b>핵심 요약</b>: <i>\"{ko_text}...\"</i>")
                tg_lines.append(f"🔗 <a href=\"{url}\">트윗 원문 보기</a>\n")
                
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
                print("✅ Live Korean-translated Report dispatched to Telegram!")
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
                "text": "The ultimate Grok @bot set up for me is to filter EVERYTHING through one agent and hide everything else. That master agent coordinates specialized sub-agents for your process and life.",
                "tweetUrl": "https://x.com/farzyness/status/2094810782697398294",
                "parsedMetrics": {"views": 69000, "likes": 332, "bookmarks": 42}
            },
            {
                "handle": "@binance",
                "heatScore": 1353.0,
                "badge": "🚀 RISING",
                "text": "Introducing the Binance Agent OS Mini Hackathon. $60,000 USDC Prize Pool: Build an AI agent with Agent OS & connect your MCPs to trade automatically.",
                "tweetUrl": "https://x.com/binance/status/2094810011557838988",
                "parsedMetrics": {"views": 78000, "likes": 106, "bookmarks": 85}
            }
        ]
    }
    send_notifications(sample_report)
