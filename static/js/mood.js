/* ── mood.js — Mood tracker module ─────────────────────────────── */

let selectedScore = null;

const TREND_ICONS = { improving: '📈', declining: '📉', stable: '➡️', no_data: '🔍', insufficient_data: '🔍' };
const MOOD_LABELS = { 1: 'Very Bad', 2: 'Bad', 3: 'Okay', 4: 'Good', 5: 'Excellent' };

// ── Select mood score ──────────────────────────────────────────
function selectMood(score) {
  selectedScore = score;
  document.querySelectorAll('.emoji-btn').forEach(btn => {
    btn.classList.toggle('selected', parseInt(btn.dataset.score) === score);
  });
}

// ── Log mood ───────────────────────────────────────────────────
async function logMood() {
  if (!selectedScore) {
    showToast('Please select how you feel first!', 'error');
    return;
  }
  const description = document.getElementById('mood-description').value.trim();
  try {
    const res = await fetch('/api/mood/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ score: selectedScore, description })
    });
    const data = await res.json();
    if (res.ok) {
      const msg = document.getElementById('mood-log-msg');
      msg.textContent = `✅ Logged: ${data.emoji} ${data.label} — ${data.emotion_tag !== 'neutral' ? `Feeling ${data.emotion_tag}` : 'Noted!'}`;
      msg.classList.add('show');
      document.getElementById('mood-description').value = '';
      selectedScore = null;
      document.querySelectorAll('.emoji-btn').forEach(b => b.classList.remove('selected'));
      setTimeout(() => msg.classList.remove('show'), 4000);
      loadMoodStats();
      showToast(`Mood logged: ${data.emoji} ${data.label}`, 'success');
    } else {
      showToast(data.error || 'Failed to log mood', 'error');
    }
  } catch {
    showToast('Connection error', 'error');
  }
}

// ── Load mood stats ────────────────────────────────────────────
async function loadMoodStats() {
  try {
    const res = await fetch('/api/mood/logs?days=30');
    if (!res.ok) return;
    const data = await res.json();
    const analysis = data.analysis;

    // Update stats
    document.getElementById('mood-avg').textContent = analysis.average > 0 ? analysis.average.toFixed(1) : '–';
    document.getElementById('mood-trend-icon').textContent = TREND_ICONS[analysis.trend] || '–';
    document.getElementById('mood-entries').textContent = analysis.total_entries || '0';

    // Insights
    const insightsEl = document.getElementById('mood-insights');
    insightsEl.innerHTML = analysis.insights.map(i =>
      `<div class="insight-item">${i}</div>`
    ).join('');

    // Alert if streak is bad
    if (analysis.streak_alert) triggerEmergency();
  } catch { /* silent */ }
}
