# 📡 X-AI-Radar (v2.0)

<p align="center">
  <b>Multi-Source Autonomous AI & Agents Intelligence Radar</b><br>
  Powered by <b>Antigravity Browser Subagent (<code>/browser</code>)</b> and <b>Gemini 3.7 Flash</b>.
</p>

<p align="center">
  <a href="#-key-features">Key Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-security--safety">Security</a> •
  <a href="./README_KO.md">한국어 문서 (Korean)</a>
</p>

---

## 🌟 Key Features

- **Zero-Cost & Ban-Free Ingestion**: Operates seamlessly over Chrome DevTools Protocol (CDP, Port 9223) using your legitimate browser session. No expensive API tiers ($100–$5,000/mo) or fragile unofficial scrapers.
- **Precision Target Search**: Ingests high-signal AI posts via search operators (`min_faves:50`, `lang:en`) to completely filter out general algorithmic timeline noise.
- **State Memory & Velocity-based Heat Scoring**: Tracks hourly growth delta ($\Delta\text{Views}/\Delta\text{h}$, $\Delta\text{Bookmarks}/\Delta\text{h}$) via `data/history.json` to prioritize breakout (`[RISING]`) topics over stale multi-day trends.
- **Thread & External Link Inspection**: Automatically identifies `1/n` technical threads and extracts embedded GitHub repositories and ArXiv research papers.
- **Multi-Platform Intelligence Adapters**: Aggregates **GitHub Trending AI Repositories** and **Hacker News AI Discussions** into a unified 3-part daily executive brief.
- **Multi-Channel Webhook Alerts**: Automatically pushes Top 3 daily highlights to Slack, Discord, and Telegram.
- **Strictly Read-Only (100% Safe)**: Enforces zero-mutation policy (no likes, retweets, replies, or follows).

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph DataSources ["1. Multi-Source Ingestion"]
        A1["X Precision Search: (AI OR Agents OR LLM OR MCP) min_faves:50"]
        A2["X Framework Search: (LangGraph OR CrewAI OR AutoGen) min_faves:30"]
        A3["GitHub Trending AI Repositories (Daily Top)"]
        A4["Hacker News AI Discussions (Official Firebase API)"]
    end

    subgraph CoreEngine ["2. v2.0 Analysis & Scoring Core"]
        B1["State Memory (data/history.json): 7-Day Metric Delta Tracker"]
        B2["Velocity Engine: Hourly Rate of Views & Bookmarks (Δ/Δh)"]
        B3["Thread (1/n) & GitHub/ArXiv Link Parser"]
        B4["Gemini 3.7 Flash Semantic Grader"]
    end

    subgraph OutputHub ["3. Intelligence Distribution"]
        C1["Daily Markdown Artifact (reports/x-ai-radar-YYYY-MM-DD.md)"]
        C2["Antigravity Interactive Chat Briefing"]
        C3["Webhook Push: Slack / Discord / Telegram"]
    end

    DataSources --> CoreEngine
    CoreEngine --> OutputHub
```

---

## 📂 Project Structure

```text
X-AI-Radar/
├── AGENTS.md                  # Autonomous agent operating protocol (DSA standard)
├── SKILL.md                   # Antigravity custom skill specification (/x-ai-radar)
├── config.yaml                # Unified configuration (Search queries, scoring, webhooks)
├── README.md                  # English documentation
├── README_KO.md               # Korean documentation (한국어 가이드)
├── .gitignore                 # Security & secret isolation rules
├── data/
│   ├── .gitkeep
│   └── history.json           # Local cache for state memory & velocity tracking (ignored)
├── scripts/
│   ├── collector.py           # Core v2.0 multi-source collection & ranking engine
│   ├── notifier.py            # Slack / Discord / Telegram webhook dispatcher
│   ├── launch_chrome.sh       # Chrome Remote Debugging (Port 9223) launcher
│   ├── run_radar.sh           # Environment health checker & manual CLI runner
│   └── adapters/
│       ├── github_trending.py # GitHub Trending AI adapter
│       └── hackernews.py      # Hacker News AI discussions adapter
├── templates/
│   └── report_template.md     # 3-part comprehensive markdown report template
└── reports/                   # Daily generated reports (x-ai-radar-YYYY-MM-DD.md)
```

---

## 🚀 Quick Start

### 1. Launch Chrome in Remote Debugging Mode
Launch an isolated Chrome profile on port 9223. Perform a **one-time manual login to X (Twitter)** in the opened browser window:

```bash
./scripts/launch_chrome.sh
```

### 2. Run X-AI-Radar Manually
In your Antigravity chat, type:
```text
/x-ai-radar
```
Or execute directly from your terminal:
```bash
python3 scripts/collector.py
```

### 3. Schedule Daily Autonomous Execution (08:15 KST)
Register the recurring task with Antigravity:
```text
/schedule
CronExpression: "15 8 * * *"
Prompt: "/x-ai-radar"
IsDaemon: true
```

---

## ⚙️ Configuration (`config.yaml`)

```yaml
# Target Search Queries
browser:
  cdp_port: 9223
  search_queries:
    - "https://x.com/search?q=(AI%20OR%20Agents%20OR%20LLM%20OR%20MCP)%20min_faves%3A50&f=live"
    - "https://x.com/search?q=(LangGraph%20OR%20CrewAI%20OR%20AutoGen)%20min_faves%3A30&f=live"

# State Memory & Velocity Weights
memory:
  enabled: true
  history_file: "data/history.json"
  velocity_weight_views: 0.2
  velocity_weight_bookmarks: 5.0

# Multi-Channel Webhook Notifications
notifications:
  enabled: true
  webhooks:
    slack: "https://hooks.slack.com/services/..."
    discord: "https://discord.com/api/webhooks/..."
    telegram_bot_token: "YOUR_BOT_TOKEN"
    telegram_chat_id: "YOUR_CHAT_ID"
```

---

## 🛡️ Security & Safety

1. **Zero-Mutation Guardrail**: The engine strictly executes DOM reads and navigation. All write operations (like, retweet, reply, bookmark, follow) are hard-disabled.
2. **Profile Isolation**: Uses a dedicated `--user-data-dir` (`$HOME/chrome_agent_profile`), keeping your personal browsing cookies completely untouched.
3. **Secret Protection**: `.gitignore` prevents publishing session data (`data/*.json`), environment files (`.env`), or local logs to git.

---

## 📄 License & Attribution

Distributed under the MIT License. Developed for the Google Antigravity & AI Agent ecosystem.  
Repository: [nanbada/X-AI-Radar](https://github.com/nanbada/X-AI-Radar)
