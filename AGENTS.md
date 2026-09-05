# 🤖 AGENTS.md - X-AI-Radar & Edu-Blog Radar Operating Manual (v2.2)

> **Repository**: [nanbada/X-AI-Radar](https://github.com/nanbada/X-AI-Radar)  
> **Workspace Path**: `/Users/nanbada/projects/X-AI-Radar`  
> **Target Engine**: Antigravity Browser Subagent (`/browser`) & Gemini 3.7 Flash  
> **Architecture**: v2.2 Dual-Engine Multi-Domain Radar (Tech + Education)

---

## 1. Unified Command Protocol (Directive-Subject-Action)

All autonomous agents modifying or executing workflows in this repository MUST follow the **DSA** framework:

| Component | Allowed Values / Pattern | Operational Meaning & Examples |
| :--- | :--- | :--- |
| `<DIRECTIVE>` | `[EXECUTE / OPTIMIZE / UPDATE_TOPIC / UPDATE_SEARCH / UPDATE_WEBHOOK / AUDIT]` | High-level goal of the agent task |
| `<SUBJECT>` | `[config.yaml / scripts/collector.py / scripts/edu_collector.py / scripts/adapters/ / reports/]` | Target configuration, script, or artifact |
| `<ACTION>` | Granular, verifiable step sequence | e.g. "Ingest Naver Edu Trends -> Curate 3 Blog Topics -> Render Markdown -> Send to Telegram" |
| `<TECHNICAL>` | Exact constraints & execution parameters | e.g. "Port: 9223, Engine: Python 3.10+, Model: Gemini 3.7 Flash, Action: Strictly Read-Only" |

---

## 2. v2.2 Dual-Engine Architecture Diagram

```mermaid
graph TD
    subgraph S1 [1. Multi-Source Ingestion]
        A1[X Precision Search Queries]
        A2[GitHub Trending AI Repositories]
        A3[Hacker News AI Discussions]
        A4[Naver Education & Parent Search Trends]
    end

    subgraph S2 [2. Analysis and Scoring Engine]
        B1[CDP Media and Resource Blocker]
        B2[State Memory History Cache]
        B3[Hourly Velocity Scoring Engine]
        B4[Edu-Blog 3-Item Planner]
    end

    subgraph S3 [3. Report and optional delivery]
        C1[Daily Markdown Reports in reports/]
        C2[Antigravity Chat Briefing]
        C3[Telegram delivery: separately approved]
        C4[Webhook delivery: separately approved]
    end

    A1 --> B1
    A2 --> B3
    A3 --> B3
    A4 --> B4
    B1 --> B2
    B2 --> B3
    B3 --> C1
    B3 -. explicit approval .-> C3
    B4 --> C1
    B4 -. explicit approval .-> C3
    B3 --> C2
    B3 -. explicit approval .-> C4
```

---

## 3. Decoupled Subagent Protocols & Roles

### A. Maker Role (Browser Subagent / Ingestion Engine)
- Attaches to Chrome CDP (Port 9223) or requests Naver search endpoints.
- Enables `Network.setBlockedURLs` (`*.mp4`, `*.m3u8`, `*.jpg`, `*.webp`, `*analytics*`).
- Reads X/browser sources and education queries without message desync
  (`cdp_send_sync`). Browser and X collection are read-only: do not use any
  engagement control or submit a form.

### B. Parallel Adapter Workers (`ThreadPoolExecutor`)
- Concurrently queries GitHub Search API, Hacker News API, and Naver Education search trends.

### C. Checker & Grader Role (Velocity & Scoring Core)
- Validates 24-hour publish timestamp constraints.
- Updates state memory (`data/history.json`) and calculates growth velocity.
- Synthesizes 3-item educational blog topic plans.
- Renders Korean-translated summaries for reports. It does not deliver them.

### D. Delivery boundary

- Telegram delivery to `@Radar4All_bot` is an external write and requires
  explicit user authorization covering the destination and content, or an
  explicitly authorized recurring delivery scope. A request to research,
  collect, rank, or render a report is not delivery authorization.
- Slack and Discord webhooks follow the same authorization rule. Reuse a
  matching approval under the global rules; ask only for uncovered scope.
- Verify the destination and final Korean text before an approved delivery;
  do not expose tokens or read `.env` values into logs or reports.

---

## 4. Zero-Trust Security Guardrails

> [!CAUTION]
> **Strict Read-Only Source Collection**:
> - Agents MUST NEVER trigger like, repost, reply, follow, bookmark, or quote actions on X.
> - During source collection, agents MUST NEVER submit forms or execute web mutations. Separately authorized delivery is governed by the delivery boundary above.

> [!IMPORTANT]
> **Secret & Cache Isolation**:
> - Ensure all local tracking data (`data/*.json`), Chrome profile directories, `.env` files (containing Telegram tokens), and temporary logs remain ignored in `.gitignore`.
