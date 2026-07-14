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

    list.innerHTML = data.articles.map((a, i) => `
      <div class="card" data-idx="${i}">
        <div class="card-source">
          <a href="${escapeHtml(a.url)}" target="_blank" rel="noopener">${escapeHtml(a.author)}</a>
        </div>
        <div class="card-text" data-original="${escapeHtml(a.text)}">${escapeHtml(a.text)}</div>
        ${isChinese(a.author) ? '' : '<button class="translate-btn" onclick="translateCard(this)">🌐 中</button>'}
        <div class="card-meta">
          <span>${formatTime(a.createdAt)}</span>
          ${a.likes != null ? `<span class="likes">❤ ${a.likes}</span>` : ''}
          ${a.retweets != null ? `<span class="retweets">🔁 ${a.retweets}</span>` : ''}
        </div>
      </div>
    `).join('');

  } catch (err) {
    list.innerHTML = `<div class="error">加载失败: ${escapeHtml(err.message)}</div>`;
  }
}

async function translateCard(btn) {
  const card = btn.closest('.card');
  const textEl = card.querySelector('.card-text');
  const original = textEl.dataset.original || textEl.textContent;

  btn.disabled = true;
  btn.textContent = '🔄 翻译中...';

  try {
    const res = await fetch('/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: original }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || `HTTP ${res.status}`);
    }

    const data = await res.json();
    if (data.translated) {
      textEl.innerHTML = escapeHtml(data.translated) + '<br><span class="translated-tip">⬆ 机器翻译</span>';
      btn.textContent = '🔙 原文';
      btn.onclick = function() {
        textEl.innerHTML = escapeHtml(original);
        btn.textContent = '🌐 中';
        btn.onclick = function() { translateCard(this); };
        btn.disabled = false;
      };
    }
  } catch (err) {
    btn.textContent = '❌ 翻译失败';
    setTimeout(() => { btn.textContent = '🌐 中'; btn.disabled = false; }, 2000);
  }
  btn.disabled = false;
}

function isChinese(author) {
  return /[\u4e00-\u9fff]/.test(author);
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
