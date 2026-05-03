/* ── focus.js — Live Pomodoro Focus Timer ─────────────────────────────── */

let focusTimer = null;
let focusTimeLeft = 25 * 60; // 25 minutes default
let isFocusing = false;
let focusMode = 'study'; // 'study' or 'break'
const FOCUS_TIME = 25 * 60;
const BREAK_TIME = 5 * 60;
let sessionsCompleted = 0;

function updateFocusDisplay() {
  const m = Math.floor(focusTimeLeft / 60).toString().padStart(2, '0');
  const s = (focusTimeLeft % 60).toString().padStart(2, '0');
  document.getElementById('focus-time').textContent = `${m}:${s}`;
  
  // Update SVG ring
  const ring = document.getElementById('focus-progress');
  const total = focusMode === 'study' ? FOCUS_TIME : BREAK_TIME;
  const offset = 880 - (focusTimeLeft / total) * 880;
  ring.style.strokeDashoffset = offset;
}

function toggleFocus() {
  const btn = document.getElementById('btn-focus-toggle');
  
  if (isFocusing) {
    clearInterval(focusTimer);
    isFocusing = false;
    btn.textContent = 'Resume';
    btn.style.background = 'var(--primary)';
    btn.style.borderColor = 'var(--primary)';
  } else {
    isFocusing = true;
    btn.textContent = 'Pause';
    btn.style.background = 'var(--danger)';
    btn.style.borderColor = 'var(--danger)';
    
    focusTimer = setInterval(() => {
      focusTimeLeft--;
      updateFocusDisplay();
      
      if (focusTimeLeft <= 0) {
        clearInterval(focusTimer);
        handleTimerComplete();
      }
    }, 1000);
  }
}

function handleTimerComplete() {
  playChime();
  isFocusing = false;
  
  const btn = document.getElementById('btn-focus-toggle');
  btn.textContent = 'Start';
  btn.style.background = 'var(--primary)';
  btn.style.borderColor = 'var(--primary)';
  
  if (focusMode === 'study') {
    sessionsCompleted++;
    document.getElementById('focus-sessions-count').textContent = sessionsCompleted;
    showToast('Focus session complete! Time for a break.', 'success');
    if (typeof addWellbeingPoints !== 'undefined') addWellbeingPoints(25, 'Completed Focus Session!');
    focusMode = 'break';
    focusTimeLeft = BREAK_TIME;
    document.getElementById('focus-mode-label').textContent = 'Short Break';
    document.getElementById('focus-progress').classList.add('break');
  } else {
    showToast('Break is over! Ready to focus?', 'success');
    focusMode = 'study';
    focusTimeLeft = FOCUS_TIME;
    document.getElementById('focus-mode-label').textContent = 'Focus Session';
    document.getElementById('focus-progress').classList.remove('break');
  }
  updateFocusDisplay();
}

function resetFocus() {
  clearInterval(focusTimer);
  isFocusing = false;
  focusMode = 'study';
  focusTimeLeft = FOCUS_TIME;
  
  const btn = document.getElementById('btn-focus-toggle');
  btn.textContent = 'Start Focus';
  btn.style.background = 'var(--primary)';
  btn.style.borderColor = 'var(--primary)';
  
  document.getElementById('focus-mode-label').textContent = 'Focus Session';
  document.getElementById('focus-progress').classList.remove('break');
  updateFocusDisplay();
}

function playChime() {
  // A simple gentle beep using Web Audio API
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    osc.type = 'sine';
    osc.frequency.setValueAtTime(440, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.1);
    
    gain.gain.setValueAtTime(0, ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.3, ctx.currentTime + 0.1);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 1.5);
    
    osc.start();
    osc.stop(ctx.currentTime + 1.5);
  } catch (e) { console.error('Audio failed', e); }
}

// Init display
window.addEventListener('load', () => {
  if (document.getElementById('focus-time')) {
    updateFocusDisplay();
  }
});
