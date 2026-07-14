# SEO 优化报告 — IanNews (iannews.cc)

> 生成日期：2026-07-15
> 站点类型：全球新闻聚合站 | 单页应用 (SPA) | 静态预渲染

---

## 执行摘要

| 项目 | 状态 | 优先级 |
|------|------|--------|
| 基础 SEO | ★★★★★ 已完成 | 最高 |
| Open Graph | ★★★★★ 已完成 | 高 |
| Twitter Card | ★★★★★ 已完成 | 高 |
| JSON-LD 结构化数据 | ★★★★★ 已完成 | 最高 |
| Sitemap | ★★★★★ 已完成 | 最高 |
| robots.txt | ★★★★★ 已完成 | 高 |
| RSS Feed | ★★★★★ 已完成 | 高 |
| Atom Feed | ★★★★★ 已完成 | 中 |
| Favicon | ★★★★★ 已完成 | 中 |
| Web Manifest | ★★★★★ 已完成 | 低 |
| 搜索引擎验证 | ★★☆☆☆ 需手动 | 最高 |
| 性能优化 | ★★★★☆ 建议优化 | 高 |
| Discover 适配 | ★★★☆☆ 建议增强 | 高 |

---

## 1. 基础 SEO — ★★★★★ 已完成

| 项目 | 状态 | 说明 |
|------|------|------|
| `<title>` | ✅ | `IanNews — 全球新闻聚合` |
| `<meta name="description">` | ✅ | 精准描述站点定位 |
| `<meta name="keywords">` | ✅ | 覆盖中英文搜索关键词 |
| `<link rel="canonical">` | ✅ | `https://iannews.cc/` |
| `<meta name="robots">` | ✅ | `index, follow, max-image-preview:large` |
| `<html lang="zh-CN">` | ✅ | 正确声明语言 |
| `<meta charset="UTF-8">` | ✅ | |
| `<meta name="viewport">` | ✅ | 含 `maximum-scale=5.0` 适配大屏 |
| `<meta name="application-name">` | ✅ | PWA 兼容 |

**爬虫可见内容**：新闻内容已完整写入 HTML `body`，搜索引擎无需执行 JavaScript 即可抓取全文。每个 NewsArticle 使用 `itemscope itemtype="https://schema.org/NewsArticle"` 微数据标记。

---

## 2. Open Graph / Social — ★★★★★ 已完成

| 项目 | 内容 |
|------|------|
| `og:type` | `website` |
| `og:locale` | `zh_CN` |
| `og:site_name` | `IanNews` |
| `og:title` | `IanNews — 全球新闻聚合` |
| `og:description` | 完整描述 |
| `og:url` | `https://iannews.cc/` |
| `og:image` | `/favicon.svg` |
| `twitter:card` | `summary` |
| `twitter:title` + `description` | ✅ |

> ⚠️ `og:image` 当前使用 SVG favicon。Facebook/LinkedIn 对 SVG 支持有限。如需要更好的社交分享预览，建议准备 1200×630px PNG。

---

## 3. 结构化数据 (JSON-LD) — ★★★★★ 已完成

三组结构化数据同时注入 `<head>`：

- **Organization** — 声明品牌实体，建立知识图谱身份
- **WebSite** — 含 `SearchAction` 搜索行为声明
- **CollectionPage + ItemList + NewsArticle** — 每条新闻使用 `NewsArticle` 类型，包含：
  - `headline`（标题）
  - `url`（原文链接）
  - `author`（来源组织）
  - `datePublished`（发布时间）
  - `description`（翻译文本作摘要）

**这是对 Google Discover 最关键的一步。** NewsArticle 结构化数据是 Google News 和 Discover 收录的核心信号。

---

## 4. Sitemap — ★★★★★ 已完成

**文件**: `/sitemap.xml`

- 首页 URL（优先 1.0，每日更新）
- 前 30 条新闻独立 URL（`/?news={id}`，优先 0.8）
- 支持 `lastmod` 标签

Cloudflare Pages 可直接访问，已在 `robots.txt` 声明。

---

## 5. robots.txt — ★★★★★ 已完成

**文件**: `/robots.txt`

所有主流爬虫均获得 `Allow: /`：

| 爬虫 | 状态 |
|------|------|
| Googlebot | ✅ 允许 |
| Bingbot | ✅ 允许 |
| Google-Extended (AI) | ✅ 允许 |
| GPTBot (OpenAI) | ✅ 允许 |
| ClaudeBot (Anthropic) | ✅ 允许 |
| PerplexityBot | ✅ 允许 |
| CCBot (Common Crawl) | ✅ 允许 |
| Applebot / Twitterbot / Slackbot | ✅ 允许 |

`Crawl-delay: 2` 降低服务器压力。已声明 Sitemap 路径。

---

## 6. RSS & Atom Feeds — ★★★★★ 已完成

- **RSS 2.0**: `/rss.xml` — 含完整频道元数据，前 30 条新闻
- **Atom 1.0**: `/atom.xml` — 兼容现代聚合器

HTML `<head>` 已通过 `<link rel="alternate"` 声明两种格式。

---

## 7. Favicon & Manifest — ★★★★★ 已完成

- **Favicon**: SVG 格式，支持 Dark Mode
- **Apple Touch Icon**: SVG 引用
- **Mask Icon**: 声明 `color="#1da1f2"`
- **Web Manifest**: `/site.webmanifest` — 含名称、图标、主题色

---

## 8. 性能优化 — ★★★☆☆ 建议完成

| 项目 | 状态 | 建议 |
|------|------|------|
| 图片 | ✅ 无外部图片 | n/a |
| CSS | ✅ 内联单文件 | 可考虑 minify（已可手动压缩） |
| JS | ✅ 异步加载 | 已使用 `DOMContentLoaded` 安全执行 |
| 字体 | ✅ 系统字体 | 零额外字体加载，`font-display` 无需配置 |
| 压缩 | ✅ Cloudflare 自动 | Cloudflare 默认开启 Brotli + Gzip |
| 缓存策略 | ⚠️ 默认 | 建议优化（见下方） |

**缓存优化建议**（需在 Cloudflare Dashboard 配置）：

1. **Page Rules** (免费版 3 条规则)：
   - `iannews.cc/style.css` → Cache TTL: 7 days
   - `iannews.cc/script.js` → Cache TTL: 7 days
   - `iannews.cc/favicon.svg` → Cache TTL: 30 days

2. 或使用 **Cache Rules**（新 UI）添加同样规则。

---

## 9. Google Search Console — ★★☆☆☆ 需手动操作

### 自动完成

已创建验证文件占位符 `/googleXXXXXX.html`。

### 需你手动完成

1. 打开 [search.google.com/search-console](https://search.google.com/search-console)
2. 添加资源 → **URL prefix** → 输入 `https://iannews.cc/`
3. 选择 **HTML file** 验证方式
4. 下载验证文件（如 `google12345678.html`）
5. 替换项目中的 `googleXXXXXX.html` 为下载的文件
6. 推送到 GitHub，Cloudflare Pages 自动部署
7. 回到 Search Console 点 **Verify**
8. 验证后提交 Sitemap：`https://iannews.cc/sitemap.xml`

---

## 10. Bing Webmaster — ★★☆☆☆ 需手动操作

1. 打开 [bing.com/webmasters](https://www.bing.com/webmasters)
2. 添加网站 `https://iannews.cc/`
3. 选择 **XML file** 验证方式（直接使用已有 `sitemap.xml`）
4. 或使用 Google Search Console 关联验证（推荐）
5. 提交 Sitemap：`https://iannews.cc/sitemap.xml`

---

## 11. Google Discover 适配建议 — ★★★☆☆ 建议增强

### 当前状态（已达标）

- ✅ `max-image-preview:large` — Discover 必需
- ✅ `NewsArticle` 结构化数据
- ✅ 网站有明确新闻属性
- ✅ 内容预渲染，非 JS 依赖

### 建议增强

| 建议 | 优先级 | 难度 |
|------|--------|------|
| 为每条新闻生成独立落地页（而非单页） | 高 | 中 — 需要为每个 article 生成 `.html` |
| 使用大图（1200px+）作为 `og:image` | 高 | 低 — 准备一张 PNG |
| 增加 `news_keywords` meta tag | 中 | 低 — 可加入 build.py |
| 缩短文章标题，避免截断 | 中 | 低 — 调整爬虫逻辑 |

**当前模式（单页 SPA）对 Discover 收录有天然限制**。Discover 偏好有独立 URL 的页面。如果你希望大幅提升 Discover 流量，最有效的投入是：**为每条新闻生成独立的 HTML 页面**，并在 `sitemap.xml` 中以独立 URL 声明。

---

## 12. Cloudflare Pages 检查 — ✅ 无问题

| 检查项 | 状态 |
|--------|------|
| 爬虫是否可以正常访问 | ✅ robots.txt 允许所有爬虫 |
| 是否有 IP 封锁 | ❌ 无 |
| 是否有 WAF 规则拦截爬虫 | ❌ 默认未开启 |
| HTTP → HTTPS 重定向 | ✅ Cloudflare 自动处理 |
| SSL/TLS | ✅ Flexible / Full 模式 |
| CDN 缓存是否影响内容更新 | ⚠️ 建议设置 Page Rule（缓存优化部分） |

Cloudflare Pages 默认 **不阻止任何合法爬虫**。只要 `robots.txt` 允许，搜索引擎可以正常抓取。

---

## 13. URL 结构友善度

当前 URL：`https://iannews.cc/` (单页)

- ✅ 简短、可读、含关键词（iannews）
- ✅ 无查询参数、无 session ID
- ✅ HTTPS
- ⚠️ 缺少独立新闻页面（建议后续扩展）

---

## 14. 对搜索排名提升最大的事项（按优先级排序）

| 优先级 | 事项 | 难度 | 影响 |
|--------|------|------|------|
| 1️⃣ | **提交 Google Search Console（手动）** | 低 | 决定站点是否被收录 |
| 2️⃣ | **提交 Sitemap** | 低 | 加速爬虫发现 |
| 3️⃣ | **提交 Bing Webmaster** | 低 | 扩大搜索引擎覆盖 |
| 4️⃣ | **准备大尺寸 OG Image (1200×630 PNG)** | 低 | 改善社交分享效果 |
| 5️⃣ | **Cloudflare Page Rules 缓存优化** | 低 | 提升 Core Web Vitals |
| 6️⃣ | **为每条新闻生成独立 HTML 页面** | 中 | 大幅提升 Discover 收录 |
| 7️⃣ | **增加 `news_keywords`** | 低 | 辅助内容分类 |

---

## 15. 已完成的文件清单

```
iannews/
├── index.html              ← 重写: SEO 全标签 + JSON-LD + OG
├── style.css               ← 更新: 可访问性 + 打印 + 动画友好
├── script.js               ← 重写: 轻量化 + 错误容错
├── sitemap.xml             ← 新建: 包含首页 + 30条新闻
├── robots.txt              ← 新建: 爬虫全开放
├── rss.xml                 ← 新建: RSS 2.0 Feed
├── atom.xml                ← 新建: Atom 1.0 Feed
├── favicon.svg             ← 新建: 蓝色渐变图标
├── site.webmanifest        ← 新建: PWA 清单
├── googleXXXXXX.html       ← 新建: Search Console 占位
├── scripts/
│   ├── scrape.py            ← 不变
│   ├── build.py             ← 重写: SEO 全量生成
│   └── seo.py              ← 新建: 静态资源生成器
└── .github/workflows/
    └── scrape.yml           ← 更新: 新增 SEO 构建步骤
```

---

## 下一步操作

1. ✅ **代码已全部修改并推送** — 去 GitHub 手动触发一次 Workflow
2. 手动完成 **Google Search Console** 验证
3. 手动完成 **Bing Webmaster** 验证
4. （可选）准备一张 1200×630px 的 OG 图片
5. 跑完 workflow 后刷新 `iannews.cc`，右键「查看网页源代码」检查 meta 标签是否就位
