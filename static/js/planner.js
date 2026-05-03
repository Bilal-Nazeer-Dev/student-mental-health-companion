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
        break_style: document.getElementById('planner-breaks').value
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

  let html = `<div class="plan-overview">💡 ${plan.overview || ''}</div><div class="plan-days">`;

  (plan.days || []).forEach((day, i) => {
    const isToday = i === new Date().getDay() - 1;
    html += `
      <div class="plan-day" id="plan-day-${i}">
        <div class="plan-day-header" onclick="toggleDay(${i})">
          <span>${isToday ? '📍 ' : ''}${day.day} <span style="color:var(--text-dim);font-weight:400;font-size:12px;">(${day.date})</span></span>
          <span class="day-tip">${day.tip || ''}</span>
        </div>
        <div class="plan-sessions" id="plan-sessions-${i}" style="${i === 0 ? '' : 'display:none'}">`;

    (day.sessions || []).forEach(session => {
      html += `
        <div class="plan-session ${session.type || 'study'}">
          <div class="session-time">${session.time}</div>
          <div class="session-info">
            <div class="session-subject">${session.subject}</div>
            <div class="session-task">${session.task}</div>
          </div>
        </div>`;
    });

    html += `</div></div>`;
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
