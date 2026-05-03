/* ── app.js — SPA Router & Global Utilities ─────────────────── */

// ── Auth guard ──────────────────────────────────────────────────
(async function authGuard() {
  try {
    const res = await fetch('/api/auth/me');
    if (!res.ok) { window.location.href = '/'; return; }
    const data = await res.json();
    const user = data.user;
    localStorage.setItem('feelora_user', JSON.stringify(user));
    document.getElementById('user-name').textContent = user.username;
    document.getElementById('user-avatar').textContent = user.username[0].toUpperCase();
  } catch {
    window.location.href = '/';
  }
})();

// ── SPA Navigation ──────────────────────────────────────────────
const PANELS = ['chat', 'mood', 'planner', 'relax', 'focus', 'dashboard'];

function navigate(page) {
  if (!PANELS.includes(page)) page = 'chat';

  // The "Focus Guardian" Check
  if (typeof isFocusing !== 'undefined' && isFocusing && page !== 'focus') {
    const confirmLeave = confirm("Focus Guardian: You are currently in a Focus Session. Are you sure you want to break your concentration and leave this room?");
    if (!confirmLeave) return; // Intercept navigation
  }

  PANELS.forEach(p => {
    document.getElementById(`panel-${p}`)?.classList.toggle('active', p === page);
    document.getElementById(`nav-${p}`)?.classList.toggle('active', p === page);
  });

  // Close mobile sidebar
  document.getElementById('sidebar')?.classList.remove('open');

  // Lazy load page data
  if (page === 'mood') loadMoodStats();
  if (page === 'dashboard') loadDashboard();
  if (page === 'planner') loadLatestPlan();

  // Update URL hash
  history.replaceState(null, '', `#${page}`);
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// ── Toast notifications ─────────────────────────────────────────
function showToast(msg, type = 'info', duration = 3500) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'toastOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ── Logout ──────────────────────────────────────────────────────
async function handleLogout() {
  await fetch('/api/auth/logout', { method: 'POST' });
  localStorage.removeItem('feelora_user');
  window.location.href = '/';
}

// ── Ambient Soundscapes ──────────────────────────────────────────

const ambientAudio = document.getElementById('ambient-audio');
const btnAmbientPlay = document.getElementById('btn-ambient-play');
const selectAmbient = document.getElementById('ambient-track');
const volAmbient = document.getElementById('ambient-volume');

function changeAmbientTrack() {
  const url = selectAmbient.value;
  if (!url) {
    ambientAudio.pause();
    btnAmbientPlay.textContent = '▶️';
    return;
  }
  ambientAudio.src = url;
  ambientAudio.volume = volAmbient.value;
  ambientAudio.play().then(() => {
    btnAmbientPlay.textContent = '⏸️';
  }).catch(e => {
    console.error("Audio play failed:", e);
    btnAmbientPlay.textContent = '▶️';
  });
}

function toggleAmbientPlay() {
  if (!selectAmbient.value) return;
  if (ambientAudio.paused) {
    ambientAudio.play();
    btnAmbientPlay.textContent = '⏸️';
  } else {
    ambientAudio.pause();
    btnAmbientPlay.textContent = '▶️';
  }
}

function changeAmbientVolume() {
  if (ambientAudio) {
    ambientAudio.volume = volAmbient.value;
  }
}

// ── Init routing from hash ──────────────────────────────────────
window.addEventListener('load', () => {
  const hash = window.location.hash.replace('#', '') || 'chat';
  navigate(hash);
  updateWellbeingUI();
});

// ── Wellbeing Score Gamification ─────────────────────────────────
let wellbeingScore = parseInt(localStorage.getItem('feelora_wellbeing') || '0');
let wellbeingLevel = Math.floor(wellbeingScore / 100) + 1;
let wellbeingCurrent = wellbeingScore % 100;

function updateWellbeingUI() {
  const scoreEl = document.getElementById('wellbeing-score');
  const fillEl = document.getElementById('wellbeing-fill');
  const levelEl = document.getElementById('wellbeing-level-badge');
  
  if (scoreEl && fillEl && levelEl) {
    scoreEl.textContent = wellbeingCurrent;
    fillEl.style.width = `${wellbeingCurrent}%`;
    levelEl.textContent = `Lvl ${wellbeingLevel}`;
  }
}

function addWellbeingPoints(points, reason) {
  wellbeingScore += points;
  localStorage.setItem('feelora_wellbeing', wellbeingScore);
  
  const oldLevel = wellbeingLevel;
  wellbeingLevel = Math.floor(wellbeingScore / 100) + 1;
  wellbeingCurrent = wellbeingScore % 100;
  
  updateWellbeingUI();
  
  showToast(`+${points} pts: ${reason}`, 'success');
  
  if (wellbeingLevel > oldLevel) {
    setTimeout(() => {
      showToast(`🎉 Level Up! You are now Level ${wellbeingLevel}!`, 'success', 5000);
      // Confetti effect
      const container = document.querySelector('.wellbeing-bar-container');
      if (container) {
        container.style.animation = 'pulse 1s ease';
        setTimeout(() => container.style.animation = '', 1000);
      }
    }, 1000);
  }
}

// ── Theme Switching ──────────────────────────────────────────────
function updateTheme(emotion) {
  if (!emotion) return;
  document.body.classList.remove('theme-happy', 'theme-sad', 'theme-anxious', 'theme-frustrated', 'theme-tired');
  document.body.classList.add(`theme-${emotion}`);
}

// ── Crisis Detection ──────────────────────────────────────────────
const CRISIS_KEYWORDS = ['suicide', 'kill myself', 'give up', 'hopeless', 'end it all', 'hurt myself', 'don\'t want to live', 'die'];

function checkCrisis(text) {
  if (!text) return false;
  const lowText = text.toLowerCase();
  const hasCrisis = CRISIS_KEYWORDS.some(kw => lowText.includes(kw));
  if (hasCrisis) {
    showEmergencyModal();
    return true;
  }
  return false;
}

function showEmergencyModal() {
  document.getElementById('emergency-overlay')?.classList.remove('hidden');
}

function closeEmergency() {
  document.getElementById('emergency-overlay')?.classList.add('hidden');
}
