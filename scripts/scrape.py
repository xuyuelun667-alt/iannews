#!/usr/bin/env python3
"""
IanNews 抓取脚本 - RSS 源 + 自动翻译
英文内容自动翻译为中文，中文内容保持原文。
"""

import json
import os
import re
import time
from datetime import datetime, timezone

import requests
from xml.etree import ElementTree

try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False

NEWS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "news.json")

SOURCES = [
    # ── 英文 ──
    {
        "name": "TechCrunch",
        "rss": "https://techcrunch.com/feed/",
    },
    {
        "name": "NASA",
        "rss": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    },
    {
        "name": "BBC",
        "rss": "https://feeds.bbci.co.uk/news/rss.xml",
    },
    {
        "name": "WSJ",
        "rss": "https://feeds.a.dj.com/rss/RSSWSJD.xml",
    },
    {
        "name": "SCMP",
        "rss": "https://www.scmp.com/rss/4/feed",
    },
    # ── 中文 ──
    {
        "name": "BBC中文",
        "rss": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
    },
    {
        "name": "华尔街日报中文",
        "rss": "https://cn.wsj.com/rss/",
    },
    {
        "name": "环球网",
        "rss": "https://www.huanqiu.com/rss/globalnews.xml",
    },
    {
        "name": "澎湃新闻",
        "rss": "https://www.thepaper.cn/rss/news.xml",
    },
    {
        "name": "36氪",
        "rss": "https://36kr.com/feed",
    },
    {
        "name": "爱范儿",
        "rss": "https://www.ifanr.com/feed",
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

MAX_ITEMS = 5

# 中文字符范围
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def is_chinese(text):
    """判断文本是否主要是中文。"""
    if not text:
        return False
    # 用作者名或内容判断
    matches = CJK_RE.findall(text[:50])
    return len(matches) >= 3


def clean_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def translate_text(text, max_len=2000):
    """调用 Google 免费翻译，英文 → 中文。"""
    if not text or not HAS_TRANSLATOR:
        return ""

    text = text[:max_len]
    try:
        result = GoogleTranslator(source="en", target="zh-CN").translate(text)
        return result or ""
    except Exception as e:
        print(f"  ⚠️  翻译失败: {e}")
        return ""


def fetch_rss(source):
    name = source["name"]
    url = source["rss"]

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"  ❌  HTTP {resp.status_code}")
            return []

        root = ElementTree.fromstring(resp.content)

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
                link = link_el.get("href", "") if link_el is not None else ""
            else:
                title_el = item.find("title")
                link_el = item.find("link")
                desc_el = item.find("description")
                date_el = item.find("pubDate")
                link = link_el.text if link_el is not None and link_el.text else ""

            title = title_el.text if title_el is not None and title_el.text else ""
            desc = desc_el.text if desc_el is not None and desc_el.text else ""
            pub_date = date_el.text if date_el is not None and date_el.text else ""

            desc_clean = clean_html(desc)
            text = title
            if desc_clean:
                text = f"{title} - {desc_clean}"

            translated = ""
            if not is_chinese(text):
                print(f"  🌐  翻译中...")
                translated = translate_text(text)
                time.sleep(0.5)  # 避免触发限流

            articles.append({
                "id": f"rss_{name}_{len(articles)}",
                "author": name,
                "text": text[:500],
                "translated": translated[:500],
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
    if not HAS_TRANSLATOR:
        print("⚠️  deep-translator 未安装，将跳过翻译")

    all_articles = []
    for i, source in enumerate(SOURCES):
        print(f"🔍  [{i+1}/{len(SOURCES)}] {source['name']}...")
        articles = fetch_rss(source)
        print(f"   → {len(articles)} 条新闻")
        all_articles.extend(articles)

    all_articles.sort(key=lambda a: a.get("createdAt", ""), reverse=True)

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
