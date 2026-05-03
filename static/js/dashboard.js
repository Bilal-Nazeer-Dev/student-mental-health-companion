/* ── dashboard.js — Dashboard & Chart module ───────────────────── */

let moodChartInst = null;
let emotionChartInst = null;

const TREND_MAP = { improving: '📈 Improving', declining: '📉 Declining', stable: '➡️ Stable', no_data: '🔍 No Data', insufficient_data: '🔍 More Data Needed' };
const EMOTION_COLORS = {
  happy: '#10B981', neutral: '#94A3B8', anxious: '#F59E0B',
  stressed: '#EF4444', sad: '#06B6D4', frustrated: '#F97316', tired: '#A78BFA'
};

async function loadDashboard() {
  try {
    const res = await fetch('/api/dashboard/stats');
    if (!res.ok) return;
    const d = await res.json();

    // Stat cards
    document.getElementById('dash-avg').textContent = d.mood_average > 0 ? d.mood_average.toFixed(1) + '/5' : '–';
    document.getElementById('dash-streak').textContent = d.checkin_streak || '0';
    document.getElementById('dash-total').textContent = d.total_mood_logs || '0';
    document.getElementById('dash-trend').textContent = TREND_MAP[d.mood_trend] || '–';

    // Weekly insight
    document.getElementById('weekly-insight').textContent = d.weekly_insight || 'Log your mood daily to unlock insights!';

    // Insights list
    const insightsList = document.getElementById('dash-insights');
    insightsList.innerHTML = (d.insights || []).map(i =>
      `<div class="insight-item">${i}</div>`
    ).join('') || '<div class="insight-item">Start logging your mood to see recommendations here!</div>';

    // Mood trend chart
    renderMoodChart(d.chart_data);

    // Emotion distribution chart
    renderEmotionChart(d.emotion_distribution);
    
    // Load AI Weekly Report
    loadWeeklyReport();

  } catch (e) {
    showToast('Could not load dashboard data', 'error');
  }
}

async function loadWeeklyReport() {
  const insightEl = document.getElementById('weekly-insight');
  if (!insightEl) return;
  
  try {
    const res = await fetch('/api/mood/report');
    if (!res.ok) return;
    const data = await res.json();
    
    // Convert markdown-ish text to simple HTML
    let text = data.report.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\n/g, '<br>');
    insightEl.innerHTML = text;
  } catch (e) {
    insightEl.textContent = 'Keep logging your mood to unlock your AI Weekly Insight! 💙';
  }
}

function renderMoodChart(chartData) {
  const canvas = document.getElementById('mood-chart');
  if (!canvas) return;
  if (moodChartInst) moodChartInst.destroy();

  const { labels = [], data = [] } = chartData || {};

  moodChartInst = new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Mood Score',
        data,
        borderColor: '#7C3AED',
        backgroundColor: 'rgba(124,58,237,0.1)',
        borderWidth: 2.5,
        pointBackgroundColor: '#9F67FF',
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.4,
        fill: true,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { min: 1, max: 5, ticks: { stepSize: 1, color: '#94A3B8' }, grid: { color: 'rgba(255,255,255,0.05)' }, border: { color: 'transparent' } },
        x: { ticks: { color: '#94A3B8', maxRotation: 45 }, grid: { display: false }, border: { color: 'transparent' } }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1A1A2E', borderColor: 'rgba(124,58,237,0.4)', borderWidth: 1,
          titleColor: '#F1F5F9', bodyColor: '#94A3B8', padding: 12, cornerRadius: 10,
          callbacks: {
            label: ctx => {
              const labels = ['', 'Very Bad 😞', 'Bad 😕', 'Okay 😐', 'Good 😊', 'Excellent 😄'];
              return ` ${labels[ctx.parsed.y] || ctx.parsed.y}`;
            }
          }
        }
      }
    }
  });
}

function renderEmotionChart(dist) {
  const canvas = document.getElementById('emotion-chart');
  if (!canvas) return;
  if (emotionChartInst) emotionChartInst.destroy();

  const entries = Object.entries(dist || {});
  if (!entries.length) {
    entries.push(['No data yet', 1]);
  }

  const labels = entries.map(([k]) => k.charAt(0).toUpperCase() + k.slice(1));
  const data = entries.map(([, v]) => v);
  const colors = entries.map(([k]) => EMOTION_COLORS[k] || '#7C3AED');

  emotionChartInst = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors, borderColor: '#0F0F1A', borderWidth: 3, hoverBorderWidth: 0 }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: { position: 'right', labels: { color: '#94A3B8', padding: 12, font: { size: 12 } } },
        tooltip: {
          backgroundColor: '#1A1A2E', borderColor: 'rgba(124,58,237,0.4)', borderWidth: 1,
          titleColor: '#F1F5F9', bodyColor: '#94A3B8', padding: 12, cornerRadius: 10
        }
      }
    }
  });
}
