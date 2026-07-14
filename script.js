/**
 * IanNews - 前端脚本
 * 优先使用 HTML 中嵌入的数据 (window.__NEWS_DATA__)，
 * 如果不可用则回退 fetch data/news.json。
 */

async function loadNews() {
  const list = document.getElementById('newsList');
  const update = document.getElementById('lastUpdate');

  try {
    let data;

    // 优先使用 HTML 中已嵌入的数据（爬虫友好）
    if (window.__NEWS_DATA__) {
      data = window.__NEWS_DATA__;
    } else {
      const res = await fetch('data/news.json');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      data = await res.json();
    }

    if (!data.articles || data.articles.length === 0) {
      // HTML 中已经有 "暂无新闻" 提示，无需重复设置
      return;
    }

    if (data.fetchedAt) {
      const d = new Date(data.fetchedAt);
      if (!update.textContent) {
        update.textContent = '🕐 更新于 ' + d.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
      }
    }

    // 内容已由后端渲染在 HTML 中，JS 只负责动态更新（如果有新数据）
    // 实际新闻内容爬虫已经在 HTML 中看到了

  } catch (err) {
    list.innerHTML = `<div class="error">加载失败: ${escapeHtml(err.message)}</div>`;
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

loadNews();
