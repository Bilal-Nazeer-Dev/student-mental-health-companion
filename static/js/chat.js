/* ── chat.js — Chat interface module ───────────────────────────── */

let isSending = false;

// ── Load chat history on panel open ────────────────────────────
async function loadChatHistory() {
  try {
    const res = await fetch('/api/chat/history');
    if (!res.ok) return;
    const data = await res.json();
    if (data.history && data.history.length > 0) {
      const msgs = document.getElementById('chat-messages');
      // Remove welcome message if we have history
      msgs.innerHTML = '';
      data.history.forEach(msg => {
        appendMessage(msg.content, msg.role === 'user' ? 'user' : 'assistant', null, false);
      });
      scrollToBottom();
      // Hide the load history button once loaded
      const historyBtn = document.getElementById('btn-load-history');
      if (historyBtn) historyBtn.style.display = 'none';
    }
  } catch { /* silent */ }
}

// ── Send message ────────────────────────────────────────────────
async function sendMessage() {
  if (isSending) return;
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  if (!message) return;

  if (typeof checkCrisis !== 'undefined' && checkCrisis(message)) {
    input.value = '';
    return;
  }

  input.value = '';
  input.style.height = 'auto';
  isSending = true;
  document.getElementById('btn-send').disabled = true;

  appendMessage(message, 'user');
  showTyping(true);
  scrollToBottom();

  // Gather Real-Time App Context
  const ambientSelect = document.getElementById('ambient-track');
  const ambientAudio = document.getElementById('ambient-audio');
  const ambientText = ambientSelect && ambientSelect.options[ambientSelect.selectedIndex].text;
  const isPlayingAmbient = ambientAudio && !ambientAudio.paused && ambientSelect.value ? ambientText : 'None';
  
  const focusContext = typeof isFocusing !== 'undefined' && isFocusing ? `Running (${document.getElementById('focus-mode-label').textContent}, ${Math.floor(focusTimeLeft/60)} mins left)` : 'Not active';
  
  const wellbeingContext = typeof wellbeingLevel !== 'undefined' ? `Level ${wellbeingLevel} (${wellbeingCurrent}/100)` : 'Level 1';
  
  const appContext = `Ambient Audio: ${isPlayingAmbient} | Focus Timer: ${focusContext} | Wellbeing Gamification: ${wellbeingContext}`;

  try {
    const res = await fetch('/api/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, appContext })
    });
    
    const data = await res.json(); // <-- Restored this line to fix the Connection Error
    
    if (res.ok) {
      appendMessage(data.response, 'assistant', data.emotion);
      updateTheme(data.emotion);
      if (data.emergency) triggerEmergency();
    } else {
      appendMessage('Sorry, I had trouble responding. Please try again. 💙', 'assistant');
    }
  } catch {
    showTyping(false);
    appendMessage('Connection error. Please check your connection and try again.', 'assistant');
  } finally {
    isSending = false;
    document.getElementById('btn-send').disabled = false;
    scrollToBottom();
  }
}

// ── Append a message bubble ─────────────────────────────────────
function appendMessage(content, role, emotion = null, animate = true) {
  const container = document.getElementById('chat-messages');

  // Remove welcome card on first real message
  const welcome = container.querySelector('.chat-welcome');
  if (welcome && role === 'user') welcome.remove();

  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;
  if (!animate) wrapper.style.animation = 'none';

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = role === 'user' ? '👤' : '🌿';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';

  // Format line breaks
  bubble.innerHTML = content.replace(/\n/g, '<br>');

  // Add emotion badge for assistant messages
  if (role === 'assistant' && emotion && emotion !== 'neutral') {
    const badge = document.createElement('div');
    badge.className = `emotion-badge emotion-${emotion}`;
    const labels = { anxious: '😰 Anxious', stressed: '😤 Stressed', sad: '😢 Sad', happy: '😊 Happy', frustrated: '😠 Frustrated', tired: '😴 Tired' };
    badge.textContent = labels[emotion] || emotion;
    bubble.appendChild(badge);
  }

  // Timestamp
  const meta = document.createElement('div');
  meta.className = 'msg-meta';
  meta.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  bubble.appendChild(meta);

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  container.appendChild(wrapper);
}

// ── Typing indicator ────────────────────────────────────────────
function showTyping(show) {
  const indicator = document.getElementById('typing-indicator');
  indicator.classList.toggle('show', show);
}

// ── Scroll to bottom ────────────────────────────────────────────
function scrollToBottom() {
  const msgs = document.getElementById('chat-messages');
  setTimeout(() => msgs.scrollTop = msgs.scrollHeight, 50);
}

// ── Handle Enter key ────────────────────────────────────────────
function handleChatKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

// ── Auto-resize textarea ────────────────────────────────────────
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

// ── Clear conversation ──────────────────────────────────────────
async function clearChat() {
  if (!confirm('Clear conversation history? This cannot be undone.')) return;
  await fetch('/api/chat/clear', { method: 'POST' });
  const msgs = document.getElementById('chat-messages');
  msgs.innerHTML = `
    <div class="chat-welcome">
      <div class="welcome-avatar">🌿</div>
      <div class="welcome-text">
        <strong>Conversation cleared.</strong><br/>
        I'm still here for you. How are you feeling?
      </div>
    </div>`;
  showToast('Conversation cleared', 'info');
}

// ── Dynamic Theme Update ────────────────────────────────────────
function updateTheme(emotion) {
  if (!emotion || emotion === 'neutral') return;
  const root = document.documentElement;
  let rgb = '124, 58, 237'; // Default Purple
  
  switch(emotion) {
    case 'happy': rgb = '245, 158, 11'; break; // Amber
    case 'sad': rgb = '59, 130, 246'; break; // Blue
    case 'anxious': rgb = '16, 185, 129'; break; // Calming Green
    case 'stressed': rgb = '239, 68, 68'; break; // Red
    case 'frustrated': rgb = '249, 115, 22'; break; // Orange
    case 'tired': rgb = '99, 102, 241'; break; // Indigo
  }
  
  root.style.setProperty('--emotion-color', rgb);
}

// ── Real-Time Empathy Engine ─────────────────────────────────────
function analyzeSentiment(text) {
  const indicator = document.getElementById('empathy-indicator');
  const icon = document.getElementById('empathy-icon');
  const label = document.getElementById('empathy-text');
  
  if (!text || text.length < 3) {
    indicator.style.opacity = '0';
    return;
  }
  
  indicator.style.opacity = '1';
  const lower = text.toLowerCase();
  
  if (lower.match(/\b(sad|depressed|cry|tears|down|hopeless|lonely|hurt)\b/)) {
    icon.textContent = '💙'; label.textContent = 'Feelora senses sadness...';
  } else if (lower.match(/\b(anxious|stress|stressed|worry|nervous|panic|overwhelmed|afraid)\b/)) {
    icon.textContent = '🌬️'; label.textContent = 'Feelora senses anxiety. Remember to breathe...';
  } else if (lower.match(/\b(angry|mad|frustrated|hate|annoyed|furious|upset)\b/)) {
    icon.textContent = '🧘'; label.textContent = 'Feelora senses frustration...';
  } else if (lower.match(/\b(happy|great|good|awesome|amazing|excited|joy|glad)\b/)) {
    icon.textContent = '✨'; label.textContent = 'Feelora senses positivity!';
  } else if (lower.match(/\b(tired|exhausted|sleepy|fatigue|drained)\b/)) {
    icon.textContent = '💤'; label.textContent = 'Feelora senses exhaustion...';
  } else {
    icon.textContent = '🔍'; label.textContent = 'Listening closely...';
  }
}

// ── Voice Dictation ──────────────────────────────────────────────
let recognition = null;
let isDictating = false;

function toggleDictation(e) {
  e.preventDefault();
  
  if (!('webkitSpeechRecognition' in window)) {
    showToast('Voice dictation is not supported in this browser.', 'error');
    return;
  }
  
  const btn = document.getElementById('btn-mic');
  
  if (isDictating) {
    if (recognition) recognition.stop();
    return;
  }
  
  recognition = new webkitSpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  
  recognition.onstart = function() {
    isDictating = true;
    btn.style.color = 'var(--danger)';
    btn.style.transform = 'scale(1.2)';
    showToast('Listening... Speak now.', 'success');
  };
  
  recognition.onresult = function(event) {
    let finalTranscript = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript;
      }
    }
    const input = document.getElementById('chat-input');
    if (finalTranscript) {
      input.value += (input.value ? ' ' : '') + finalTranscript;
      analyzeSentiment(input.value);
      autoResize(input);
    }
  };
  
  recognition.onerror = function(event) {
    console.error('Speech recognition error', event.error);
    stopDictationUI();
  };
  
  recognition.onend = function() {
    stopDictationUI();
  };
  
  recognition.start();
}

function stopDictationUI() {
  isDictating = false;
  const btn = document.getElementById('btn-mic');
  btn.style.color = '';
  btn.style.transform = '';
}

// Load setup voice when module initialises
window.addEventListener('load', () => {
  // We no longer auto-load chat history. User must click "Load History" button.
});
