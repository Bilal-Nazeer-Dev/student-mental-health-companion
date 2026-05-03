/* ── app.js — SPA Router & Global Utilities ─────────────────── */

// ── Auth guard ──────────────────────────────────────────────────
(async function authGuard() {
  try {
    const res = await fetch('/api/auth/me');
    if (!res.ok) { window.location.href = '/'; return; }
    const data = await res.json();
    const user = data.user;
    localStorage.setItem('sage_user', JSON.stringify(user));
    document.getElementById('user-name').textContent = user.username;
    document.getElementById('user-avatar').textContent = user.username[0].toUpperCase();
  } catch {
    window.location.href = '/';
  }
})();

// ── SPA Navigation ──────────────────────────────────────────────
const PANELS = ['chat', 'mood', 'planner', 'relax', 'dashboard'];

function navigate(page) {
  if (!PANELS.includes(page)) page = 'chat';

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
  localStorage.removeItem('sage_user');
  window.location.href = '/';
}

// ── Init routing from hash ──────────────────────────────────────
window.addEventListener('load', () => {
  const hash = window.location.hash.replace('#', '') || 'chat';
  navigate(hash);
});
