#!/usr/bin/env python3
"""
Telegram Auto-Link Helper for X-AI-Radar
Polls getUpdates to detect user's /start message, saves chat_id to config.yaml, and sends welcome alert.
"""

import json
import os
import sys
import time
import urllib.request
import yaml

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")

def check_chat_id():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        with urllib.request.urlopen(url, timeout=5) as res:
            data = json.loads(res.read().decode())
            results = data.get("result", [])
            if results:
                # Get the latest message's chat ID
                last_msg = results[-1].get("message") or results[-1].get("channel_post") or results[-1].get("my_chat_member", {}).get("chat")
                if last_msg:
                    chat_id = last_msg.get("chat", {}).get("id") or last_msg.get("id")
                    username = last_msg.get("chat", {}).get("first_name") or last_msg.get("chat", {}).get("title", "User")
                    return chat_id, username
    except Exception as e:
        print(f"Error checking updates: {e}", file=sys.stderr)
    return None, None

def save_and_notify(chat_id, user_name):
    # 1. Update config.yaml
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
        
    cfg["notifications"]["enabled"] = True
    cfg["notifications"]["webhooks"]["telegram_bot_token"] = TOKEN
    cfg["notifications"]["webhooks"]["telegram_chat_id"] = str(chat_id)
    
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
        
    print(f"✅ Updated config.yaml with Chat ID: {chat_id}")
    
    # 2. Send Welcome Test Notification
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    welcome_text = f"""🎉 *[X-AI-Radar] 텔레그램 알림 연동 완료!*

안녕하세요, {user_name}님!
X-AI-Radar가 성공적으로 텔레그램 봇(@Radar4All_bot)에 연결되었습니다.

• *알림 주기*: 매일 오전 08:15 KST
• *내용*: 최근 24시간 X AI/Agents 핫이슈, GitHub Trending, Hacker News Top 3
• *상태*: 정상 활성화 (Active)

내일 아침 08:15부터 최신 브리핑이 이곳으로 자동 발송됩니다!"""

    payload = json.dumps({
        "chat_id": chat_id,
        "text": welcome_text,
        "parse_mode": "Markdown"
    }).encode("utf-8")
    
    req = urllib.request.Request(send_url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as res:
        print("🎉 Welcome message sent successfully to Telegram!")

if __name__ == "__main__":
    chat_id, user_name = check_chat_id()
    if chat_id:
        save_and_notify(chat_id, user_name)
    else:
        print("WAITING_FOR_USER_START")
