# IanNews

从 Twitter/X 抓取新闻，每两天更新一次。

## 技术栈

- **托管**：Cloudflare Pages
- **定时抓取**：GitHub Actions → Python
- **数据**：静态 JSON 文件（`data/news.json`）

## 目录

```
iannews/
├── index.html          # 首页
├── style.css           # 样式
├── script.js           # 前端 JS
├── _redirects          # Cloudflare 路由配置
├── data/
│   └── news.json       # 新闻数据（由抓取脚本更新）
├── scripts/
│   └── scrape.py       # Twitter 抓取脚本
└── .github/workflows/
    └── scrape.yml      # 定时工作流
```
