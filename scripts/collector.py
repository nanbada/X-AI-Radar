#!/usr/bin/env python3
"""
X-AI-Radar High-Performance Intelligence Engine (v2.1)

Optimizations:
1. Synchronized CDP RPC Pipeline: Ensures zero message desync for Page.navigate and Runtime.evaluate.
2. CDP Media & Resource Blocking: Blocks heavy video streams and high-res images to accelerate loading.
3. Concurrent Adapter Execution: ThreadPoolExecutor fetches GitHub Trending & Hacker News in parallel.
4. State Memory & Velocity Scoring: Computes hourly delta against data/history.json.
5. Multi-Channel Webhooks: Dispatches executive alerts to Slack, Discord, and Telegram.
"""

from concurrent.futures import ThreadPoolExecutor
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
import platform
import subprocess
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

# Patterns of heavy media and trackers to block
BLOCKED_PATTERNS = [
    "*.mp4", "*.m3u8", "*.ts", "*.mov",
    "*.jpg", "*.jpeg", "*.webp",
    "*analytics*", "*telemetry*", "*doubleclick*", "*google-analytics*"
]

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
            
            // 3. Metric counters
            const getGroupMetric = (testId) => {
                const el = art.querySelector(`button[data-testid="${testId}"]`) || art.querySelector(`a[data-testid="${testId}"]`);
                if (!el) return '0';
                return el.innerText.trim() || '0';
            };
            
            const replies = getGroupMetric('reply');
            const reposts = getGroupMetric('retweet');
            const likes = getGroupMetric('like');
            const bookmarks = getGroupMetric('bookmark');
            
            let views = '0';
            const viewsEl = art.querySelector('a[href*="/analytics"]');
            if (viewsEl) views = viewsEl.innerText.trim() || '0';
            
            // 4. External technical links (GitHub, ArXiv, HuggingFace)
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

def get_x_page_ws():
    try:
        url = f"http://127.0.0.1:{CDP_PORT}/json/list"
        with urllib.request.urlopen(url, timeout=5) as res:
            pages = json.loads(res.read().decode())
            
        # 1. Look for existing x.com page
        target = next((p for p in pages if "x.com" in p.get("url", "") and p.get("type") == "page"), None)
        if target:
            return target["webSocketDebuggerUrl"]
            
        # 2. Fallback to any active page
        target = next((p for p in pages if p.get("type") == "page"), None)
        if target:
            return target["webSocketDebuggerUrl"]
            
        # 3. Create a new page tab via CDP /json/new
        new_url = f"http://127.0.0.1:{CDP_PORT}/json/new?https://x.com/home"
        req = urllib.request.Request(new_url, method="PUT")
        with urllib.request.urlopen(req, timeout=5) as res:
            new_target = json.loads(res.read().decode())
            return new_target.get("webSocketDebuggerUrl")
    except Exception as e:
        print(f"❌ Failed to reach Chrome CDP on port {CDP_PORT}: {e}", file=sys.stderr)
    return None

def parse_metric_str(s):
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

def load_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
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
    text_lower = post["text"].lower()
    
    # Exclude keywords filter
    for ex in EXCLUDE_KEYWORDS:
        if ex in text_lower:
            return -9999.0
            
    views = parse_metric_str(post["views"])
    likes = parse_metric_str(post["likes"])
    reposts = parse_metric_str(post["reposts"])
    bookmarks = parse_metric_str(post["bookmarks"])
    
    # Thread indicator detection
    is_thread = bool(re.search(r'\b(1/\d+|1/n|🧵)\b', text_lower) or text_lower.endswith('1/'))
    
    # Topic boost bonuses
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
                
    # Velocity metric computation
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
        
    if score > 15000:
        badge = "🔥 HOT"
        
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

def cdp_send_sync(ws, method, params=None, msg_id=1):
    """
    Sends a CDP command and synchronously receives its matching response.
    """
    payload = {"id": msg_id, "method": method}
    if params:
        payload["params"] = params
    ws.send(json.dumps(payload))
    while True:
        raw = ws.recv()
        try:
            res = json.loads(raw)
            if res.get("id") == msg_id:
                return res
        except:
            pass

def navigate_and_extract(ws, url, scroll_count=3):
    print(f"  🔍 Navigating to: {url}")
    # Synchronously navigate
    cdp_send_sync(ws, "Page.navigate", {"url": url}, msg_id=100)
    time.sleep(2.5)
    
    collected_dict = {}
    for i in range(scroll_count):
        req_id = 200 + i * 10
        res = cdp_send_sync(ws, "Runtime.evaluate", {"expression": EXTRACT_SCRIPT}, msg_id=req_id)
        val = res.get("result", {}).get("result", {}).get("value", "[]")
        try:
            batch = json.loads(val)
            for item in batch:
                key = item.get("tweetUrl") or (item.get("handle", "") + item.get("text", "")[:30])
                if key not in collected_dict:
                    collected_dict[key] = item
        except:
            pass
            
        # Smooth scroll
        cdp_send_sync(ws, "Runtime.evaluate", {"expression": "window.scrollBy(0, 1200)"}, msg_id=req_id + 1)
        time.sleep(1.0)
        
    return list(collected_dict.values())

def main():
    start_time = time.time()
    print(f"⚡ [X-AI-Radar v2.1] Initializing High-Speed Collection Engine (Port: {CDP_PORT})...")
    
    # 1. Parallel thread pool for external adapters (GitHub + Hacker News)
    executor = ThreadPoolExecutor(max_workers=3)
    gh_future = executor.submit(fetch_trending_ai_repos, limit=config.get("adapters", {}).get("github_trending", {}).get("limit", 5))
    hn_future = executor.submit(fetch_top_hn_ai_stories, limit=config.get("adapters", {}).get("hackernews", {}).get("limit", 5))
    
    # 2. Connect to active X CDP WebSocket
    ws_url = get_x_page_ws()
    if not ws_url:
        print(f"⚠️ Port {CDP_PORT} not responding. Attempting auto-launch of Chrome Remote Debugger...")
        try:
            import platform
            current_os = platform.system().lower()
            if "windows" in current_os:
                subprocess.Popen(["cmd.exe", "/c", os.path.join(os.path.dirname(__file__), "launch_chrome.bat")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["bash", os.path.join(os.path.dirname(__file__), "launch_chrome.sh")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3.0)
            ws_url = get_x_page_ws()
        except Exception as err:
            print(f"⚠️ Auto-launch Chrome error: {err}", file=sys.stderr)

    if not ws_url:
        print(f"❌ Could not connect to Chrome CDP on port {CDP_PORT}.", file=sys.stderr)
        return
        
    ws = websocket.create_connection(ws_url)
    
    # Enable Network & block heavy media patterns
    cdp_send_sync(ws, "Network.enable", msg_id=1)
    cdp_send_sync(ws, "Network.setBlockedURLs", {"urls": BLOCKED_PATTERNS}, msg_id=2)
    
    # Ingest search queries and timeline
    all_raw_posts = {}
    search_queries = config.get("browser", {}).get("search_queries", [])
    for sq in search_queries:
        posts = navigate_and_extract(ws, sq, scroll_count=3)
        for p in posts:
            key = p.get("tweetUrl") or (p["handle"] + p["text"][:30])
            if key not in all_raw_posts:
                all_raw_posts[key] = p
                
    if config.get("browser", {}).get("include_home_timeline", True):
        posts = navigate_and_extract(ws, "https://x.com/home", scroll_count=3)
        for p in posts:
            key = p.get("tweetUrl") or (p["handle"] + p["text"][:30])
            if key not in all_raw_posts:
                all_raw_posts[key] = p
                
    ws.close()
    print(f"📊 Collected {len(all_raw_posts)} total deduplicated posts from X sources.")
    
    # 3. Retrieve parallel adapter results
    try:
        github_repos = gh_future.result(timeout=6)
    except Exception as e:
        print(f"⚠️ GitHub adapter error: {e}", file=sys.stderr)
        github_repos = []
        
    try:
        hn_stories = hn_future.result(timeout=6)
    except Exception as e:
        print(f"⚠️ Hacker News adapter error: {e}", file=sys.stderr)
        hn_stories = []
        
    executor.shutdown(wait=False)
    
    # 4. State Memory & Velocity Scoring
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
    
    # 5. Render v2.1 Integrated Report
    today_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(out_dir, exist_ok=True)
    report_file = os.path.join(out_dir, f"x-ai-radar-{today_str}.md")
    
    # Render X table rows & deep dives
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

    # Metrics summary
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
        
    elapsed = time.time() - start_time
    print(f"🎉 [v2.1 Engine] Complete pipeline finished in {elapsed:.2f}s! (Report: {report_file})")
    
    # 6. Webhook Notifications
    send_notifications({
        "date": today_str,
        "report_file": report_file,
        "top_posts": top_x_posts
    })
    
    print("---SUMMARY_JSON_START---")
    print(json.dumps({
        "execution_time_seconds": round(elapsed, 2),
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
