/**
 * IanNews — 前端增强脚本
 * 当 HTML 中已预渲染新闻内容时，JS 仅负责更新时间戳等动态功能。
 * 当通过 fetch 加载 data/news.json 时（fallback），会执行完整渲染。
 */

(function () {
  'use strict';

  const listEl = document.getElementById('newsList');
  const updateEl = document.getElementById('lastUpdate');

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatTime(iso) {
    if (!iso) return '';
    try {
      var d = new Date(
        iso
          .replace(' +0000', 'Z')
          .replace(' GMT', '')
          .replace(/(\+\d{2})(\d{2})$/, '$1:$2')
      );
      return d.toLocaleString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'Asia/Shanghai',
      });
    } catch (_) {
      return iso;
    }
  }

  function init() {
    var data = window.__NEWS_DATA__;

    if (!data || !data.articles) {
      // 无内嵌数据时回退 fetch（兼容性兜底）
      fetch('/data/news.json')
        .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
        .then(function (d) { updateUI(d); })
        .catch(function () {
          if (listEl) listEl.innerHTML =
            '<div class="error">加载失败，请刷新重试</div>';
        });
      return;
    }

    updateUI(data);
  }

  function updateUI(data) {
    // 更新时间
    if (updateEl && data.fetchedAt) {
      try {
        var d = new Date(data.fetchedAt.replace('Z', '+00:00'));
        updateEl.innerHTML =
          '<time datetime="' + data.fetchedAt + '">🕐 更新于 ' +
          d.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' }) +
          '</time>';
      } catch (_) {}
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
