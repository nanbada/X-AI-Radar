#!/usr/bin/env python3
"""
Hacker News AI & Agent Discussions Adapter
Extracts active AI/LLM/Agent discussions from Hacker News official Firebase API.
"""

import json
import urllib.request
import re
import sys

AI_KEYWORDS = ["ai", "llm", "agent", "agents", "openai", "claude", "anthropic", "deepseek", "gemini", "gpt", "mcp", "transformer", "reasoning"]

def fetch_top_hn_ai_stories(limit=5):
    """
    Queries Hacker News top stories and filters items matching AI/Agent topics.
    """
    results = []
    try:
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(top_url, headers={"User-Agent": "X-AI-Radar-Agent/2.0"})
        with urllib.request.urlopen(req, timeout=6) as response:
            story_ids = json.loads(response.read().decode("utf-8"))[:60]
            
        for sid in story_ids:
            if len(results) >= limit:
                break
            try:
                item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                req_item = urllib.request.Request(item_url, headers={"User-Agent": "X-AI-Radar-Agent/2.0"})
                with urllib.request.urlopen(req_item, timeout=3) as res_item:
                    item = json.loads(res_item.read().decode("utf-8"))
                    
                if not item or item.get("type") != "story":
                    continue
                    
                title = item.get("title", "")
                title_lower = title.lower()
                
                # Check keyword match
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
        
    return results

if __name__ == "__main__":
    stories = fetch_top_hn_ai_stories(limit=5)
    print(json.dumps(stories, ensure_ascii=False, indent=2))
