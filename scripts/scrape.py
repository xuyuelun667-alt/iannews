#!/usr/bin/env python3
"""
IanNews 抓取脚本 - RSS 源
从各大新闻网站抓取最新头条。
"""

import json
import os
import re
from datetime import datetime, timezone

import requests
from xml.etree import ElementTree

NEWS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "news.json")

SOURCES = [
    {
        "name": "Reuters",
        "rss": "https://www.reutersagency.com/feed/",
        "lang": "en",
    },
    {
        "name": "TechCrunch",
        "rss": "https://techcrunch.com/feed/",
        "lang": "en",
    },
    {
        "name": "NASA",
        "rss": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
        "lang": "en",
    },
    {
        "name": "BBC",
        "rss": "https://feeds.bbci.co.uk/news/rss.xml",
        "lang": "en",
    },
    {
        "name": "CNN",
        "rss": "https://edition.cnn.com/services/rss/",
        "lang": "en",
    },
    {
        "name": "WSJ",
        "rss": "https://feeds.a.dj.com/rss/RSSWSJD.xml",
        "lang": "en",
    },
    {
        "name": "SCMP",
        "rss": "https://www.scmp.com/rss/4/feed",
        "lang": "en",
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

MAX_ITEMS = 5


def clean_html(text):
    """Remove HTML tags from text."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_rss(source):
    """Fetch and parse an RSS feed, return article dicts."""
    name = source["name"]
    url = source["rss"]

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"  ❌  HTTP {resp.status_code}")
            return []

        root = ElementTree.fromstring(resp.content)

        # Find all <item> elements (RSS 2.0) or <entry> (Atom)
        items = root.findall(".//item") or root.findall(
            ".//{http://www.w3.org/2005/Atom}entry"
        )

        articles = []
        is_atom = len(root.findall(".//{http://www.w3.org/2005/Atom}entry")) > 0

        for item in items[:MAX_ITEMS]:
            if is_atom:
                title_el = item.find("{http://www.w3.org/2005/Atom}title")
                link_el = item.find("{http://www.w3.org/2005/Atom}link")
                desc_el = item.find("{http://www.w3.org/2005/Atom}summary")
                date_el = item.find("{http://www.w3.org/2005/Atom}updated")
                link = (
                    link_el.get("href", "")
                    if link_el is not None
                    else ""
                )
            else:
                title_el = item.find("title")
                link_el = item.find("link")
                desc_el = item.find("description")
                date_el = item.find("pubDate")
                link = link_el.text if link_el is not None and link_el.text else ""

            title = title_el.text if title_el is not None and title_el.text else ""
            desc = desc_el.text if desc_el is not None and desc_el.text else ""
            pub_date = date_el.text if date_el is not None and date_el.text else ""

            # Clean text: title + description
            text = title
            desc_clean = clean_html(desc)
            if desc_clean:
                text = f"{title} - {desc_clean}"

            articles.append({
                "id": f"rss_{name}_{len(articles)}",
                "author": name,
                "text": text[:500],
                "url": link,
                "createdAt": pub_date,
                "likes": None,
                "retweets": None,
            })

        return articles

    except Exception as e:
        print(f"  ❌  Error: {e}")
        return []


def main():
    all_articles = []
    for i, source in enumerate(SOURCES):
        print(f"🔍  [{i+1}/{len(SOURCES)}] {source['name']}...")
        articles = fetch_rss(source)
        print(f"   → {len(articles)} 条新闻")
        all_articles.extend(articles)

    # Sort by date descending (best effort)
    all_articles.sort(
        key=lambda a: a.get("createdAt", ""), reverse=True
    )

    data = {
        "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "articles": all_articles[:50],
    }

    os.makedirs(os.path.dirname(NEWS_FILE), exist_ok=True)
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成：共 {len(all_articles)} 条新闻 → {NEWS_FILE}")


if __name__ == "__main__":
    main()
