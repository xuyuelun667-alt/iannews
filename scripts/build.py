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
    <div class="card">
        <div class="card-source"><a href="{url}" target="_blank" rel="noopener">{author}</a></div>
        <div class="card-text">{text[:1000]}</div>
        {translated_html}
        <div class="card-meta">{"".join(meta_parts)}</div>
    </div>""")

    fetched_at = data.get("fetchedAt", "")
    update_html = ""
    if fetched_at:
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
            update_html = f'<div class="last-update">🕐 更新于 {dt.strftime("%Y/%m/%d %H:%M")}</div>'
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
  <header>
    <div class="container header-inner">
      <h1 class="logo">IanNews</h1>
      <span class="tagline">每日速递 · 精选推文</span>
    </div>
  </header>

  <main class="container">
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
