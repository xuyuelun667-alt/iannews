#!/usr/bin/env python3
"""
IanNews 抓取脚本
使用 X API v2 (search/recent) 抓取指定新闻账号的最新推文。
"""

import json
import os
import time
from datetime import datetime, timezone, timedelta

import requests

# ── 配置 ────────────────────────────────────────────────
NEWS_ACCOUNTS = [
    "Reuters",
    "TechCrunch",
    "NASA",
    "BBCWorld",
    "CNN",
    "WSJ",
    "nytimes",
    "SCMPNews",
]

# 每个账号抓取的最新推文数
TWEETS_PER_ACCOUNT = 3

# 排除转推、回复
QUERY_TEMPLATE = "from:{user} -is:retweet -is:reply lang:en"

# 输出文件
NEWS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "news.json")

# ── X API ───────────────────────────────────────────────
BEARER_TOKEN = os.environ.get("X_API_BEARER", "")
SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"


def api_headers():
    return {"Authorization": f"Bearer {BEARER_TOKEN}"}


def fetch_tweets(username, max_results=TWEETS_PER_ACCOUNT):
    """Search recent tweets from a given account."""
    query = QUERY_TEMPLATE.format(user=username)
    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "public_metrics,created_at,author_id",
        "expansions": "author_id",
        "user.fields": "username",
    }

    resp = requests.get(SEARCH_URL, headers=api_headers(), params=params, timeout=15)

    if resp.status_code == 429:
        print(f"⚠️  Rate limited on {username}, pausing 60s...")
        time.sleep(60)
        return fetch_tweets(username, max_results)

    if resp.status_code != 200:
        print(f"❌  {username}: HTTP {resp.status_code} - {resp.text[:200]}")
        return []

    data = resp.json()
    tweets = data.get("data", [])
    users_map = {}
    for user in data.get("includes", {}).get("users", []):
        users_map[user["id"]] = user["username"]

    articles = []
    for tw in tweets:
        author_id = tw.get("author_id", "")
        metrics = tw.get("public_metrics", {})
        articles.append({
            "id": tw["id"],
            "author": users_map.get(author_id, username),
            "text": tw.get("text", ""),
            "url": f"https://x.com/{users_map.get(author_id, username)}/status/{tw['id']}",
            "createdAt": tw.get("created_at", ""),
            "likes": metrics.get("like_count", 0),
            "retweets": metrics.get("retweet_count", 0),
        })

    return articles


def main():
    if not BEARER_TOKEN:
        print("❌  X_API_BEARER 未设置")
        exit(1)

    if not NEWS_ACCOUNTS:
        print("❌  没有配置新闻账号")
        exit(1)

    all_articles = []
    for i, account in enumerate(NEWS_ACCOUNTS):
        print(f"🔍  [{i+1}/{len(NEWS_ACCOUNTS)}] {account}...")
        articles = fetch_tweets(account)
        print(f"   → {len(articles)} 条推文")
        all_articles.extend(articles)
        # 每个账号之间稍作间隔，避免速率限制
        if i < len(NEWS_ACCOUNTS) - 1:
            time.sleep(2)

    # 按时间倒序排列
    all_articles.sort(key=lambda a: a.get("createdAt", ""), reverse=True)

    data = {
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "articles": all_articles[:50],  # 最多保留 50 条
    }

    os.makedirs(os.path.dirname(NEWS_FILE), exist_ok=True)
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成：共 {len(all_articles)} 条推文 → {NEWS_FILE}")


if __name__ == "__main__":
    main()
