"""
Twitter / X API v2 新闻抓取脚本
后续接入 X API 后填充逻辑。
"""

import json
import os
from datetime import datetime, timezone

def main():
    # TODO: 接入 X API v2
    # bearer = os.environ.get("X_API_BEARER")
    # 搜索指定账号的最新推文
    # 写入 data/news.json

    news_file = os.path.join(os.path.dirname(__file__), "..", "data", "news.json")

    # 临时占位：留空
    data = {
        "fetchedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "articles": []
    }

    with open(news_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ Scrape placeholder run complete.")

if __name__ == "__main__":
    main()
