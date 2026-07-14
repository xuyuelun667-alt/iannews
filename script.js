async function loadNews() {
  const list = document.getElementById('newsList');
  const update = document.getElementById('lastUpdate');

  try {
    const res = await fetch('data/news.json');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (!data.articles || data.articles.length === 0) {
      list.innerHTML = '<div class="loading">暂无新闻，等待下次抓取</div>';
      return;
    }

    if (data.fetchedAt) {
      const d = new Date(data.fetchedAt);
      update.textContent = '🕐 更新于 ' + d.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
    }

    list.innerHTML = data.articles.map((a, i) => {
      const hasTranslated = a.translated && a.translated.length > 0;
      const isChinese = /[\u4e00-\u9fff]/.test(a.author);
      return `
      <div class="card">
        <div class="card-source">
          <a href="${escapeHtml(a.url)}" target="_blank" rel="noopener">${escapeHtml(a.author)}</a>
        </div>
        <div class="card-text">${escapeHtml(a.text)}</div>
        ${hasTranslated ? `<div class="card-translated">${escapeHtml(a.translated)}<span class="translated-label">（翻译）</span></div>` : ''}
        <div class="card-meta">
          <span>${formatTime(a.createdAt)}</span>
          ${a.likes != null ? `<span class="likes">❤ ${a.likes}</span>` : ''}
          ${a.retweets != null ? `<span class="retweets">🔁 ${a.retweets}</span>` : ''}
        </div>
      </div>
    `}).join('');

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
