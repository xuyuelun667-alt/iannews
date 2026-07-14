#!/usr/bin/env python3
"""
IanNews 抓取脚本 - X API v2
"""

import json
import os
import time
from datetime import datetime, timezone

import requests

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

TWEETS_PER_ACCOUNT = 3
QUERY_TPL = "from:{user} -is:retweet -is:reply lang:en"
NEWS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "news.json")
SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"


def fetch_tweets(username, bearer, max_results=TWEETS_PER_ACCOUNT):
    headers = {"Authorization": f"Bearer {bearer}"}
    params = {
        "query": QUERY_TPL.format(user=username),
        "max_results": max_results,
        "tweet.fields": "public_metrics,created_at,author_id",
        "expansions": "author_id",
        "user.fields": "username",
    }
    resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=15)

    if resp.status_code == 429:
        print("  ⚠️  Rate limited, pausing 60s...")
        time.sleep(60)
        return fetch_tweets(username, bearer, max_results)

    if resp.status_code != 200:
        print(f"  ❌  HTTP {resp.status_code} - {resp.text[:120]}")
        return []

    data = resp.json()
    tweets = data.get("data", [])
    users = {u["id"]: u["username"] for u in data.get("includes", {}).get("users", [])}

    articles = []
    for tw in tweets:
        aid = tw.get("author_id", "")
        uname = users.get(aid, username)
        metrics = tw.get("public_metrics", {})
        articles.append({
            "id": tw["id"],
            "author": uname,
            "text": tw.get("text", ""),
            "url": f"https://x.com/{uname}/status/{tw['id']}",
            "createdAt": tw.get("created_at", ""),
            "likes": metrics.get("like_count", 0),
            "retweets": metrics.get("retweet_count", 0),
        })
    return articles


def main():
    bearer = os.environ.get("X_API_BEARER", "")
    if not bearer:
        print("❌  X_API_BEARER 未设置")
        exit(1)

    all_articles = []
    for i, account in enumerate(NEWS_ACCOUNTS):
        print(f"🔍  [{i+1}/{len(NEWS_ACCOUNTS)}] {account}...")
        articles = fetch_tweets(account, bearer)
        print(f"   → {len(articles)} 条推文")
        all_articles.extend(articles)
        if i < len(NEWS_ACCOUNTS) - 1:
            time.sleep(2)

    all_articles.sort(key=lambda a: a.get("createdAt", ""), reverse=True)

    data = {
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "articles": all_articles[:50],
    }

    os.makedirs(os.path.dirname(NEWS_FILE), exist_ok=True)
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成：共 {len(all_articles)} 条推文 → {NEWS_FILE}")


if __name__ == "__main__":
    main()
