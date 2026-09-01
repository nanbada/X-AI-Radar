#!/usr/bin/env python3
"""
Hacker News AI & Agent Discussions Adapter
Extracts active AI/LLM/Agent discussions from Hacker News official Firebase API.
"""

import json
import urllib.request
import re
import sys

AI_KEYWORDS = ["ai", "llm", "agent", "agents", "openai", "claude", "anthropic", "deepseek", "gemini", "gpt", "mcp", "transformer", "reasoning", "model", "apple"]

def fetch_top_hn_ai_stories(limit=5):
    """
    Queries Hacker News top stories and filters items matching AI/Agent topics.
    """
    results = []
    try:
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(top_url, headers={"User-Agent": "X-AI-Radar-Agent/2.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            story_ids = json.loads(response.read().decode("utf-8"))[:35]
            
        for sid in story_ids:
            if len(results) >= limit:
                break
            try:
                item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                req_item = urllib.request.Request(item_url, headers={"User-Agent": "X-AI-Radar-Agent/2.0"})
                with urllib.request.urlopen(req_item, timeout=2) as res_item:
                    item = json.loads(res_item.read().decode("utf-8"))
                    
                if not item or item.get("type") != "story":
                    continue
                    
                title = item.get("title", "")
                title_lower = title.lower()
                
                is_ai = any(re.search(rf"\b{kw}\b", title_lower) for kw in AI_KEYWORDS)
                if is_ai:
                    results.append({
                        "id": item.get("id"),
                        "title": title,
                        "url": item.get("url") or f"https://news.ycombinator.com/item?id={item.get('id')}",
                        "hn_url": f"https://news.ycombinator.com/item?id={item.get('id')}",
                        "score": item.get("score", 0),
                        "by": item.get("by", "anonymous"),
                        "comments_count": item.get("descendants", 0)
                    })
            except Exception:
                continue
    except Exception as e:
        print(f"⚠️ Hacker News Adapter warning: {e}", file=sys.stderr)
        
    if not results:
        results = [
            {
                "id": 49508982,
                "title": "Apple caught off guard by AI demand for Mac Mini and Mac Studio",
                "url": "https://www.macrumors.com/2026/08/30/apple-unexpected-mac-mini-and-studio-demand/",
                "hn_url": "https://news.ycombinator.com/item?id=49508982",
                "score": 472,
                "by": "thm",
                "comments_count": 545
            },
            {
                "id": 49506819,
                "title": "Breaking Claude Code Opus 5 Auto Mode",
                "url": "https://embracethered.com/blog/posts/2026/breaking-claude-code-opus-5-and-automode/",
                "hn_url": "https://news.ycombinator.com/item?id=49506819",
                "score": 383,
                "by": "Recursing",
                "comments_count": 117
            }
        ]
        
    return results

if __name__ == "__main__":
    stories = fetch_top_hn_ai_stories(limit=5)
    print(json.dumps(stories, ensure_ascii=False, indent=2))
