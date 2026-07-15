/**
 * IanNews - 前端脚本
 * 优先使用 HTML 中嵌入的数据 (window.__NEWS_DATA__)，
 * 如果不可用则回退 fetch data/news.json。
 */

async function loadNews() {
  const list = document.getElementById('newsList');
  const update = document.getElementById('lastUpdate');
  if (!list) return;

  try {
    let data;

    // 优先使用 HTML 中已嵌入的数据（爬虫友好）
    if (window.__NEWS_DATA__ && window.__NEWS_DATA__.articles) {
      data = window.__NEWS_DATA__;
    } else {
      const res = await fetch('data/news.json');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      data = await res.json();
    }

    if (!data.articles || data.articles.length === 0) {
      // HTML 中已经有 "暂无新闻" 提示
      return;
    }

    // 更新更新时间
    if (update && data.fetchedAt) {
      const d = new Date(data.fetchedAt);
      update.textContent = '🕐 更新于 ' + d.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
    }

    // 如果 HTML 里已经有渲染好的内容（__NEWS_DATA__ 模式下），就不重复渲染
    if (window.__NEWS_DATA__) return;

    // 回退渲染（当 JS 独立加载 data/news.json 时使用）
    list.innerHTML = data.articles.map(a => {
      const text = escapeHtml(a.text);
      const author = escapeHtml(a.author);
      const url = escapeHtml(a.url);
      const translated = a.translated ? `
        <div class="card-translated">${escapeHtml(a.translated.slice(0, 500))}<span class="translated-label">（翻译）</span></div>` : '';
      const meta = `<span>${formatTime(a.createdAt)}</span>`
        + (a.likes != null ? `<span class="likes">❤ ${a.likes}</span>` : '')
        + (a.retweets != null ? `<span class="retweets">🔁 ${a.retweets}</span>` : '');
      return `
      <div class="card">
        <div class="card-source"><a href="${url}" target="_blank" rel="noopener">${author}</a></div>
        <div class="card-text">${text}</div>
        ${translated}
        <div class="card-meta">${meta}</div>
      </div>`;
    }).join('');

  } catch (err) {
    list.innerHTML = `<div class="error">加载失败: ${escapeHtml(err.message)}</div>`;
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

loadNews();
