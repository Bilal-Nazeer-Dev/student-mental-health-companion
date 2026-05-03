"""
Gemini AI Service — uses the google-generativeai SDK.
"""
import json
import logging
import time
from datetime import datetime

import google.generativeai as genai

from config import Config

logger = logging.getLogger('gemini_service')

# ── System prompt ────────────────────────────────────────────────
SYSTEM_INSTRUCTION = """You are Feelora, an AI-powered student mental health companion and high-intensity study planner.
Your role:
- Provide emotional support to students facing stress, anxiety, and academic pressure
- Handle study scheduling strictly based on urgency and next-day priorities
- If a user mentions an exam is "tomorrow", focus ONLY on a plan until tomorrow morning — no long-term planning
- Always ask for current syllabus completion status if it's not provided before making a detailed plan
- Offer practical relaxation and coping techniques
Behavior Rules:
- Always be empathetic, warm, and supportive — never clinical or robotic
- For urgent deadlines, be direct, encouraging, and highly focused on immediate tasks
- Keep responses concise and readable (3-5 sentences unless more detail is genuinely needed)
- If a student expresses serious distress or crisis, gently encourage them to reach out to a trusted person or professional counselor
Response Style:
- Friendly, warm, and encouraging
- Simple language — avoid jargon
- End with an open question or gentle encouragement when appropriate
If extreme distress is detected (hopelessness, self-harm thoughts, crisis):
- Respond with deep care and compassion
- Strongly encourage contacting a trusted friend, family member, or counselor
- Mention the Umang helpline: 0311-7786264 (Pakistan)"""

EMERGENCY_KEYWORDS = [
    'suicide', 'kill myself', 'end my life', 'want to die', 'self harm',
    'self-harm', 'hurt myself', 'no reason to live', 'end it all',
    'give up on life', 'not worth living', 'cut myself', 'overdose',
    "can't go on", 'cant go on'
]

GENERIC_FALLBACK_REPLY = (
    "I'm having a bit of trouble processing that right now. "
    "Could you try again in a moment? 💙"
)

_TRANSIENT_HTTP_CODES = ('500', '502', '503', '504')

_configured = False


# ── Init ──────────────────────────────────────────────────────────
def init_gemini() -> bool:
    """Configure the Gemini SDK once at app startup."""
    global _configured
    if not Config.GEMINI_API_KEY:
        logger.error('init_gemini: no API key configured')
        return False
    genai.configure(api_key=Config.GEMINI_API_KEY)
    _configured = True
    logger.info('init_gemini: configured with model=%s', Config.GEMINI_MODEL)
    return True


def _ensure_configured() -> None:
    """Lazy-configure the SDK if init_gemini() wasn't called yet."""
    if not _configured and Config.GEMINI_API_KEY:
        init_gemini()


# ── Helpers ───────────────────────────────────────────────────────
def check_emergency(message: str) -> bool:
    ml = message.lower()
    return any(kw in ml for kw in EMERGENCY_KEYWORDS)


def detect_emotion(message: str) -> str:
    ml = message.lower()
    if any(w in ml for w in ['anxious', 'anxiety', 'nervous', 'worried', 'panic', 'scared']):
        return 'anxious'
    if any(w in ml for w in ['stressed', 'stress', 'overwhelmed', 'pressure', 'burnout']):
        return 'stressed'
    if any(w in ml for w in ['sad', 'depressed', 'depression', 'unhappy', 'lonely', 'alone', 'crying']):
        return 'sad'
    if any(w in ml for w in ['angry', 'frustrated', 'mad', 'irritated', 'annoyed']):
        return 'frustrated'
    if any(w in ml for w in ['happy', 'good', 'great', 'excited', 'amazing', 'wonderful', 'grateful']):
        return 'happy'
    if any(w in ml for w in ['tired', 'sleepy', 'drained', 'exhausted', 'fatigued']):
        return 'tired'
    return 'neutral'


def _safe_response_text(response) -> str:
    """Extract text from a Gemini response without crashing on safety/empty cases.

    response.text raises ValueError when there are no candidates (safety block,
    recitation, or empty completion). Inspect prompt_feedback / finish_reason
    instead and return a clear, non-empty string.
    """
    try:
        text = response.text
        if text and text.strip():
            return text.strip()
    except (ValueError, AttributeError):
        pass

    feedback = getattr(response, 'prompt_feedback', None)
    block_reason = getattr(feedback, 'block_reason', None) if feedback else None
    if block_reason:
        logger.warning('Gemini blocked the prompt: %s', block_reason)
        return (
            "I can't respond to that one — it tripped a safety filter. "
            "Could you rephrase what's on your mind? 💙"
        )

    candidates = getattr(response, 'candidates', None) or []
    if candidates:
        finish = getattr(candidates[0], 'finish_reason', None)
        logger.warning('Gemini returned no usable text. finish_reason=%s', finish)
        if str(finish).upper().endswith('SAFETY'):
            return (
                "I had to hold back on that response for safety reasons. "
                "Want to try asking it a different way? 💙"
            )

    logger.warning('Gemini returned an empty response.')
    return GENERIC_FALLBACK_REPLY


def _classify_error(error_msg: str) -> str:
    """Map a raw exception message to a friendly user-facing reply."""
    lower = error_msg.lower()
    if 'api_key_invalid' in lower or 'api key not valid' in lower or 'permission_denied' in lower:
        return (
            "⚠️ API Key Error: Your Gemini API key is invalid or unauthorized.\n\n"
            "✅ Fix: Double-check GEMINI_API_KEY in your .env file. "
            "Get a fresh key at https://aistudio.google.com."
        )
    if '429' in error_msg or 'quota' in lower or 'rate limit' in lower:
        return (
            "⚠️ Quota Exceeded: The AI is a bit busy right now.\n\n"
            "✅ Fix: Wait a minute and try again, or switch GEMINI_MODEL."
        )
    if 'not found' in lower or '404' in error_msg:
        return (
            f"⚠️ Model Error: The model '{Config.GEMINI_MODEL}' was not found.\n\n"
            "✅ Fix: Set GEMINI_MODEL in your .env to a supported model "
            "(e.g. gemini-flash-latest)."
        )
    if any(code in error_msg for code in _TRANSIENT_HTTP_CODES) or 'deadline' in lower or 'timeout' in lower:
        return (
            "⚠️ Temporary Service Issue: Gemini is having a moment.\n\n"
            "✅ Fix: Please try again in a few seconds."
        )
    return GENERIC_FALLBACK_REPLY


def _sanitize_history(conversation_history: list) -> list:
    """Convert app-format history to Gemini-format, preserving user/model alternation.

    - Drops messages that are noise (errors, empty content).
    - Drops leading 'model' turns (Gemini history must start with user).
    - Collapses consecutive same-role turns by keeping only the latest one,
      so the API never sees two user-roles or two model-roles in a row.
    """
    cleaned = []
    for msg in conversation_history[-10:]:
        content = (msg.get('content') or '').strip()
        if not content:
            continue
        if '⚠️' in content or 'API Key Error' in content or 'Google API Error' in content:
            continue
        role = 'user' if msg.get('role') == 'user' else 'model'
        cleaned.append({'role': role, 'parts': [{'text': content}]})

    while cleaned and cleaned[0]['role'] != 'user':
        cleaned.pop(0)

    deduped = []
    for entry in cleaned:
        if deduped and deduped[-1]['role'] == entry['role']:
            deduped[-1] = entry
        else:
            deduped.append(entry)
    return deduped


def _generate_with_retry(model, *args, retries: int = 2, **kwargs):
    """Call generate_content / send_message with one retry for transient failures."""
    last_exc = None
    for attempt in range(retries + 1):
        try:
            return model(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            msg = str(exc)
            if not (any(c in msg for c in _TRANSIENT_HTTP_CODES) or 'timeout' in msg.lower() or 'deadline' in msg.lower()):
                raise
            if attempt < retries:
                wait = 2 ** attempt
                logger.warning('Transient Gemini error (attempt %d): %s — retrying in %ds', attempt + 1, exc, wait)
                time.sleep(wait)
    raise last_exc


# ── Chat ─────────────────────────────────────────────────────────
def chat_with_gemini(message: str, conversation_history: list, app_context: str = "") -> dict:
    if not Config.GEMINI_API_KEY:
        return {
            'response': (
                "I'm having trouble connecting right now. "
                "Please add your GEMINI_API_KEY to the .env file. "
                "Get a free key at https://aistudio.google.com 💙"
            ),
            'emotion': 'neutral',
            'emergency': False,
        }
    try:
        _ensure_configured()
        model = genai.GenerativeModel(Config.GEMINI_MODEL, system_instruction=SYSTEM_INSTRUCTION)
        history = _sanitize_history(conversation_history)
        chat = model.start_chat(history=history)

        if app_context:
            enhanced_message = f"[SYSTEM CONTEXT: The user's current live app state is: '{app_context}'].\n\n{message}"
        else:
            enhanced_message = message

        response = _generate_with_retry(chat.send_message, enhanced_message)
        return {
            'response': _safe_response_text(response),
            'emotion': detect_emotion(message),
            'emergency': check_emergency(message),
        }
    except Exception as exc:  # noqa: BLE001
        error_msg = str(exc)
        logger.exception('chat_with_gemini failed: %s', error_msg)
        return {
            'response': _classify_error(error_msg),
            'emotion': 'neutral',
            'emergency': False,
            'error': error_msg,
        }


# ── Study plan generation ─────────────────────────────────────────
def generate_study_plan(subjects: str, deadlines: str, available_hours: str, break_style: str,
                        energy_level: str = "Medium", learning_style: str = "Visual",
                        latest_mood: str = "Neutral") -> dict:
    if not Config.GEMINI_API_KEY:
        return {
            "overview": (
                "⚠️ API Key Not Found!\n\n"
                "To generate AI-powered study plans:\n"
                "1. Get a free key at https://aistudio.google.com\n"
                "2. Add it to your .env file as GEMINI_API_KEY=your_key_here\n"
                "3. Restart the app"
            ),
            "days": [],
        }

    current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    prompt = f"""You are Feelora, a high-intensity AI study planner. Your role is to handle scheduling strictly based on urgency.

CURRENT DATE & TIME: {current_time}
Subjects/Topics: {subjects}
Upcoming Deadlines: {deadlines}
Available study hours: {available_hours}
Break style: {break_style}
Latest Mood: {latest_mood}

CRITICAL URGENCY RULES:
1. IF EXAM/DEADLINE IS TOMORROW OR WITHIN 24 HOURS:
   - You MUST NOT create a week-long or multi-day schedule.
   - The 'days' array must contain EXACTLY ONE entry.
   - Title it 'Urgent: Until Exam Morning' or 'Next 24 Hours'.
   - Break the syllabus into specific hourly sessions.
2. IF NO URGENT DEADLINE: Create a standard 3-7 day plan.
3. SYLLABUS COMPLETION: If the user hasn't specified what's already done, ask in 'overview'.
4. NO FILLER: Focus on task completion, not 'long-term growth'.

Return ONLY a valid JSON object with this exact shape:
{{
  "overview": "string",
  "days": [
    {{
      "day": "string",
      "date": "{current_time}",
      "sessions": [
        {{"time": "string", "subject": "string", "task": "string", "type": "study"}}
      ],
      "tip": "string"
    }}
  ]
}}"""

    try:
        _ensure_configured()
        model = genai.GenerativeModel(
            Config.GEMINI_MODEL,
            generation_config={'response_mime_type': 'application/json'},
        )
        response = _generate_with_retry(model.generate_content, prompt)
        text = _safe_response_text(response)
        return json.loads(text)
    except json.JSONDecodeError as exc:
        logger.error('Study plan JSON parse failed: %s — falling back', exc)
        return _fallback_plan(subjects, available_hours)
    except Exception as exc:  # noqa: BLE001
        error_msg = str(exc)
        logger.exception('generate_study_plan failed: %s', error_msg)
        return {
            "overview": _classify_error(error_msg),
            "days": [],
        }


# ── Weekly insight ────────────────────────────────────────────────
def generate_weekly_insight(logs, checkins_this_week):
    if not Config.GEMINI_API_KEY or not logs:
        return "Keep tracking to see your growth over time! 💙"

    avg_score = sum(l['score'] for l in logs) / len(logs)
    prompt = f"""You are Feelora. Analyze this student's week:
Average Mood: {avg_score:.1f}/5
Check-ins: {checkins_this_week} this week
Logs: {[f"Text: {l['description']}, Emotion: {l['emotion_tag']}" for l in logs]}

Write a warm, insightful 2-sentence summary. Keep it encouraging."""
    try:
        _ensure_configured()
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = _generate_with_retry(model.generate_content, prompt)
        return _safe_response_text(response)
    except Exception as exc:  # noqa: BLE001
        logger.warning('generate_weekly_insight failed: %s', exc)
        return "I see you've been reflecting on your mood. Keep it up!"


def generate_mood_reflection(score: int, description: str, triggers: str) -> str:
    if not Config.GEMINI_API_KEY:
        return "I'm here for you! Taking a moment to reflect is a great step."

    prompt = f"""You are Feelora. The student just logged their mood.
Score: {score}/5. Description: {description}. Triggers: {triggers}.
Write a short (2 sentences max), highly empathetic response."""
    try:
        _ensure_configured()
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = _generate_with_retry(model.generate_content, prompt)
        return _safe_response_text(response)
    except Exception as exc:  # noqa: BLE001
        logger.warning('generate_mood_reflection failed: %s', exc)
        return "I'm here for you! Taking a moment to reflect is a great step."


def generate_mood_question(score: int) -> str:
    if not Config.GEMINI_API_KEY:
        return "What's on your mind today?"

    prompt = f"Ask an empathetic question to a student who just clicked {score}/5 on a mood scale."
    try:
        _ensure_configured()
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = _generate_with_retry(model.generate_content, prompt)
        return _safe_response_text(response)
    except Exception as exc:  # noqa: BLE001
        logger.warning('generate_mood_question failed: %s', exc)
        return "Would you like to share what's on your mind today?"


def generate_weekly_report(logs: list) -> str:
    if not Config.GEMINI_API_KEY or not logs:
        return "Connect your API key to see your AI reports! 💙"

    log_text = "\n".join([f"- Score: {l['score']}/5, Description: {l['description']}" for l in logs])
    prompt = f"Analyze these student logs and provide a 3-part wellbeing report: Trend, Challenges, Path Forward.\n\nLOGS:\n{log_text}"
    try:
        _ensure_configured()
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = _generate_with_retry(model.generate_content, prompt)
        return _safe_response_text(response)
    except Exception as exc:  # noqa: BLE001
        logger.warning('generate_weekly_report failed: %s', exc)
        return "I couldn't generate the report right now. Keep logging your mood!"


# ── Fallback plan (no API key / parse failure) ────────────────────
def _fallback_plan(subjects: str, available_hours: str) -> dict:
    subjects_list = [s.strip() for s in subjects.split(',') if s.strip()] or ['General Study']
    is_urgent = 'tomorrow' in subjects.lower()
    plan = {
        "overview": "I'm currently in high-urgency mode. Here is a focused plan to help you finish your remaining syllabus.",
        "days": [],
    }
    if is_urgent:
        sessions = [
            {"time": "Now - 2 Hours", "subject": subjects_list[0], "task": "Intensive Review of Core Topics", "type": "study"},
            {"time": "Next 2 Hours", "subject": subjects_list[0], "task": "Practice Past Papers/Key Questions", "type": "study"},
            {"time": "Before Sleep", "subject": subjects_list[0], "task": "Final Syllabus Check", "type": "study"},
        ]
        plan["days"].append({
            "day": "Urgent Plan (Next 24 Hours)",
            "date": "Today/Tomorrow",
            "sessions": sessions,
            "tip": "Focus on high-yield topics only. You've got this!",
        })
        plan["overview"] = (
            "Here is your urgent breakdown for the next 24 hours. "
            "Please tell me how much of the syllabus is already completed for a better plan!"
        )
    else:
        days_info = [('Monday', 'Focus!'), ('Tuesday', 'Hydrate!'), ('Wednesday', 'Win!'),
                     ('Thursday', 'Review!'), ('Friday', 'Rest!'), ('Saturday', 'Recharge!'),
                     ('Sunday', 'Plan!')]
        for i, (day, tip) in enumerate(days_info):
            sessions = [{"time": "9:00 AM", "subject": subjects_list[0], "task": "Study session", "type": "study"}]
            plan["days"].append({"day": day, "date": f"Day {i+1}", "sessions": sessions, "tip": tip})
    return plan
