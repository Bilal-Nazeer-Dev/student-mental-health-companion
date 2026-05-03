/* ── mood.js — Mood tracker module ─────────────────────────────── */

let selectedScore = null;

const TREND_ICONS = { improving: '📈', declining: '📉', stable: '➡️', no_data: '🔍', insufficient_data: '🔍' };
const MOOD_LABELS = { 1: 'Very Bad', 2: 'Bad', 3: 'Okay', 4: 'Good', 5: 'Excellent' };

// ── Select mood score ──────────────────────────────────────────
async function selectMood(btn, score) {
  selectedScore = score;
  document.querySelectorAll('.emoji-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  document.getElementById('mood-step-2').style.display = 'block';
  
  // Theme update
  const emotions = { 1: 'frustrated', 2: 'sad', 3: 'anxious', 4: 'happy', 5: 'happy' };
  if (typeof updateTheme !== 'undefined') updateTheme(emotions[score]);

  const questionEl = document.getElementById('mood-question');
  questionEl.innerHTML = '<span style="opacity: 0.7;">Feelora is typing...</span>';
  
  try {
    const res = await fetch('/api/mood/question', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ score })
    });
    const data = await res.json();
    questionEl.textContent = "✨ " + data.question;
  } catch {
    questionEl.textContent = "✨ Would you like to share more about how you're feeling?";
  }
}

let selectedTags = new Set();

function toggleTag(btn, tag) {
  if (selectedTags.has(tag)) {
    selectedTags.delete(tag);
    btn.classList.remove('selected');
  } else {
    selectedTags.add(tag);
    btn.classList.add('selected');
  }
}

async function saveMood() {
  if (!selectedScore) {
    showToast('Please select how you feel first!', 'error');
    return;
  }
  const description = document.getElementById('mood-desc').value.trim();
  const triggers = Array.from(selectedTags).join(', ');
  
  if (typeof checkCrisis !== 'undefined' && checkCrisis(description)) return;
  
  try {
    const res = await fetch('/api/mood/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ score: selectedScore, description, triggers })
    });
    const data = await res.json();
    if (res.ok) {
      document.getElementById('btn-save-mood').style.display = 'none';
      document.getElementById('btn-reflect-mood').style.display = 'block';
      showToast(`Mood logged! Want some advice?`, 'success');
      loadMoodStats();
      if (typeof addWellbeingPoints !== 'undefined') addWellbeingPoints(10, 'Checked in with yourself');
    } else {
      showToast(data.error || 'Failed to log mood', 'error');
    }
  } catch {
    showToast('Connection error', 'error');
  }
}

async function getReflection() {
  document.getElementById('reflection-modal').classList.remove('hidden');
  document.getElementById('reflection-text').textContent = 'Feelora is thinking...';
  
  const description = document.getElementById('mood-desc').value.trim();
  const triggers = Array.from(selectedTags).join(', ');
  
  try {
    const res = await fetch('/api/mood/reflect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ score: selectedScore, description, triggers })
    });
    const data = await res.json();
    document.getElementById('reflection-text').textContent = data.reflection || 'Could not connect.';
  } catch {
    document.getElementById('reflection-text').textContent = 'Could not get reflection right now. 💙';
  }
}

function closeReflection() {
  document.getElementById('reflection-modal').classList.add('hidden');
  
  // reset form
  document.getElementById('mood-desc').value = '';
  selectedScore = null;
  selectedTags.clear();
  document.querySelectorAll('.emoji-btn, .mood-tag').forEach(b => b.classList.remove('selected'));
  document.getElementById('btn-save-mood').style.display = 'block';
  document.getElementById('btn-reflect-mood').style.display = 'none';
  document.getElementById('mood-step-2').style.display = 'none';
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
