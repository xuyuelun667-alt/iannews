#!/usr/bin/env python3
"""
读取 data/news.json，生成 index.html。
上半部分：主流新闻网站导航；下半部分：最新 50 条新闻摘要。
"""

import json
import os
from html import escape
from datetime import datetime

NEWS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "news.json")
INDEX_FILE = os.path.join(os.path.dirname(__file__), "..", "index.html")

# ═══ 主流新闻网站导航 ═══
NAV_GROUPS = [
    {
        "title": "综合新闻",
        "icon": "🌐",
        "items": [
            ("新华网", "https://www.news.cn", "新华社官方门户"),
            ("人民网", "http://www.people.com.cn", "人民日报旗下"),
            ("澎湃新闻", "https://www.thepaper.cn", "深度时政调查"),
            ("界面新闻", "https://www.jiemian.com", "商业与财经"),
            ("新浪新闻", "https://news.sina.com.cn", "门户新闻"),
            ("腾讯新闻", "https://news.qq.com", "门户新闻"),
        ],
    },
    {
        "title": "国际媒体",
        "icon": "🌍",
        "items": [
            ("BBC 中文", "https://www.bbc.com/zhongwen/simp", "英国广播公司中文"),
            ("FT 中文网", "https://www.ftchinese.com", "英国金融时报中文"),
            ("华尔街日报中文", "https://cn.wsj.com", "WSJ 中文版"),
            ("纽约时报中文", "https://cn.nytimes.com", "NYT 中文网"),
            ("Reuters", "https://www.reuters.com", "路透社（英文）"),
            ("CNN", "https://www.cnn.com", "美国有线电视新闻网（英文）"),
        ],
    },
    {
        "title": "科技互联网",
        "icon": "💻",
        "items": [
            ("IT之家", "https://www.ithome.com", "科技数码快讯"),
            ("36氪", "https://36kr.com", "创投与科技"),
            ("虎嗅", "https://www.huxiu.com", "商业科技洞察"),
            ("爱范儿", "https://www.ifanr.com", "科技与生活方式"),
            ("少数派", "https://sspai.com", "效率工具与数字生活"),
            ("量子位", "https://www.qbitai.com", "AI 前沿报道"),
            ("机器之心", "https://www.jiqizhixin.com", "AI 产业与学术"),
            ("Solidot", "https://www.solidot.org", "奇客科技情报"),
        ],
    },
    {
        "title": "财经金融",
        "icon": "📈",
        "items": [
            ("东方财富", "https://www.eastmoney.com", "行情与资讯"),
            ("新浪财经", "https://finance.sina.com.cn", "财经门户"),
            ("华尔街见闻", "https://wallstreetcn.com", "全球市场快讯"),
            ("雪球", "https://xueqiu.com", "投资者社区"),
            ("财新", "https://www.caixin.com", "深度财经报道"),
        ],
    },
    {
        "title": "游戏",
        "icon": "🎮",
        "items": [
            ("游民星空", "https://www.gamersky.com", "游戏资讯门户"),
            ("机核 GCORES", "https://www.gcores.com", "游戏文化媒体"),
            ("游研社", "https://www.yystv.cn", "游戏深度研究"),
            ("触乐", "https://www.chuapp.com", "游戏媒体"),
            ("TapTap", "https://www.taptap.cn", "手游社区"),
        ],
    },
    {
        "title": "教育",
        "icon": "🎓",
        "items": [
            ("芥末堆", "https://www.jiemodui.com", "教育行业资讯"),
            ("中国教育在线", "https://www.eol.cn", "综合教育门户"),
            ("中国教育新闻网", "https://www.jyb.cn", "教育综合新闻"),
            ("教育部官网", "https://www.moe.gov.cn", "教育政策与公告"),
            ("多知网", "https://www.duozhi.com", "教育培训行业"),
        ],
    },
]


def nav_html():
    blocks = []
    for g in NAV_GROUPS:
        links = "".join(
            f'<a class="nav-site" href="{url}" target="_blank" rel="noopener">'
            f'<span class="ns-name">{escape(name)}</span>'
            f'<span class="ns-desc">{escape(desc)}</span></a>'
            for name, url, desc in g["items"]
        )
        blocks.append(
            f'<section class="nav-group"><h2>{g["icon"]} {g["title"]}</h2>'
            f'<div class="nav-grid">{links}</div></section>'
        )
    return "\n      ".join(blocks)


def render():
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])

    cards_html = []
    for a in articles:
        text = escape(a.get("text", ""))
        author = escape(a.get("author", ""))
        url = escape(a.get("url", ""))
        translated = a.get("translated", "")
        translated_html = ""
        if translated:
            translated_html = (
                f'<div class="card-translated">{escape(translated[:500])}'
                f'<span class="translated-label">（翻译）</span></div>'
            )
        ts = a.get("createdAt", "")
        time_str = ""
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                time_str = dt.strftime("%m月%d日 %H:%M")
            except Exception:
                time_str = ts

        cards_html.append(f"""\
    <div class="card">
        <div class="card-source"><a href="{url}" target="_blank" rel="noopener">{author}</a></div>
        <div class="card-text">{text[:400]}</div>
        {translated_html}
        <div class="card-meta"><span>{time_str}</span><a class="card-full" href="{url}" target="_blank" rel="noopener">阅读原文 ↗</a></div>
    </div>""")

    fetched_at = data.get("fetchedAt", "")
    update_html = ""
    if fetched_at:
        try:
            dt = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
            update_html = f'<div class="last-update" id="lastUpdate">🕐 更新于 {dt.strftime("%Y/%m/%d %H:%M")}</div>'
        except Exception:
            pass

    news_content = "".join(cards_html) if cards_html else (
        '<div class="loading">暂无新闻，等待下次抓取</div>'
    )

    news_json = escape(json.dumps(data, ensure_ascii=False))

    html = f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IanNews - 新闻导航与每日速递</title>
  <link rel="stylesheet" href="style.css">
  <script>
    // 新闻数据已内置在 HTML 中，无需额外 fetch
    window.__NEWS_DATA__ = {news_json};
  </script>
</head>
<body>
  <nav class="nav">
    <div class="container">
      <a class="logo" href="https://iannews.cc">IanNews</a>
      <a class="sbtn on" href="https://iannews.cc">📰 首页</a>
      <a class="sbtn" href="https://finance.iannews.cc">📈 金融</a>
      <a class="sbtn" href="https://ai.iannews.cc">🤖 AI</a>
      <a class="sbtn" href="https://gaming.iannews.cc">🎮 游戏</a>
      <a class="sbtn" href="https://3c.iannews.cc">📱 3C</a>
      <a class="sbtn" href="https://supports.iannews.cc">🎧 客服</a>
      <a class="sbtn" href="https://edu.iannews.cc">🎓 教育</a>
    </div>
  </nav>
  <header>
    <div class="container header-inner">
      <h1 class="logo">IanNews</h1>
      <span class="tagline">主流新闻导航 · 每日精选速递</span>
    </div>
  </header>

  <main class="container">
    <div class="mission">导航主流新闻网站，精选可信来源，减少信息噪音。</div>
    <div class="nav-section">
      {nav_html()}
    </div>

    <h2 class="news-heading">📰 最新速递（50 条）</h2>
    {update_html}
    <div class="news-list" id="newsList">
      {news_content}
    </div>
  </main>

  <footer>
    <div class="container footer-inner">
      <p>&copy; 2026 IanNews · 数据来源 RSS · 版权归原媒体所有</p>
    </div>
  </footer>

  <script src="script.js"></script>
</body>
</html>"""

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ index.html 已生成（导航 {sum(len(g['items']) for g in NAV_GROUPS)} 站 + {len(articles)} 条新闻）")


if __name__ == "__main__":
    render()
