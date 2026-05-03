/* ── auth.js — Client-side auth helpers ─────────────────────── */
// auth.js is minimal — session is managed server-side.
// Login/register logic lives in index.html (standalone page).
// This file is only loaded in app.html for convenience exports.

function getStoredUser() {
  try { return JSON.parse(localStorage.getItem('feelora_user')); } catch { return null; }
}
