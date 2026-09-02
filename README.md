# 📡 X-AI-Radar & Edu-Blog Radar (v2.2)

<p align="center">
  <b>Multi-Domain Autonomous Intelligence & Blog Ideation Radar</b><br>
  Powered by <b>Antigravity Browser Subagent (<code>/browser</code>)</b> and <b>Gemini 3.7 Flash</b>.<br>
  <i>⚡ Dual Engine: AI & Tech Radar (~17s) + Elementary & Middle School Edu-Blog Radar (3 Daily Items)</i><br>
  <i>💻 100% Cross-Platform: Unified CLI for macOS, Windows (Batch / PowerShell), and Linux.</i>
</p>

<p align="center">
  <a href="#-dual-intelligence-engines">Dual Engines</a> •
  <a href="#-key-features">Key Features</a> •
  <a href="#-project-structure">Project Structure</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-customizing-topics">Customizing Topics</a> •
  <a href="./README_KO.md">한국어 설명서 (Korean)</a>
</p>

---

## 🚀 Dual Intelligence Engines

X-AI-Radar features two specialized, turnkey intelligence engines that deliver automated briefings to your **Telegram (`@Radar4All_bot` & `@edunewsradar_bot`)**, Slack, Discord, and Markdown reports:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. 🤖 X-AI-Radar (Tech Engine)                                              │
│    • Target: Global AI, Autonomous Agents, LLM, MCP, and GitHub Trending    │
│    • Latency: ~17 seconds via Chrome CDP Media Resource Blocker             │
│    • Command: python radar.py --ai                                          │
│    • Telegram: @Radar4All_bot                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. 🎓 Edu-Blog Radar (Education & Parent Blog Engine)                       │
│    • Target: Elementary/Middle School Fun Study Tips, Seasonal Study Items  │
│    • Output: Top 3 Actionable Blog Topic Outlines & SEO Hashtags            │
│    • Command: python radar.py --edu                                         │
│    • Telegram: @edunewsradar_bot (학습블로그 아이템)                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Features

- **⚡ Blazing Fast Ingestion**: Uses Chrome DevTools Protocol (CDP) with media resource blocking (`*.mp4`, `*.jpg`, trackers) and parallel adapter thread pools to deliver full reports in under 18 seconds.
- **💻 Unified CLI (`radar.py`)**: Single command execution across macOS, Windows, and Linux (`python radar.py --all`, `--ai`, `--edu`, or `--browser`).
- **🎯 3-Item Edu-Blog Generator**: Analyzes parent and student concerns from Naver and Google search to produce ready-to-publish blog drafts (Hook titles, 3-step outlines, and SEO hashtags).
- **📱 Dual Telegram Bot Routing**: Automatically dispatches Tech summaries to `@Radar4All_bot` (Korean translated) and Educational blog ideas to `@edunewsradar_bot`.
- **Zero-Cost & Ban-Free**: Reuses your local Chrome session (Port 9223). Zero expensive API tiers or fragile scraping tokens.
- **State Memory & Velocity Scoring**: Tracks hourly growth delta (Views/h, Bookmarks/h) via `data/history.json` to prioritize breakout (`[RISING]`) topics.
- **🛡️ Strictly Read-Only (100% Safe)**: Enforces zero-mutation policy (no likes, retweets, replies, or follows).

---

## 📂 Optimized Project Structure

```text
X-AI-Radar/
├── radar.py                   # 🌟 Unified Root CLI Orchestrator (--all, --ai, --edu, --browser)
├── run.bat                    # 🚀 Windows One-Click Root Launcher (Double Click)
├── run.sh                     # 🚀 macOS/Linux Root Runner
├── requirements.txt           # Python project dependencies (pyyaml, websocket-client)
├── .env.example               # Secret credentials template
├── .env                       # Local private Telegram & Webhook secrets (Git Ignored)
├── config.yaml                # Unified search queries, scoring, and schedule configuration
├── AGENTS.md                  # Autonomous agent operating manual (DSA standard)
├── SKILL.md                   # Antigravity custom skill specification (/x-ai-radar, /edu-blog-radar)
├── README.md                  # Global English documentation
├── README_KO.md               # Korean user manual (한국어 가이드)
├── data/
│   ├── .gitkeep
│   └── history.json           # State memory & velocity tracking cache (Git Ignored)
├── scripts/
│   ├── collector.py           # Core v2.1 high-speed AI & tech intelligence engine (~17s)
│   ├── edu_collector.py       # Edu-Blog Radar: Elementary & Middle school 3-item planner
│   ├── notifier.py            # Multi-channel webhook & Telegram Korean translator
│   ├── setup_telegram.py      # Interactive Telegram bot link helper
│   ├── launch_chrome.bat      # Windows Chrome CDP launcher
│   ├── launch_chrome.ps1      # Windows PowerShell Chrome CDP launcher
│   ├── launch_chrome.sh       # macOS/Linux Chrome CDP launcher
│   └── adapters/
│       ├── github_trending.py # GitHub Trending AI adapter
│       ├── hackernews.py      # Hacker News AI discussions adapter
│       └── naver_edu.py       # Naver education search & trends adapter
├── templates/
│   ├── report_template.md     # 3-part AI tech intelligence report template
│   └── edu_report_template.md # 3-item educational blog ideation template
└── reports/                   # Daily generated reports (*.md)
```

---

## 🚀 Quick Start (Unified CLI)

### 1. Launch Chrome in Remote Debugging Mode (Port 9223)

* **macOS / Linux / Windows (Unified)**:
  ```bash
  python radar.py --browser
  ```
  *(Or double click `scripts/launch_chrome.bat` on Windows)*

> [!NOTE]
> In the opened Chrome window, perform a **one-time login to X.com**. The session is saved in an isolated directory (`chrome_agent_profile`) and will be reused automatically.

### 2. Run the Intelligence Radars

* **Run Both Radars (Default)**:
  ```bash
  python radar.py --all
  ```
* **Run AI Tech Radar Only**:
  ```bash
  python radar.py --ai
  ```
* **Run Educational Blog Radar Only**:
  ```bash
  python radar.py --edu
  ```
* **Windows One-Click**: Double-click `run.bat`

### 3. Schedule Daily Autonomous Execution (08:15 KST)
Register the recurring task with Antigravity:
```text
/schedule
CronExpression: "15 8 * * *"
Prompt: "/x-ai-radar"
IsDaemon: true
```

---

## 🎯 Customizing Topics & Search Queries

You can easily adapt X-AI-Radar to track any domain (Robotics, Web3, Healthcare AI, Specific LLMs, etc.) by modifying `config.yaml`:

```yaml
browser:
  search_queries:
    # Example A: AI Agents & Reasoning Models
    - "https://x.com/search?q=(AI%20OR%20Agents%20OR%20Reasoning%20OR%20MCP)%20min_faves%3A50&f=live"
    
    # Example B: Robotics & Physical AI
    - "https://x.com/search?q=(Robotics%20OR%20Humanoid%20OR%20PhysicalAI)%20min_faves%3A30&f=live"
```

---

## 🛡️ Security & Safety

1. **Zero-Mutation Guardrail**: The engine strictly executes DOM reads and navigation. All write operations (like, retweet, reply, bookmark, follow) are hard-disabled.
2. **Profile Isolation**: Uses a dedicated `--user-data-dir` (`chrome_agent_profile`), keeping your personal browsing cookies completely untouched.
3. **Secret Protection**: `.gitignore` prevents publishing session data (`data/*.json`), environment files (`.env`), or local logs to git.

---

## 📄 License & Attribution

Distributed under the MIT License. Developed for the Google Antigravity & AI Agent ecosystem.  
Repository: [nanbada/X-AI-Radar](https://github.com/nanbada/X-AI-Radar)
