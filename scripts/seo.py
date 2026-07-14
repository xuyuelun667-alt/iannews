#!/usr/bin/env python3
"""
SEO 静态资源生成器
生成: sitemap.xml, robots.txt, rss.xml, favicon.svg, site.webmanifest
"""

import json
import os
from datetime import datetime, timezone
from html import escape

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
NEWS_FILE = os.path.join(PROJECT_ROOT, "data", "news.json")
SITE_URL = "https://iannews.cc"

LATEST_NEWS = ""
NEWS_COUNT = 0
ARTICLES = []


def load_news():
    global LATEST_NEWS, NEWS_COUNT, ARTICLES
    try:
        with open(NEWS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        ARTICLES = data.get("articles", [])
        NEWS_COUNT = len(ARTICLES)
        if ARTICLES:
            ts = ARTICLES[0].get("createdAt", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    LATEST_NEWS = dt.strftime("%Y-%m-%d")
                except:
                    LATEST_NEWS = ts[:10]
    except:
        pass


# ─── Sitemap ───────────────────────────────────────────

def gen_sitemap():
    path = os.path.join(PROJECT_ROOT, "sitemap.xml")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lastmod = LATEST_NEWS + "T00:00:00Z" if LATEST_NEWS else now

    urls = [f"""\
  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>"""]

    # 为可发现的内容生成独立 URL (推荐给 Google Discover)
    for a in ARTICLES[:30]:
        aid = a.get("id", "")
        ts = a.get("createdAt", "")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00").replace(" +0000", "+00:00").replace(" GMT", "").replace(" +", "+").rsplit(" ", 1)[0] if " " in ts and "+" not in ts and "Z" not in ts else ts)
                lastmod_art = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except:
                lastmod_art = now
        else:
            lastmod_art = now
        urls.append(f"""\
  <url>
    <loc>{SITE_URL}/?news={escape(aid)}</loc>
    <lastmod>{lastmod_art}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"✅ sitemap.xml ({len(urls)} 条 URL)")


# ─── robots.txt ────────────────────────────────────────

def gen_robots():
    path = os.path.join(PROJECT_ROOT, "robots.txt")
    content = f"""\
# robots.txt for IanNews
# https://iannews.cc

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: CCBot
Allow: /

User-agent: Applebot
Allow: /

User-agent: Twitterbot
Allow: /

User-agent: Slackbot
Allow: /

User-agent: *
Allow: /
Crawl-delay: 2

Sitemap: {SITE_URL}/sitemap.xml
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ robots.txt")


# ─── RSS Feed ──────────────────────────────────────────

def gen_rss():
    path = os.path.join(PROJECT_ROOT, "rss.xml")
    now_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for a in ARTICLES[:30]:
        title = a.get("text", "")[:120].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        link = escape(a.get("url", ""))
        author = escape(a.get("author", ""))
        desc = a.get("translated", "") or a.get("text", "")[:500]
        desc = desc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")[:1000]
        ts = a.get("createdAt", "")
        pubdate = now_str
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00").replace(" +0000", "+00:00").replace(" GMT", "").rsplit(" ", 1)[0] if " " in ts and "+" not in ts and "Z" not in ts else ts)
                pubdate = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
            except:
                pass
        guid = escape(a.get("id", link))
        items.append(f"""\
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description><![CDATA[{desc}]]></description>
      <author>{author}</author>
      <pubDate>{pubdate}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
      <source url="{link}">{author}</source>
    </item>""")

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>IanNews - 全球新闻聚合</title>
    <link>{SITE_URL}/</link>
    <description>降低获取全球信息的门槛。精选可信来源，减少信息噪音，让您更高效地了解世界。</description>
    <language>zh-cn</language>
    <lastBuildDate>{now_str}</lastBuildDate>
    <docs>https://www.rssboard.org/rss-specification</docs>
    <generator>IanNews SEO Engine</generator>
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>
    <image>
      <url>{SITE_URL}/favicon.svg</url>
      <title>IanNews</title>
      <link>{SITE_URL}/</link>
    </image>
{chr(10).join(items)}
  </channel>
</rss>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(rss_xml)
    print(f"✅ rss.xml ({len(items)} 条目)")


# ─── Atom Feed ─────────────────────────────────────────

def gen_atom():
    path = os.path.join(PROJECT_ROOT, "atom.xml")
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries = []
    for a in ARTICLES[:30]:
        title = escape(a.get("text", "")[:120])
        link = escape(a.get("url", ""))
        author = escape(a.get("author", ""))
        content_text = a.get("translated", "") or a.get("text", "")[:500]
        content_text = escape(content_text[:1000])
        ts = a.get("createdAt", "")
        updated = now_iso
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00").replace(" +0000", "+00:00").replace(" GMT", "").rsplit(" ", 1)[0] if " " in ts and "+" not in ts and "Z" not in ts else ts)
                updated = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except:
                pass
        eid = escape(a.get("id", link))
        entries.append(f"""\
  <entry>
    <title>{title}</title>
    <link href="{link}" rel="alternate"/>
    <id>{eid}</id>
    <updated>{updated}</updated>
    <author><name>{author}</name></author>
    <summary type="html"><![CDATA[{content_text}]]></summary>
  </entry>""")

    atom_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>IanNews - 全球新闻聚合</title>
  <subtitle>降低获取全球信息的门槛</subtitle>
  <link href="{SITE_URL}/" rel="alternate"/>
  <link href="{SITE_URL}/atom.xml" rel="self" type="application/atom+xml"/>
  <id>{SITE_URL}/</id>
  <updated>{now_iso}</updated>
  <author>
    <name>IanNews</name>
  </author>
  <generator>IanNews SEO Engine</generator>
{chr(10).join(entries)}
</feed>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(atom_xml)
    print(f"✅ atom.xml ({len(entries)} 条目)")


# ─── Favicon SVG ───────────────────────────────────────

def gen_favicon():
    path = os.path.join(PROJECT_ROOT, "favicon.svg")
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1da1f2"/>
      <stop offset="100%" style="stop-color:#0d7bc1"/>
    </linearGradient>
  </defs>
  <rect width="100" height="100" rx="20" fill="url(#g)"/>
  <text x="50" y="68" font-family="Arial,sans-serif" font-size="52" font-weight="bold" fill="white" text-anchor="middle">i</text>
</svg>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print("✅ favicon.svg")


# ─── Web Manifest ──────────────────────────────────────

def gen_manifest():
    path = os.path.join(PROJECT_ROOT, "site.webmanifest")
    manifest = {
        "name": "IanNews - 全球新闻聚合",
        "short_name": "IanNews",
        "description": "降低获取全球信息的门槛。精选可信来源，减少信息噪音。",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#1a1a1a",
        "theme_color": "#1a1a1a",
        "lang": "zh-CN",
        "icons": [
            {
                "src": "/favicon.svg",
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            }
        ]
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("✅ site.webmanifest")


# ─── Google Search Console Verification ────────────────

def gen_verification():
    """生成 google*.html 占位文件 —— 用户需在 Search Console 下载实际文件替换"""
    path = os.path.join(PROJECT_ROOT, "googleXXXXXX.html")
    content = """<!DOCTYPE html>
<html><head>
  <meta name="google-site-verification" content="XXXXXXXXXX" />
  <title>Google Search Console Verification</title>
</head><body>
  <p>This file verifies ownership of iannews.cc for Google Search Console.</p>
  <p>Replace this file with the actual verification file downloaded from Google.</p>
</body></html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ googleXXXXXX.html (占位，需替换)")


# ─── Main ──────────────────────────────────────────────

def main():
    load_news()
    gen_sitemap()
    gen_robots()
    gen_rss()
    gen_atom()
    gen_favicon()
    gen_manifest()
    gen_verification()
    print("\n✅ SEO 静态资源全部生成")


if __name__ == "__main__":
    main()
