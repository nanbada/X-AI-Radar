# ⚙️ X-AI-Radar & Edu-Blog Radar: Complete Customization & Channel Guide

This guide covers how to customize search sources, topics, keywords, filters, and notification channels (Telegram, Slack, Discord).

---

## 🚀 Quick Interactive Wizard (Recommended)

You can view and modify all active search queries, topics, and notification channels using the built-in interactive wizard:

```bash
python radar.py --config
```

```text
========================================================
⚙️ X-AI-Radar & Edu-Blog Radar Configuration Wizard
========================================================
  [1] 📋 View Current Active Configuration
  [2] 📡 Manage X.com Search Queries & Sources
  [3] 🏷️ Manage Boost & Exclude Keywords
  [4] 🔔 Configure Telegram / Slack / Discord Webhooks
  [5] 🧪 Test All Active Notification Channels
  [Q] Exit Wizard
========================================================
```

---

## 📡 1. Customizing Search Topics & Sources

### A. Modifying X.com Search Queries (`config.yaml`)
X-AI-Radar uses precision search operators to bypass timeline algorithms and gather high-signal posts:

```yaml
browser:
  search_queries:
    # Query 1: Track AI Agents & Reasoning Models (min 50 likes)
    - "https://x.com/search?q=(AI%20OR%20Agents%20OR%20Reasoning%20OR%20MCP)%20min_faves%3A50&f=live"
    
    # Query 2: Track Frameworks (LangGraph, CrewAI, AutoGen)
    - "https://x.com/search?q=(LangGraph%20OR%20CrewAI%20OR%20AutoGen)%20min_faves%3A30&f=live"
```

#### 💡 Useful Search Operators:
- `min_faves:50`: Only posts with 50+ likes (filters out noise).
- `lang:en` or `lang:ko`: Filter by language.
- `-filter:replies`: Exclude reply threads.
- `(TermA OR TermB)`: Boolean union search.

---

### B. Modifying Topic Boost & Exclude Keywords (`config.yaml`)
Posts matching boost keywords receive an automatic **+150.0 score bonus** in Velocity calculations:

```yaml
topics:
  boost_keywords:
    - "Agent"
    - "LangGraph"
    - "CrewAI"
    - "MCP"
    - "Claude"
    - "DeepSeek"

  exclude_keywords:
    - "airdrop"
    - "giveaway"
    - "memecoin"
    - "football"
    - "transfer"
```

---

### C. Modifying Edu-Blog Radar Search Queries (`scripts/adapters/naver_edu.py`)
To change the topics analyzed for the educational blog engine:

```python
SEARCH_QUERIES = [
    "초등 재미있는 공부법",
    "초등 자기주도학습 습관",
    "중등 내신 공부법",
    "중학교 시험 플래너",
    "시즌별 초중등 학습 아이템",
    "학부모 교육 고민 꿀팁"
]
```

---

## 🔔 2. Customizing Notification Channels

All sensitive webhook tokens and chat IDs are securely loaded from `.env` (which is git-ignored):

```env
# 1. AI & Tech Radar Telegram Bot (@Radar4All_bot)
TELEGRAM_BOT_TOKEN="8969095857:AAFK1_v2QpLFKy4yx32g6ktocd4ZQSnyszY"
TELEGRAM_CHAT_ID="6350373048"

# 2. Edu-Blog Radar Telegram Bot (@edunewsradar_bot / 학습블로그 아이템)
EDU_TELEGRAM_BOT_TOKEN="8376644109:AAFRgtiM5kJ7h4Qu5Gl2B602wYIj3GhXms4"
EDU_TELEGRAM_CHAT_ID="6350373048"

# 3. Optional Slack & Discord Webhooks
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

---

## 📋 3. Ready-to-Use Domain Presets

### Preset A: 🤖 Robotics & Physical AI
```yaml
browser:
  search_queries:
    - "https://x.com/search?q=(Robotics%20OR%20Humanoid%20OR%20PhysicalAI)%20min_faves%3A30&f=live"
    - "https://x.com/search?q=(FigureAI%20OR%20Optimus%20OR%20Unitree)%20min_faves%3A20&f=live"
topics:
  boost_keywords: ["Humanoid", "ROS2", "Actuator", "Physical AI", "Dexterity"]
```

### Preset B: 📈 Quant Finance & Trading AI
```yaml
browser:
  search_queries:
    - "https://x.com/search?q=(Quant%20OR%20AlgorithmicTrading%20OR%20FinLLM)%20min_faves%3A30&f=live"
topics:
  boost_keywords: ["Backtest", "OrderBook", "Alpha", "Pairs Trading", "HFT"]
```

### Preset C: 🇰🇷 Korean Tech & Startup Radar
```yaml
browser:
  search_queries:
    - "https://x.com/search?q=(인공지능%20OR%20생성형AI%20OR%20스타트업)%20min_faves%3A10&f=live"
topics:
  boost_keywords: ["거대언어모델", "에이전트", "LLM", "오픈소스", "파인튜닝"]
```
