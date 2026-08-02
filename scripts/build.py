#!/usr/bin/env python3
"""
读取 data/news.json，生成 index.html（新闻内容直接写入 HTML）。
爬虫 / AI 不需要执行 JS 就能看到新闻。
"""

import json
import os
from html import escape

NEWS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "news.json")
INDEX_FILE = os.path.join(os.path.dirname(__file__), "..", "index.html")


def render():
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    articles = data.get("articles", [])

    cards_html = []
    for idx, a in enumerate(articles):
        text = escape(a.get("text", ""))
        author = escape(a.get("author", ""))
        url = escape(a.get("url", ""))
        content = a.get("content", "")
        translated = a.get("translated", "")
        translated_html = ""
        if translated:
            translated_html = (
                f'<div class="card-translated">{escape(translated[:500])}'
                f'<span class="translated-label">（翻译）</span></div>'
            )
        # 正文全文：有则折叠展示，无则回退摘要
        body_html = ""
        if content:
            body_html = (
                f'<details class="card-body-wrap">'
                f'<summary>📖 展开全文（{len(content)}字）</summary>'
                f'<div class="card-body">'
                + "<br><br>".join(escape(p) for p in content.split("\n\n"))
                + f'</div><a class="card-full" href="{url}" target="_blank" rel="noopener">阅读原文 ↗</a></details>'
            )
        author_short = escape(a.get("author", ""))[:20]
        ts = a.get("createdAt", "")
        time_str = ""
        if ts:
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                time_str = dt.strftime("%m月%d日 %H:%M")
            except:
                time_str = ts
        likes = a.get("likes")
        meta_parts = [f'<span>{time_str}</span>']
        if likes is not None:
            meta_parts.append(f'<span class="likes">❤ {likes}</span>')
        retweets = a.get("retweets")
        if retweets is not None:
            meta_parts.append(f'<span class="retweets">🔁 {retweets}</span>')

        cards_html.append(f"""\
    <div class="card" id="card-{idx}">
        <div class="card-source"><a href="{url}" target="_blank" rel="noopener">{author}</a></div>
        <div class="card-text">{text[:400]}</div>
        {translated_html}
        {body_html}
        <div class="card-meta">{"".join(meta_parts)}</div>
    </div>""")

    fetched_at = data.get("fetchedAt", "")
    update_html = ""
    if fetched_at:
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
            update_html = f'<div class="last-update" id="lastUpdate">🕐 更新于 {dt.strftime("%Y/%m/%d %H:%M")}</div>'
        except:
            pass

    news_content = "".join(cards_html) if cards_html else (
        '<div class="loading">暂无新闻，等待下次抓取</div>'
    )

    # 把新闻数据也嵌入为 JSON，供 JS 使用
    news_json = escape(json.dumps(data, ensure_ascii=False))

    html = f"""\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IanNews - 每日速递</title>
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
      <span class="tagline">降低获取全球信息的门槛</span>
    </div>
  </header>

  <main class="container">
    <div class="mission">精选可信来源，减少信息噪音，让您更高效地了解世界。</div>
    {update_html}
    <div class="news-list" id="newsList">
      {news_content}
    </div>
  </main>

  <footer>
    <div class="container footer-inner">
      <p>&copy; 2026 IanNews · 数据来源 RSS</p>
    </div>
  </footer>

  <script src="script.js"></script>
</body>
</html>"""

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ index.html 已生成 ({len(articles)} 条新闻嵌入)")


if __name__ == "__main__":
    render()
