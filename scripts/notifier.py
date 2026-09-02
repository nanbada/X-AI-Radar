#!/usr/bin/env python3
"""
Multi-Channel Webhook Notifier for X-AI-Radar
Dispatches Top 3 Daily Highlights to Slack, Discord, and Telegram endpoints.
Attaches the actual .md report document directly into the Telegram chat room.
"""

import html
import json
import os
import sys
import urllib.parse
import urllib.request
import uuid
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

def send_telegram_document(token, chat_id, file_path, caption=""):
    """
    Attaches the physical markdown (.md) report file directly into the Telegram chat room.
    """
    if not os.path.exists(file_path):
        return
        
    filename = os.path.basename(file_path)
    boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
    
    with open(file_path, "rb") as f:
        file_content = f.read()
        
    body = []
    body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode('utf-8'))
    if caption:
        body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode('utf-8'))
    body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="document"; filename="{filename}"\r\nContent-Type: text/markdown; charset=utf-8\r\n\r\n'.encode('utf-8'))
    body.append(file_content)
    body.append(f'\r\n--{boundary}--\r\n'.encode('utf-8'))
    
    payload = b''.join(body)
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
    
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            print(f"📎 Attached {filename} document directly into Telegram chat!")
    except Exception as e:
        print(f"⚠️ Telegram document attach error: {e}", file=sys.stderr)

def translate_to_korean(text):
    if not text:
        return ""
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ko&dt=t&q=" + urllib.parse.quote(text[:300])
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as res:
            data = json.loads(res.read().decode("utf-8"))
            return "".join([part[0] for part in data[0] if part[0]])
    except Exception:
        return text

def send_notifications(summary_data):
    """
    Reads webhook configurations and sends formatted alerts with direct Telegram file attachments.
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
    
    # 1. Slack / Discord Markdown Text
    lines = [
        f"📡 *[X-AI-Radar] AI & Agents 데일리 핫이슈 ({today_str})*",
        f"📁 리포트 파일: `{os.path.basename(report_file)}`",
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
            
    # 2. Telegram Bot Dispatch (Summary HTML + Direct .md Attachment)
    if tg_token and tg_chat_id:
        try:
            tg_lines = [
                f"📡 <b>[X-AI-Radar] 오늘의 AI &amp; Agents 핫이슈 요약 ({html.escape(today_str)})</b>",
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
                
            tg_lines.append("───────────────────────────────")
            tg_lines.append("📎 <i>상세 전체 리포트는 아래 첨부된 마크다운 파일을 확인하세요.</i>")
            tg_html = "\n".join(tg_lines)
            
            # Step A: Send clean text summary
            tg_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
            payload = json.dumps({
                "chat_id": tg_chat_id,
                "text": tg_html,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }).encode("utf-8")
            req = urllib.request.Request(tg_url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8):
                print("✅ Live Report text dispatched to Telegram!")
                
            # Step B: Attach the physical .md report file directly in chat
            send_telegram_document(tg_token, tg_chat_id, report_file, caption=f"📄 [X-AI-Radar] {today_str} 일일 전체 리포트 파일")
            
        except Exception as e:
            print(f"⚠️ Telegram notification error: {e}", file=sys.stderr)
