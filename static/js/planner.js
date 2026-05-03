/* ── planner.js — Study planner module ─────────────────────────── */

// ── Generate plan ──────────────────────────────────────────────
async function generatePlan() {
  const subjects = document.getElementById('planner-subjects').value.trim();
  if (!subjects) { showToast('Please enter at least one subject', 'error'); return; }

  const btn = document.getElementById('planner-btn');
  btn.disabled = true;
  btn.textContent = '✨ Generating your plan…';
  document.getElementById('planner-placeholder').style.display = 'none';
  document.getElementById('planner-output').style.display = 'none';
  document.getElementById('planner-output').innerHTML = '<div class="skeleton" style="height:200px;"></div>';
  document.getElementById('planner-output').style.display = 'block';

  try {
    const res = await fetch('/api/schedule/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        subjects,
        deadlines: document.getElementById('planner-deadlines').value.trim(),
        available_hours: document.getElementById('planner-hours').value,
        break_style: document.getElementById('planner-breaks').value,
        energy_level: document.getElementById('planner-energy').value,
        learning_style: document.getElementById('planner-style').value
      })
    });
    const data = await res.json();
    if (res.ok) {
      renderPlan(data.schedule);
      showToast('Study plan generated! 🎉', 'success');
    } else {
      showToast(data.error || 'Failed to generate plan', 'error');
      document.getElementById('planner-placeholder').style.display = 'flex';
      document.getElementById('planner-output').style.display = 'none';
    }
  } catch {
    showToast('Connection error', 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = '✨ Generate My Plan';
  }
}

// ── Load latest saved plan ─────────────────────────────────────
async function loadLatestPlan() {
  try {
    const res = await fetch('/api/schedule/latest');
    const data = await res.json();
    if (data.schedule) {
      renderPlan(data.schedule.schedule_json);
    }
  } catch { /* silent */ }
}

// ── Render plan ────────────────────────────────────────────────
function renderPlan(plan) {
  const output = document.getElementById('planner-output');
  document.getElementById('planner-placeholder').style.display = 'none';

  let html = `
    <div style="margin-bottom: 20px; display: flex; align-items: center; gap: 8px;">
      <span style="background: var(--primary-light); color: var(--bg); font-size: 10px; font-weight: 800; padding: 4px 8px; border-radius: 20px; text-transform: uppercase;">✨ Mood Optimized</span>
      <span style="font-size: 11px; color: var(--text-muted);">AI adjusted this plan for your current energy.</span>
    </div>
    <div class="plan-overview">💡 ${plan.overview || ''}</div>
    <div class="timeline">`;

  (plan.days || []).forEach((day, i) => {
    const isToday = i === new Date().getDay() - 1;
    html += `
      <div class="timeline-item" id="plan-day-${i}">
        <div class="timeline-marker"></div>
        <div class="timeline-content">
          <div class="timeline-header">
            <span>${isToday ? '📍 ' : ''}${day.day}</span>
          </div>
          <div class="timeline-date">${day.date}</div>
          ${day.tip ? `<div class="timeline-tip">✨ ${day.tip}</div>` : ''}
          <div class="plan-sessions" id="plan-sessions-${i}">`;

    (day.sessions || []).forEach(session => {
      // Create a button to start focus mode if it's a study session
      const focusBtn = session.type === 'study' ? `<button class="btn-icon" style="width:32px;height:32px;font-size:14px;border-color:var(--primary)" onclick="navigate('focus')" title="Start Focus Timer">⏱️</button>` : '';
      
      html += `
        <div class="plan-session ${session.type || 'study'}">
          <div class="session-time">${session.time}</div>
          <div class="session-info">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              <div class="session-subject">${session.subject}</div>
              ${focusBtn}
            </div>
            <div class="session-task">${session.task}</div>
          </div>
        </div>`;
    });

    html += `</div></div></div>`;
  });

  html += '</div>';
  output.innerHTML = html;
  output.style.display = 'block';
}

function toggleDay(i) {
  const sessions = document.getElementById(`plan-sessions-${i}`);
  if (sessions) {
    sessions.style.display = sessions.style.display === 'none' ? 'flex' : 'none';
  }
}
