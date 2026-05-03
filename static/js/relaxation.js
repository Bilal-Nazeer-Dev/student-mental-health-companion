/* ── relaxation.js — Guided exercises module ───────────────────── */

let exerciseTimer = null;

function startExercise(type) {
  document.getElementById('exercise-modal').classList.remove('hidden');
  const content = document.getElementById('exercise-content');
  if (type === 'breathing') startBreathing(content);
  else if (type === 'grounding') startGrounding(content);
  else if (type === 'pmr') startPMR(content);
  else if (type === 'meditation') startMeditation(content);
}

function closeExercise() {
  clearInterval(exerciseTimer);
  clearTimeout(exerciseTimer);
  document.getElementById('exercise-modal').classList.add('hidden');
  document.getElementById('exercise-content').innerHTML = '';
}

let breathAudioCtx = null;
let breathOsc = null;
let breathGain = null;
let isBreathingActive = false;

function playBreathTone(type, duration) {
  try {
    if (!breathAudioCtx) {
      breathAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (breathAudioCtx.state === 'suspended') breathAudioCtx.resume();
    
    const ctx = breathAudioCtx;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    osc.type = 'sine';
    
    const now = ctx.currentTime;
    if (type === 'inhale') {
      osc.frequency.setValueAtTime(220, now);
      osc.frequency.linearRampToValueAtTime(440, now + duration);
      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(0.15, now + duration);
    } else if (type === 'exhale') {
      osc.frequency.setValueAtTime(440, now);
      osc.frequency.linearRampToValueAtTime(220, now + duration);
      gain.gain.setValueAtTime(0.15, now);
      gain.gain.linearRampToValueAtTime(0, now + duration);
    } else {
      // hold
      const freq = type === 'hold1' ? 440 : 220;
      const vol = type === 'hold1' ? 0.15 : 0;
      osc.frequency.setValueAtTime(freq, now);
      gain.gain.setValueAtTime(vol, now);
    }
    
    osc.start(now);
    osc.stop(now + duration);
    
  } catch(e) { console.error('Audio play failed', e); }
}

function startBreathing(el) {
  isBreathingActive = true;
  el.innerHTML = `
    <div class="exercise-title">🫁 Interactive Breathing</div>
    
    <div style="display:flex; justify-content:center; gap: 10px; margin-bottom: 20px; flex-wrap:wrap;">
      <div style="background:var(--surface-3); padding:8px; border-radius:8px; text-align:center;">
        <label style="font-size:10px; color:var(--text-dim); display:block;">Inhale (s)</label>
        <input type="range" id="dur-inhale" min="2" max="8" value="4" oninput="document.getElementById('val-inhale').textContent=this.value" style="width:60px;">
        <span id="val-inhale" style="font-size:12px;font-weight:bold;">4</span>
      </div>
      <div style="background:var(--surface-3); padding:8px; border-radius:8px; text-align:center;">
        <label style="font-size:10px; color:var(--text-dim); display:block;">Hold (s)</label>
        <input type="range" id="dur-hold" min="0" max="6" value="4" oninput="document.getElementById('val-hold').textContent=this.value" style="width:60px;">
        <span id="val-hold" style="font-size:12px;font-weight:bold;">4</span>
      </div>
      <div style="background:var(--surface-3); padding:8px; border-radius:8px; text-align:center;">
        <label style="font-size:10px; color:var(--text-dim); display:block;">Exhale (s)</label>
        <input type="range" id="dur-exhale" min="2" max="10" value="4" oninput="document.getElementById('val-exhale').textContent=this.value" style="width:60px;">
        <span id="val-exhale" style="font-size:12px;font-weight:bold;">4</span>
      </div>
    </div>

    <div class="breathing-circle" id="breath-circle" style="transition: transform linear;">Ready</div>
    <div class="exercise-step" id="breath-step">Adjust sliders and click begin.</div>
    
    <div style="display:flex;justify-content:center;margin-top:20px;gap:10px;">
      <button class="btn-primary" id="btn-breath-start" onclick="runBreathingCycle(this)">Begin</button>
      <button class="btn-primary" style="background:var(--surface-3);color:var(--text);" onclick="stopBreathing()">Stop</button>
    </div>
  `;

  window.runBreathingCycle = async (btn) => {
    btn.disabled = true;
    btn.textContent = "Breathing...";
    if (!breathAudioCtx) breathAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    
    const inhaleD = parseInt(document.getElementById('dur-inhale').value);
    const holdD = parseInt(document.getElementById('dur-hold').value);
    const exhaleD = parseInt(document.getElementById('dur-exhale').value);
    
    const circle = document.getElementById('breath-circle');
    const step = document.getElementById('breath-step');
    
    const runPhase = (name, dur, type, scale) => {
      return new Promise(resolve => {
        if (!isBreathingActive) return resolve();
        circle.textContent = name;
        step.textContent = `Breathe phase...`;
        circle.style.transitionDuration = `${dur}s`;
        circle.style.transform = `scale(${scale})`;
        
        playBreathTone(type, dur);
        
        let timeLeft = dur;
        step.textContent = timeLeft;
        clearInterval(exerciseTimer);
        exerciseTimer = setInterval(() => {
          timeLeft--;
          if (timeLeft > 0) step.textContent = timeLeft;
        }, 1000);
        
        setTimeout(() => {
          clearInterval(exerciseTimer);
          resolve();
        }, dur * 1000);
      });
    };

    while (isBreathingActive) {
      await runPhase('Inhale', inhaleD, 'inhale', 1.5);
      if (holdD > 0 && isBreathingActive) await runPhase('Hold', holdD, 'hold1', 1.5);
      if (isBreathingActive) await runPhase('Exhale', exhaleD, 'exhale', 1.0);
      if (holdD > 0 && isBreathingActive) await runPhase('Hold', holdD, 'hold2', 1.0);
    }
  };
  
  window.stopBreathing = () => {
    isBreathingActive = false;
    clearInterval(exerciseTimer);
    if (typeof addWellbeingPoints !== 'undefined') addWellbeingPoints(5, 'Completed Breathing Exercise');
    closeExercise();
  };
}

// ── 2. 5-4-3-2-1 Grounding ─────────────────────────────────────
function startGrounding(el) {
  const steps = [
    { sense: '👁️', count: 5, type: 'see', action: 'Name 5 things you can SEE around you right now.' },
    { sense: '✋', count: 4, type: 'touch', action: 'Name 4 things you can TOUCH or feel right now.' },
    { sense: '👂', count: 3, type: 'hear', action: 'Name 3 things you can HEAR in your environment.' },
    { sense: '👃', count: 2, type: 'smell', action: 'Name 2 things you can SMELL (or like to smell).' },
    { sense: '👅', count: 1, type: 'taste', action: 'Name 1 thing you can TASTE right now.' },
  ];
  let stepIdx = 0;

  function renderStep() {
    const s = steps[stepIdx];
    el.innerHTML = `
      <div class="exercise-title">🌍 5-4-3-2-1 Grounding</div>
      <div class="grounding-step">
        <div class="grounding-sense">${s.sense}</div>
        <div style="font-size:32px;font-weight:800;color:var(--primary-light);margin-bottom:12px;">${s.count}</div>
        <div class="grounding-instruction">${s.action}</div>
      </div>
      <div class="exercise-progress"><div class="exercise-progress-bar" style="width:${(stepIdx + 1) / steps.length * 100}%"></div></div>
      <div style="display:flex;gap:12px;justify-content:center;margin-top:20px;">
        ${stepIdx > 0 ? '<button class="btn-icon" onclick="groundingPrev()">← Back</button>' : ''}
        <button class="btn-primary" style="max-width:160px;" onclick="groundingNext()">${stepIdx < steps.length - 1 ? 'Next →' : 'Finish ✅'}</button>
      </div>`;
  }

  window.groundingNext = () => {
    if (stepIdx < steps.length - 1) { stepIdx++; renderStep(); }
    else {
      el.innerHTML = `<div style="text-align:center;padding:20px;"><div style="font-size:64px;margin-bottom:16px;">🌿</div><div class="exercise-title">Grounded!</div><p style="color:var(--text-muted);margin-top:8px;">You're back in the present moment. Take a slow breath and carry on. 💙</p><button class="btn-primary" style="margin-top:20px;" onclick="closeExercise()">Close</button></div>`;
    }
  };
  window.groundingPrev = () => { if (stepIdx > 0) { stepIdx--; renderStep(); } };
  renderStep();
}

// ── 3. Progressive Muscle Relaxation ──────────────────────────
function startPMR(el) {
  const groups = [
    { name: 'Hands & Forearms', icon: '✊', instruction: 'Make a tight fist with both hands. Hold for 7 seconds, then release for 20 seconds. Feel the tension melt away.' },
    { name: 'Upper Arms & Shoulders', icon: '💪', instruction: 'Raise your shoulders up to your ears. Hold for 7 seconds, then drop them. Notice the warmth and relaxation.' },
    { name: 'Face & Jaw', icon: '😬', instruction: 'Scrunch your face tightly — eyes, nose, jaw. Hold for 7 seconds, then let go completely. Feel your face soften.' },
    { name: 'Chest & Abdomen', icon: '🫁', instruction: 'Take a deep breath, hold it, and tighten your stomach muscles for 7 seconds. Exhale slowly and release.' },
    { name: 'Legs & Feet', icon: '🦵', instruction: 'Tighten your thighs, calves and curl your toes. Hold 7 seconds, then release. Feel the relaxation spread.' },
  ];
  let idx = 0;

  function render() {
    const g = groups[idx];
    el.innerHTML = `
      <div class="exercise-title">💪 Muscle Relaxation</div>
      <div style="text-align:center;font-size:56px;margin:16px 0;">${g.icon}</div>
      <div style="text-align:center;font-size:16px;font-weight:700;margin-bottom:12px;">${g.name}</div>
      <div class="meditation-text">${g.instruction}</div>
      <div class="exercise-progress"><div class="exercise-progress-bar" style="width:${(idx + 1) / groups.length * 100}%"></div></div>
      <div style="display:flex;gap:12px;justify-content:center;margin-top:20px;">
        <button class="btn-primary" style="max-width:180px;" onclick="pmrNext()">${idx < groups.length - 1 ? 'Next Group →' : 'Complete ✅'}</button>
      </div>`;
  }

  window.pmrNext = () => {
    if (idx < groups.length - 1) { idx++; render(); }
    else { el.innerHTML = `<div style="text-align:center;padding:20px;"><div style="font-size:64px;margin-bottom:16px;">😌</div><div class="exercise-title">Fully Relaxed!</div><p style="color:var(--text-muted);margin-top:8px;">Your muscles are now relaxed. Notice how different your body feels. 🌿</p><button class="btn-primary" style="margin-top:20px;" onclick="closeExercise()">Close</button></div>`; }
  };
  render();
}

// ── 4. Quick Meditation ────────────────────────────────────────
function startMeditation(el) {
  const script = [
    "Close your eyes and take three deep, slow breaths. In through the nose… out through the mouth.",
    "With each exhale, release any tension you're holding. Let your shoulders drop, your jaw unclench.",
    "Picture a calm, peaceful place — a beach, a forest, a quiet room. You are safe here.",
    "Any thoughts that arise — simply notice them, and gently let them float away like clouds.",
    "Focus on the rhythm of your breath. Inhale peace… exhale stress. You are okay.",
    "Slowly bring your awareness back to the room. Wiggle your fingers. Take one final deep breath.",
    "Open your eyes when you're ready. Well done — you took time for yourself today. 💙"
  ];
  let idx = 0;
  const duration = 20;
  let timeLeft = duration;

  function render() {
    el.innerHTML = `
      <div class="exercise-title">🧘 Quick Meditation</div>
      <div class="meditation-text" id="med-text">${script[idx]}</div>
      <div class="exercise-timer" id="med-timer">${timeLeft}</div>
      <div class="exercise-progress"><div class="exercise-progress-bar" id="med-bar" style="width:${(idx / script.length) * 100}%"></div></div>
      <p style="text-align:center;color:var(--text-dim);font-size:12px;">Step ${idx + 1} of ${script.length}</p>`;

    clearInterval(exerciseTimer);
    exerciseTimer = setInterval(() => {
      timeLeft--;
      const timerEl = document.getElementById('med-timer');
      if (timerEl) timerEl.textContent = timeLeft;
      if (timeLeft <= 0) {
        clearInterval(exerciseTimer);
        idx++;
        if (idx >= script.length) {
          el.innerHTML = `<div style="text-align:center;padding:20px;"><div style="font-size:64px;margin-bottom:16px;">🌟</div><div class="exercise-title">Meditation Complete</div><p style="color:var(--text-muted);margin-top:8px;">You did something wonderful for yourself today. Carry this calm with you. 💙</p><button class="btn-primary" style="margin-top:20px;" onclick="closeExercise()">Close</button></div>`;
        } else {
          timeLeft = duration;
          render();
        }
      }
    }, 1000);
  }
  render();
}
