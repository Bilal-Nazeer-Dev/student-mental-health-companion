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
    }
  } catch { /* silent */ }
}

// ── Send message ────────────────────────────────────────────────
async function sendMessage() {
  if (isSending) return;
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  if (!message) return;

  input.value = '';
  input.style.height = 'auto';
  isSending = true;
  document.getElementById('btn-send').disabled = true;

  appendMessage(message, 'user');
  showTyping(true);
  scrollToBottom();

  try {
    const res = await fetch('/api/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    showTyping(false);

    if (res.ok) {
      appendMessage(data.response, 'assistant', data.emotion);
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

// Load history when module initialises
window.addEventListener('load', loadChatHistory);
