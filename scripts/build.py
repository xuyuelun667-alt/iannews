#!/usr/bin/env python3
"""
读取 data/news.json，生成 SEO 优化的 index.html。
新闻内容直接写入 HTML，爬虫 / AI 无需执行 JS 即可看到完整内容。
"""

import json
import os
import re
from datetime import datetime, timezone
from html import escape

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
NEWS_FILE = os.path.join(PROJECT_ROOT, "data", "news.json")
INDEX_FILE = os.path.join(PROJECT_ROOT, "index.html")
SITE_URL = "https://iannews.cc"
SITE_NAME = "IanNews"
SITE_DESC = "降低获取全球信息的门槛。精选可信来源，减少信息噪音，让您更高效地了解世界。"
SITE_DESC_SHORT = "全球新闻聚合 — 精选可信来源，减少信息噪音"


def generate_json_ld(articles, fetched_at):
    """生成结构化数据 JSON-LD"""

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lastmod = fetched_at or now_iso

    # 1. Organization
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{SITE_URL}/#organization",
        "name": SITE_NAME,
        "url": SITE_URL,
        "description": SITE_DESC,
        "logo": f"{SITE_URL}/favicon.svg",
        "foundingDate": "2026",
        "nonprofitStatus": "Nonprofit",
    }

    # 2. WebSite
    website = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "url": SITE_URL,
        "name": SITE_NAME,
        "description": SITE_DESC,
        "publisher": {"@id": f"{SITE_URL}/#organization"},
        "inLanguage": "zh-CN",
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{SITE_URL}/?q={{search_term_string}}"
            },
            "query-input": "required name=search_term_string"
        },
    }

    # 3. CollectionPage (the main listing page)
    collection = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": f"{SITE_URL}/#webpage",
        "url": f"{SITE_URL}/",
        "name": f"{SITE_NAME} — {SITE_DESC_SHORT}",
        "description": SITE_DESC,
        "about": SITE_DESC,
        "isPartOf": {"@id": f"{SITE_URL}/#website"},
        "mainEntity": {
            "@type": "ItemList",
            "itemListElement": [],
        },
        "dateModified": lastmod,
        "datePublished": "2026-07-14",
    }

    item_list = collection["mainEntity"]["itemListElement"]
    for i, a in enumerate(articles[:50]):
        headline = a.get("text", "")[:200]
        author = a.get("author", "")
        url = a.get("url", "")
        ts = a.get("createdAt", "")
        translated = a.get("translated", "")

        news_article = {
            "@type": "NewsArticle",
            "position": i + 1,
            "headline": headline,
            "url": url,
            "author": {"@type": "Organization", "name": author},
            "publisher": {"@type": "Organization", "name": author},
            "inLanguage": "en" if not re.search(r"[\u4e00-\u9fff]", headline) else "zh-CN",
            "description": translated or headline[:300],
        }
        if ts:
            try:
                dt = parse_date(ts)
                news_article["datePublished"] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except:
                pass
        item_list.append(news_article)

    return json.dumps([org, website, collection], ensure_ascii=False, indent=2)


def parse_date(ts):
    """灵活解析各种日期格式"""
    ts_clean = ts.replace("Z", "+00:00").replace(" GMT", "").strip()
    # 处理 "Tue, 14 Jul 2026 15:00:08 +0000"
    try:
        return datetime.strptime(ts_clean, "%a, %d %b %Y %H:%M:%S %z")
    except:
        pass
    # 处理 "2026-07-14T15:00:08+00:00"
    try:
        return datetime.fromisoformat(ts_clean)
    except:
        pass
    # 处理 "2026-07-14 19:21:42  +0800"
    ts_clean2 = ts.replace("Z", "+00:00").replace("  +", "+").strip()
    try:
        return datetime.strptime(ts_clean2, "%Y-%m-%d %H:%M:%S %z")
    except:
        pass
    return datetime.now(timezone.utc)


def format_time_for_display(ts):
    if not ts:
        return ""
    try:
        dt = parse_date(ts)
        return dt.astimezone(timezone.utc).strftime("%m月%d日 %H:%M")
    except:
        return ts


def format_time_iso(ts):
    if not ts:
        return ""
    try:
        dt = parse_date(ts)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except:
        return ts


def render():
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])
    fetched_at = data.get("fetchedAt", "")

    # ── Build cards HTML ──
    cards_html = []
    for a in articles:
        text = a.get("text", "")
        author = a.get("author", "")
        url = a.get("url", "")
        translated = a.get("translated", "")
        ts = a.get("createdAt", "")

        translated_html = ""
        if translated:
            translated_html = (
                f'<div class="card-translated">{escape(translated[:500])}'
                f'<span class="translated-label">（翻译）</span></div>'
            )

        meta_parts = [f'<span>{format_time_for_display(ts)}</span>']
        likes = a.get("likes")
        if likes is not None:
            meta_parts.append(f'<span class="likes">❤ {likes}</span>')
        retweets = a.get("retweets")
        if retweets is not None:
            meta_parts.append(f'<span class="retweets">🔁 {retweets}</span>')

        cards_html.append(f"""\
    <article class="card" itemscope itemtype="https://schema.org/NewsArticle">
      <meta itemprop="url" content="{escape(url)}">
      <meta itemprop="datePublished" content="{format_time_iso(ts)}">
      <meta itemprop="headline" content="{escape(text[:200])}">
      <div class="card-source"><a href="{escape(url)}" target="_blank" rel="noopener" itemprop="author" itemscope itemtype="https://schema.org/Organization"><span itemprop="name">{escape(author)}</span></a></div>
      <div class="card-text" itemprop="articleBody">{escape(text[:1000])}</div>
      {translated_html}
      <div class="card-meta">{"".join(meta_parts)}</div>
    </article>""")

    # ── Update time ──
    update_html = ""
    if fetched_at:
        try:
            dt = parse_date(fetched_at)
            update_html = f'<div class="last-update" id="lastUpdate"><time datetime="{dt.strftime("%Y-%m-%dT%H:%M:%SZ")}">🕐 更新于 {dt.strftime("%Y/%m/%d %H:%M")}</time></div>'
        except:
            update_html = f'<div class="last-update" id="lastUpdate">🕐 更新于 {escape(fetched_at)}</div>'

    news_content = "".join(cards_html) if cards_html else (
        '<div class="loading">暂无新闻，等待下次抓取</div>'
    )

    # ── JSON-LD Structured Data ──
    json_ld = generate_json_ld(articles, fetched_at)

    # ── Embedded news data for JS ──
    news_json = escape(json.dumps(data, ensure_ascii=False))

    html = f"""\
<!DOCTYPE html>
<html lang="zh-CN" prefix="og: https://ogp.me/ns#">
<head>
  <!-- ═══════════ 基础 SEO ═══════════ -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{SITE_NAME} — {SITE_DESC_SHORT}</title>
  <meta name="description" content="{SITE_DESC}">
  <meta name="keywords" content="全球新闻,国际新闻,科技新闻,财经新闻,新闻聚合,中文,翻译,Reuters,TechCrunch,BBC,NASA,WSJ,SCMP,澎湃,36氪">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <link rel="canonical" href="{SITE_URL}/">
  <meta name="language" content="zh-CN">
  <meta name="application-name" content="{SITE_NAME}">

  <!-- ═══════════ Open Graph / Facebook ═══════════ -->
  <meta property="og:type" content="website">
  <meta property="og:locale" content="zh_CN">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="{SITE_NAME} — {SITE_DESC_SHORT}">
  <meta property="og:description" content="{SITE_DESC}">
  <meta property="og:url" content="{SITE_URL}/">
  <meta property="og:image" content="{SITE_URL}/favicon.svg">
  <meta property="og:image:width" content="100">
  <meta property="og:image:height" content="100">
  <meta property="og:image:alt" content="{SITE_NAME} Logo">
  <meta property="og:updated_time" content="{format_time_iso(fetched_at) or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}">

  <!-- ═══════════ Twitter Card ═══════════ -->
  <meta name="twitter:card" content="summary">
  <meta name="twitter:site" content="@iannews">
  <meta name="twitter:title" content="{SITE_NAME} — {SITE_DESC_SHORT}">
  <meta name="twitter:description" content="{SITE_DESC}">
  <meta name="twitter:image" content="{SITE_URL}/favicon.svg">

  <!-- ═══════════ Feeds ═══════════ -->
  <link rel="alternate" type="application/rss+xml" title="{SITE_NAME} RSS Feed" href="{SITE_URL}/rss.xml">
  <link rel="alternate" type="application/atom+xml" title="{SITE_NAME} Atom Feed" href="{SITE_URL}/atom.xml">

  <!-- ═══════════ PWA / Manifest ═══════════ -->
  <link rel="manifest" href="{SITE_URL}/site.webmanifest">
  <meta name="theme-color" content="#1a1a1a">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="{SITE_NAME}">

  <!-- ═══════════ Favicon ═══════════ -->
  <link rel="icon" type="image/svg+xml" href="{SITE_URL}/favicon.svg">
  <link rel="apple-touch-icon" href="{SITE_URL}/favicon.svg">
  <link rel="mask-icon" href="{SITE_URL}/favicon.svg" color="#1da1f2">

  <!-- ═══════════ DNS Prefetch ═══════════ -->
  <link rel="dns-prefetch" href="https://iannews.cc">

  <!-- ═══════════ CSS ═══════════ -->
  <link rel="stylesheet" href="/style.css">

  <!-- ═══════════ JSON-LD Structured Data ═══════════ -->
  <script type="application/ld+json">
{json_ld}
  </script>

  <!-- ═══════════ Embedded Data ═══════════ -->
  <script>
    window.__NEWS_DATA__ = {news_json};
  </script>
</head>
<body>
  <header>
    <div class="container header-inner">
      <a href="/" class="logo-link" aria-label="{SITE_NAME} 首页">
        <h1 class="logo">{SITE_NAME}</h1>
      </a>
      <span class="tagline">{SITE_DESC_SHORT}</span>
    </div>
  </header>

  <main class="container">
    <div class="mission">{SITE_DESC}</div>
    {update_html}
    <div class="news-list" id="newsList">
      {news_content}
    </div>
  </main>

  <footer>
    <div class="container footer-inner">
      <p>&copy; 2026 <a href="{SITE_URL}/">{SITE_NAME}</a> · 数据来源公开 RSS · <a href="{SITE_URL}/rss.xml">RSS</a> · <a href="{SITE_URL}/atom.xml">Atom</a></p>
    </div>
  </footer>

  <script src="/script.js"></script>
</body>
</html>"""

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ index.html 已生成 ({len(articles)} 条新闻, JSON-LD 结构化数据)")


if __name__ == "__main__":
    render()
