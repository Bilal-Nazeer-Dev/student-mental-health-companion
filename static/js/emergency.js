/* ── emergency.js — Emergency detection & overlay ──────────────── */

let emergencyShown = false;

function triggerEmergency() {
  if (emergencyShown) return;
  emergencyShown = true;
  document.getElementById('emergency-overlay').classList.remove('hidden');
}

function closeEmergency() {
  document.getElementById('emergency-overlay').classList.add('hidden');
  // Allow re-triggering after 10 minutes
  setTimeout(() => { emergencyShown = false; }, 10 * 60 * 1000);
}
