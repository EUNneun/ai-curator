// Category filter & search state
let activeCategory = 'all';
let searchQuery = '';

function filterByCategory(btn, category) {
  activeCategory = category;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters();
}

function handleSearch(query) {
  searchQuery = query.toLowerCase().trim();
  applyFilters();
}

function applyFilters() {
  const cards = document.querySelectorAll('.video-card');
  let visible = 0;

  cards.forEach(card => {
    const catMatch = activeCategory === 'all' || card.dataset.category === activeCategory;

    let searchMatch = true;
    if (searchQuery) {
      const item = SEARCH_INDEX.find(s => s.id === card.dataset.id);
      if (item) {
        const haystack = `${item.title} ${item.summary} ${item.channel} ${item.category}`.toLowerCase();
        searchMatch = haystack.includes(searchQuery);
      } else {
        searchMatch = false;
      }
    }

    const show = catMatch && searchMatch;
    card.style.display = show ? '' : 'none';
    if (show) visible++;
  });

  const noResults = document.getElementById('no-results');
  if (noResults) noResults.classList.toggle('hidden', visible > 0);
}

async function sendFeedback(videoId, rating) {
  const card = document.querySelector(`[data-id="${videoId}"]`);
  if (!card) return;

  const btn = card.querySelector(`.btn-${rating.toLowerCase()}`);
  if (btn) { btn.disabled = true; }

  const payload = {
    video_id: videoId,
    rating: rating,
    timestamp: new Date().toISOString(),
    processed: false,
  };

  const endpoint = typeof FEEDBACK_ENDPOINT !== 'undefined' ? FEEDBACK_ENDPOINT : '';

  if (!endpoint) {
    // Formspree 미설정 시 localStorage에 임시 저장
    try {
      const stored = JSON.parse(localStorage.getItem('pending_feedback') || '[]');
      stored.push(payload);
      localStorage.setItem('pending_feedback', JSON.stringify(stored));
    } catch (_) {}
    showToast(rating === 'GOOD' ? '👍 감사합니다!' : '👎 피드백 감사합니다!');
    return;
  }

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      showToast(rating === 'GOOD' ? '👍 감사합니다!' : '👎 피드백 감사합니다!');
    } else {
      throw new Error(`HTTP ${res.status}`);
    }
  } catch (e) {
    console.error('Feedback error:', e);
    if (btn) btn.disabled = false;
    showToast('전송 실패, 다시 시도해 주세요.');
  }
}

function showToast(msg) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = msg;
  document.body.appendChild(toast);

  requestAnimationFrame(() => {
    requestAnimationFrame(() => toast.classList.add('show'));
  });
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 2200);
}
