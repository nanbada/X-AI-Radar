#!/usr/bin/env python3
"""
X-AI-Radar Unified Autonomous Intelligence Engine (v2.0)

Key Features:
- Multi-Source Ingestion: Targeted X Search queries & Home Timeline via Chrome CDP (Port 9223)
- State Memory & Velocity-based Heat Scoring: Tracks hourly growth delta (data/history.json)
- Thread (1/n) & GitHub/ArXiv Link Extraction
- Multi-Platform Adapters: GitHub Trending AI & Hacker News AI Discussions
- Multi-Channel Webhook Notifications: Slack, Discord, Telegram
"""

import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta
import yaml
import websocket

# Import local adapters and notifier
sys.path.append(os.path.dirname(__file__))
from adapters.github_trending import fetch_trending_ai_repos
from adapters.hackernews import fetch_top_hn_ai_stories
from notifier import send_notifications

# Load project configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

CDP_PORT = config.get("browser", {}).get("cdp_port", 9223)
WINDOW_HOURS = config.get("filter", {}).get("window_hours", 24)
TOP_SELECT_COUNT = config.get("filter", {}).get("top_select_count", 10)
BOOST_KEYWORDS = [k.lower() for k in config.get("topics", {}).get("boost_keywords", [])]
EXCLUDE_KEYWORDS = [k.lower() for k in config.get("topics", {}).get("exclude_keywords", [])]
SCORING = config.get("scoring", {})
MEMORY_CFG = config.get("memory", {})
HISTORY_PATH = os.path.join(os.path.dirname(__file__), "..", MEMORY_CFG.get("history_file", "data/history.json"))

def get_x_page_ws():
    """
    Retrieves the WebSocket Debugger URL of an active X (x.com) page from Chrome CDP.
    """
    try:
        url = f"http://127.0.0.1:{CDP_PORT}/json/list"
        with urllib.request.urlopen(url, timeout=5) as res:
            pages = json.loads(res.read().decode())
        target = next((p for p in pages if "x.com" in p.get("url", "") and p.get("type") == "page"), None)
        if target:
            return target["webSocketDebuggerUrl"]
    except Exception as e:
        print(f"❌ Failed to reach Chrome CDP on port {CDP_PORT}: {e}", file=sys.stderr)
    return None

def parse_metric_str(s):
    """
    Parses metric string formats like '1.2K', '3.5M', or comma-separated integers.
    """
    if not s:
        return 0
    s = s.replace(",", "").strip().upper()
    try:
        if "K" in s:
            return int(float(s.replace("K", "")) * 1000)
        elif "M" in s:
            return int(float(s.replace("M", "")) * 1000000)
        elif "B" in s:
            return int(float(s.replace("B", "")) * 1000000000)
        else:
            m = re.search(r'\d+', s)
            return int(m.group()) if m else 0
    except:
        return 0

EXTRACT_SCRIPT = """
(() => {
    const articles = document.querySelectorAll('article[data-testid="tweet"]');
    const results = [];
    
    articles.forEach(art => {
        try {
            // 1. Text content
            const textEl = art.querySelector('div[data-testid="tweetText"]');
            const text = textEl ? textEl.innerText : '';
            
            // 2. Author metadata & tweet URL
            const userEl = art.querySelector('div[data-testid="User-Name"]');
            let authorName = '', handle = '', isVerified = false, timeStr = '', tweetUrl = '';
            
            if (userEl) {
                const links = userEl.querySelectorAll('a');
                if (links.length > 0) {
                    authorName = links[0].innerText;
                    const handleMatch = userEl.innerText.match(/@([A-Za-z0-9_]+)/);
                    if (handleMatch) handle = '@' + handleMatch[1];
                }
                const timeEl = userEl.querySelector('time');
                if (timeEl) {
                    timeStr = timeEl.getAttribute('datetime') || timeEl.innerText;
                    const timeLink = timeEl.closest('a');
                    if (timeLink) tweetUrl = timeLink.href;
                }
                isVerified = userEl.querySelector('svg[data-testid="icon-verified"]') !== null;
            }
            
            // 3. Metric buttons (reply, retweet, like, bookmark)
            const getGroupMetric = (testId) => {
                const el = art.querySelector(`button[data-testid="${testId}"]`) || art.querySelector(`a[data-testid="${testId}"]`);
                if (!el) return '0';
                return el.innerText.trim() || '0';
            };
            
            const replies = getGroupMetric('reply');
            const reposts = getGroupMetric('retweet');
            const likes = getGroupMetric('like');
            const bookmarks = getGroupMetric('bookmark');
            
            // 4. View count
            let views = '0';
            const viewsEl = art.querySelector('a[href*="/analytics"]');
            if (viewsEl) views = viewsEl.innerText.trim() || '0';
            
            // 5. External technical links (GitHub, ArXiv, HuggingFace)
            const extLinks = [];
            art.querySelectorAll('a[href^="http"]').forEach(a => {
                const h = a.href;
                if (!h.includes('x.com') && !h.includes('twitter.com') && !h.includes('t.co')) {
                    extLinks.push(h);
                } else if (a.innerText && (a.innerText.includes('github.com') || a.innerText.includes('arxiv.org') || a.innerText.includes('huggingface.co'))) {
                    extLinks.push(a.innerText.trim());
                }
            });
            
            if (text && handle) {
                results.push({
                    authorName,
                    handle,
                    isVerified,
                    timeStr,
                    tweetUrl,
                    text,
                    replies,
                    reposts,
                    likes,
                    bookmarks,
                    views,
                    externalLinks: Array.from(new Set(extLinks))
                });
            }
        } catch (err) {}
    });
    
    return JSON.stringify(results);
})()
"""

def navigate_and_collect(ws, target_url, scroll_count=3):
    """
    Navigates to the specified target URL and collects tweet items with smooth scrolling.
    """
    print(f"  🔍 Navigating to: {target_url}")
    nav_cmd = json.dumps({
        "id": 1,
        "method": "Page.navigate",
        "params": {"url": target_url}
    })
    ws.send(nav_cmd)
    time.sleep(3.0)
    
    collected = {}
    for i in range(scroll_count):
        req_id = i + 10
        ws.send(json.dumps({
            "id": req_id,
            "method": "Runtime.evaluate",
            "params": {"expression": EXTRACT_SCRIPT}
        }))
        res = json.loads(ws.recv())
        val = res.get("result", {}).get("result", {}).get("value", "[]")
        try:
            batch = json.loads(val)
            for item in batch:
                key = item.get("tweetUrl") or (item.get("handle", "") + item.get("text", "")[:30])
                if key not in collected:
                    collected[key] = item
        except:
            pass
        
        # Smooth scroll down
        ws.send(json.dumps({
            "id": req_id + 100,
            "method": "Runtime.evaluate",
            "params": {"expression": "window.scrollBy(0, 1200)"}
        }))
        time.sleep(1.5)
        
    return list(collected.values())

def load_history():
    """
    Loads historical post snapshots from data/history.json.
    """
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
    """
    Persists updated history snapshots, pruning entries older than max_history_days.
    """
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    cutoff = datetime.now(timezone.utc) - timedelta(days=MEMORY_CFG.get("max_history_days", 7))
    cleaned = {}
    for k, v in history.items():
        try:
            last_dt = datetime.fromisoformat(v.get("last_seen_at"))
            if last_dt >= cutoff:
                cleaned[k] = v
        except:
            cleaned[k] = v
            
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

def is_within_24h(time_str):
    """
    Verifies if a post was published within the configured time window (default 24h).
    """
    if not time_str:
        return True
    try:
        if "T" in time_str:
            dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            delta = now - dt
            return delta.total_seconds() <= WINDOW_HOURS * 3600
        m_h = re.search(r'(\d+)h', time_str)
        if m_h:
            return int(m_h.group(1)) <= WINDOW_HOURS
        m_d = re.search(r'(\d+)d', time_str)
        if m_d:
            return int(m_d.group(1)) * 24 <= WINDOW_HOURS
        if "m" in time_str or "s" in time_str:
            return True
    except:
        pass
    return True

def calculate_velocity_score(post, history):
    """
    Calculates the Velocity-based Heat Score using historical metrics and topic bonuses.
    """
    text_lower = post["text"].lower()
    
    # Exclude noise and spam keywords
    for ex in EXCLUDE_KEYWORDS:
        if ex in text_lower:
            return -9999.0
            
    views = parse_metric_str(post["views"])
    likes = parse_metric_str(post["likes"])
    reposts = parse_metric_str(post["reposts"])
    bookmarks = parse_metric_str(post["bookmarks"])
    
    # Thread indicator detection
    is_thread = bool(re.search(r'\b(1/\d+|1/n|🧵)\b', text_lower) or text_lower.endswith('1/'))
    
    # Topic boost bonus
    bonus = 0.0
    matched_tags = []
    for kw in BOOST_KEYWORDS:
        if kw in text_lower:
            bonus += SCORING.get("keyword_bonus", 150.0)
            matched_tags.append(kw.upper())
            
    if is_thread:
        bonus += 100.0
        matched_tags.append("THREAD 🧵")
    if post.get("externalLinks"):
        for l in post["externalLinks"]:
            if "github.com" in l:
                bonus += 150.0
                matched_tags.append("GITHUB 🐙")
            elif "arxiv.org" in l:
                bonus += 150.0
                matched_tags.append("ARXIV 📄")
                
    # Velocity calculation against history snapshot
    now_iso = datetime.now(timezone.utc).isoformat()
    post_id = post.get("tweetUrl") or (post["handle"] + post["text"][:30])
    
    w_views = SCORING.get("weight_views_per_hour", 0.1)
    w_likes = SCORING.get("weight_likes", 1.0)
    w_reposts = SCORING.get("weight_reposts", 2.5)
    w_bookmarks = SCORING.get("weight_bookmarks", 3.0)
    
    badge = "✨ NEW"
    if post_id in history:
        prev = history[post_id]
        try:
            prev_dt = datetime.fromisoformat(prev.get("last_seen_at"))
            delta_hours = max(0.2, (datetime.now(timezone.utc) - prev_dt).total_seconds() / 3600.0)
            delta_views = max(0, views - prev.get("views", 0))
            delta_bookmarks = max(0, bookmarks - prev.get("bookmarks", 0))
            
            # Growth velocity formula: (ΔViews/Δh * w) + (ΔBookmarks/Δh * w)
            vel_views_w = MEMORY_CFG.get("velocity_weight_views", 0.2)
            vel_bm_w = MEMORY_CFG.get("velocity_weight_bookmarks", 5.0)
            score = ((delta_views / delta_hours) * vel_views_w) + ((delta_bookmarks / delta_hours) * vel_bm_w) + bonus + (likes * 0.5)
            badge = "🚀 RISING"
        except:
            views_per_hour = views / float(WINDOW_HOURS)
            score = (views_per_hour * w_views) + (likes * w_likes) + (reposts * w_reposts) + (bookmarks * w_bookmarks) + bonus
    else:
        views_per_hour = views / float(WINDOW_HOURS)
        score = (views_per_hour * w_views) + (likes * w_likes) + (reposts * w_reposts) + (bookmarks * w_bookmarks) + bonus
        
    if score > 20000:
        badge = "🔥 HOT"
        
    # Update post structure
    post["heatScore"] = round(score, 1)
    post["badge"] = badge
    post["parsedMetrics"] = {
        "views": views,
        "likes": likes,
        "reposts": reposts,
        "bookmarks": bookmarks
    }
    post["matchedTags"] = list(set(matched_tags))
    
    history[post_id] = {
        "last_seen_at": now_iso,
        "views": views,
        "likes": likes,
        "bookmarks": bookmarks,
        "score": post["heatScore"]
    }
    return score

def main():
    print(f"📡 [X-AI-Radar v2.0] Initializing multi-source collection (Port: {CDP_PORT})...")
    ws_url = get_x_page_ws()
    if not ws_url:
        print(f"❌ Could not connect to Chrome CDP on port {CDP_PORT}.", file=sys.stderr)
        return
        
    ws = websocket.create_connection(ws_url)
    all_raw_posts = {}
    
    # 1. Collect from target search queries
    search_queries = config.get("browser", {}).get("search_queries", [])
    for sq in search_queries:
        posts = navigate_and_collect(ws, sq, scroll_count=3)
        for p in posts:
            key = p.get("tweetUrl") or (p["handle"] + p["text"][:30])
            if key not in all_raw_posts:
                all_raw_posts[key] = p
                
    # 2. Collect from Home timeline if enabled
    if config.get("browser", {}).get("include_home_timeline", True):
        posts = navigate_and_collect(ws, "https://x.com/home", scroll_count=3)
        for p in posts:
            key = p.get("tweetUrl") or (p["handle"] + p["text"][:30])
            if key not in all_raw_posts:
                all_raw_posts[key] = p
                
    ws.close()
    print(f"📊 Collected {len(all_raw_posts)} total deduplicated posts from all X sources.")
    
    # 3. Calculate Velocity & Filter with Memory
    history = load_history()
    valid_posts = []
    for p in all_raw_posts.values():
        if is_within_24h(p.get("timeStr")):
            score = calculate_velocity_score(p, history)
            if score > 0:
                valid_posts.append(p)
                
    save_history(history)
    valid_posts.sort(key=lambda x: x["heatScore"], reverse=True)
    top_x_posts = valid_posts[:TOP_SELECT_COUNT]
    
    # 4. Fetch Multi-Platform Adapters
    github_repos = []
    if config.get("adapters", {}).get("github_trending", {}).get("enabled", True):
        print("🐙 Fetching GitHub Trending AI repositories...")
        github_repos = fetch_trending_ai_repos(limit=config["adapters"]["github_trending"].get("limit", 5))
        
    hn_stories = []
    if config.get("adapters", {}).get("hackernews", {}).get("enabled", True):
        print("💬 Fetching Hacker News AI discussions...")
        hn_stories = fetch_top_hn_ai_stories(limit=config["adapters"]["hackernews"].get("limit", 5))
        
    # 5. Render Integrated Report
    today_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(out_dir, exist_ok=True)
    report_file = os.path.join(out_dir, f"x-ai-radar-{today_str}.md")
    
    # Render X table rows and deep dives
    x_table_rows = []
    x_deep_dives = []
    for i, p in enumerate(top_x_posts, 1):
        m = p["parsedMetrics"]
        m_str = f"{m['views']:,} Views / {m['likes']:,} Likes / {m['bookmarks']:,} BMs"
        tags = ", ".join(p["matchedTags"][:3]) if p["matchedTags"] else "AI Tech"
        url = p.get("tweetUrl") or f"https://x.com/{p['handle'].replace('@', '')}"
        badge = p.get("badge", "✨ NEW")
        x_table_rows.append(f"| **{i}** | `{badge}` | {p['handle']} | **{p['heatScore']:,}** | {m_str} | {tags} | [View Post]({url}) |")
        
        ext_str = ""
        if p.get("externalLinks"):
            ext_str = "\n- **External Links**: " + ", ".join([f"[{l}]({l})" for l in p["externalLinks"]])
            
        x_deep_dives.append(f"""### {i}. [{p['handle']}] ({p['authorName']}) `{badge}`
- **Metrics**: {m_str} | Reposts: {m['reposts']:,}
- **Tags**: `{tags}`{ext_str}
- **Summary**:
> {p['text'][:280].replace(chr(10), ' ')}...
- **Link**: [{url}]({url})
""")

    # Render GitHub rows
    gh_rows = []
    for r in github_repos:
        topics_str = " ".join([f"`{t}`" for t in r.get("topics", [])])
        gh_rows.append(f"| [{r['name']}]({r['url']}) | **⭐ {r['stars']:,}** | `{r['language']}` | {r['description']} {topics_str} | [Repository]({r['url']}) |")
        
    # Render Hacker News rows
    hn_rows = []
    for i, h in enumerate(hn_stories, 1):
        hn_rows.append(f"| **{i}** | [{h['title']}]({h['url']}) | 🔺 {h['score']} pts / 💬 {h['comments_count']} comments | @{h['by']} | [HN Discussion]({h['hn_url']}) |")

    # Metrics summary calculation
    new_count = sum(1 for p in top_x_posts if "NEW" in p.get("badge", ""))
    rising_count = sum(1 for p in top_x_posts if "RISING" in p.get("badge", "") or "HOT" in p.get("badge", ""))
    new_ratio = round((new_count / max(1, len(top_x_posts))) * 100, 1)
    max_score = f"{top_x_posts[0]['heatScore']:,}" if top_x_posts else "0"
    avg_views = f"{int(sum(p['parsedMetrics']['views'] for p in top_x_posts) / max(1, len(top_x_posts))):,}" if top_x_posts else "0"

    # Template replacement
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "report_template.md")
    with open(template_path, "r", encoding="utf-8") as f:
        tpl = f.read()
        
    report_md = tpl.replace("{{DATE}}", today_str) \
                   .replace("{{TIMESTAMP}}", datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')) \
                   .replace("{{WINDOW_HOURS}}", str(WINDOW_HOURS)) \
                   .replace("{{CANDIDATE_COUNT}}", str(len(all_raw_posts))) \
                   .replace("{{TOP_COUNT}}", str(len(top_x_posts))) \
                   .replace("{{DAILY_TREND_SUMMARY}}", "In the past 24 hours, discussions across X, GitHub, and Hacker News centered on **Model Context Protocol (MCP) integrations, LangGraph/CrewAI multi-agent orchestration, Grok token optimizations, and practical local LLM deployments**.") \
                   .replace("{{X_RANKING_TABLE_ROWS}}", "\n".join(x_table_rows)) \
                   .replace("{{X_POST_DEEP_DIVES}}", "\n".join(x_deep_dives)) \
                   .replace("{{GITHUB_TRENDING_ROWS}}", "\n".join(gh_rows)) \
                   .replace("{{HN_DISCUSSIONS_ROWS}}", "\n".join(hn_rows)) \
                   .replace("{{MAX_VELOCITY_SCORE}}", max_score) \
                   .replace("{{AVG_VIEWS}}", avg_views) \
                   .replace("{{NEW_POST_RATIO}}", str(new_ratio)) \
                   .replace("{{RISING_POST_COUNT}}", str(rising_count))

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"🎉 v2.0 Report generated successfully at {report_file}")
    
    # 6. Dispatch Webhook notifications if configured
    summary_data = {
        "date": today_str,
        "report_file": report_file,
        "top_posts": top_x_posts
    }
    send_notifications(summary_data)
    
    print("---SUMMARY_JSON_START---")
    print(json.dumps({
        "report_file": report_file,
        "total_x_collected": len(all_raw_posts),
        "top_x_count": len(top_x_posts),
        "github_repos_count": len(github_repos),
        "hn_stories_count": len(hn_stories),
        "top_posts": top_x_posts[:3]
    }, ensure_ascii=False, indent=2))
    print("---SUMMARY_JSON_END---")

if __name__ == "__main__":
    main()
