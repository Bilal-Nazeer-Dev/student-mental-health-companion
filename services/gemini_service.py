"""
Gemini AI Service — uses the new google-genai SDK (google.genai).
"""
import json
from google import genai
from google.genai import types
from config import Config

# ── System prompt ────────────────────────────────────────────────
SYSTEM_INSTRUCTION = """You are Sage, an AI-powered student mental health companion.

Your role:
- Provide emotional support to students facing stress, anxiety, and academic pressure
- Help students develop healthy study habits and a balanced lifestyle
- Offer practical relaxation and coping techniques
- Be a non-judgmental, empathetic listener

Behavior Rules:
- Always be empathetic, warm, and supportive — never clinical or robotic
- Never judge the user for their feelings or struggles
- Keep responses concise and readable (3-5 sentences unless more detail is genuinely needed)
- Offer practical, actionable advice when appropriate
- Do NOT provide medical diagnoses or clinical assessments
- If a student expresses serious distress or crisis, gently encourage them to reach out to a trusted person or professional counselor
- Use a friendly, human-like tone with occasional emojis to feel approachable

Response Style:
- Friendly, warm, and encouraging
- Simple language — avoid jargon
- Short to medium length responses
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

_client = None


def init_gemini():
    """Initialize the Gemini client. Called once at app startup."""
    global _client
    if Config.GEMINI_API_KEY:
        _client = genai.Client(api_key=Config.GEMINI_API_KEY)
        return True
    return False


def _get_client():
    global _client
    if _client is None and Config.GEMINI_API_KEY:
        _client = genai.Client(api_key=Config.GEMINI_API_KEY)
    return _client


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


# ── Chat ─────────────────────────────────────────────────────────

def chat_with_gemini(message: str, conversation_history: list) -> dict:
    client = _get_client()
    if not client:
        return {
            'response': (
                "I'm having trouble connecting right now. "
                "Please add your GEMINI_API_KEY to the .env file. "
                "Get a free key at aistudio.google.com 💙"
            ),
            'emotion': 'neutral',
            'emergency': False
        }
    try:
        # Build history in google-genai format
        history = []
        for msg in conversation_history[-10:]:
            role = 'user' if msg['role'] == 'user' else 'model'
            history.append(
                types.Content(role=role, parts=[types.Part(text=msg['content'])])
            )

        chat = client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.8,
                max_output_tokens=512,
            ),
            history=history,
        )
        response = chat.send_message(message)

        return {
            'response': response.text,
            'emotion': detect_emotion(message),
            'emergency': check_emergency(message)
        }
    except Exception as e:
        # Returning the real error message so we can debug exactly what is wrong
        return {
            'response': f"⚠️ API Error: {str(e)}\n\nPlease check your terminal logs or API key.",
            'emotion': 'neutral',
            'emergency': False,
            'error': str(e)
        }


# ── Study plan generation ─────────────────────────────────────────

def generate_study_plan(subjects: str, deadlines: str, available_hours: str, break_style: str) -> dict:
    client = _get_client()
    if not client:
        return _fallback_plan(subjects, available_hours)
    try:
        prompt = f"""Create a balanced 7-day study schedule for a student.

Subjects/Topics: {subjects}
Upcoming Deadlines: {deadlines}
Available study hours per day: {available_hours} hours
Preferred break style: {break_style}

Return ONLY a valid JSON object (no markdown, no code blocks) with this EXACT structure:
{{
  "overview": "Brief motivational summary (2-3 sentences)",
  "days": [
    {{
      "day": "Monday",
      "date": "Day 1",
      "sessions": [
        {{
          "time": "9:00 AM - 10:30 AM",
          "subject": "Subject Name",
          "task": "Specific task description",
          "type": "study"
        }}
      ],
      "tip": "Daily wellness tip"
    }}
  ]
}}

Types allowed: study, break, review, exercise
Rules:
- Include proper breaks based on break style
- Prioritize subjects with closer deadlines
- Include self-care/exercise at least once
- Keep it realistic
- Return ONLY raw JSON, nothing else"""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                max_output_tokens=2048,
            )
        )
        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1]) if lines[-1].strip() == '```' else '\n'.join(lines[1:])
        return json.loads(text.strip())
    except Exception:
        return _fallback_plan(subjects, available_hours)


# ── Weekly insight ────────────────────────────────────────────────

def generate_weekly_insight(mood_logs: list, checkin_count: int) -> str:
    client = _get_client()
    if not client or not mood_logs:
        return "Keep checking in daily to unlock your personalized AI insights! 🌟"
    try:
        avg = sum(l['score'] for l in mood_logs) / len(mood_logs)
        emotions = [l.get('emotion_tag', 'neutral') for l in mood_logs]
        prompt = f"""A student's weekly data:
- Average mood score: {avg:.1f}/5 over the past 7 days
- Check-ins completed: {checkin_count} out of 7 days
- Recent emotions: {', '.join(emotions[-7:])}

Write a warm, encouraging weekly insight (3-4 sentences) that:
1. Genuinely acknowledges their week
2. Highlights something positive
3. Gives one specific actionable suggestion
4. Ends with encouragement

Keep it personal, warm, and NOT clinical."""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.75,
                max_output_tokens=256,
            )
        )
        return response.text
    except Exception:
        return "You're doing great by showing up and tracking your wellbeing! Every small step counts. 🌟"


# ── Fallback plan (no API key) ────────────────────────────────────

def _fallback_plan(subjects: str, available_hours: str) -> dict:
    subjects_list = [s.strip() for s in subjects.split(',') if s.strip()] or ['General Study']
    days_info = [
        ('Monday',    'Focus on your hardest subject first. 💪'),
        ('Tuesday',   'Stay hydrated and take regular breaks.'),
        ('Wednesday', 'Halfway through — celebrate small wins! 🎉'),
        ('Thursday',  'Review notes from earlier this week.'),
        ('Friday',    'Light study day — prepare for the weekend.'),
        ('Saturday',  'Rest and recharge — you deserve it! 🌿'),
        ('Sunday',    'Plan and set intentions for next week.'),
    ]
    plan = {
        "overview": "Here's your personalized study plan! Balance is key — study smart, rest well, and take care of yourself. You've got this! 🚀",
        "days": []
    }
    for i, (day, tip) in enumerate(days_info):
        sessions = []
        if i < 5:
            for j, subj in enumerate(subjects_list[:3]):
                sessions.append({"time": f"{9+j*2}:00–{10+j*2}:30", "subject": subj, "task": f"Study & practice {subj}", "type": "study"})
                if j < 2:
                    sessions.append({"time": f"{10+j*2}:30–{10+j*2}:45", "subject": "Break", "task": "Stretch & hydrate 💧", "type": "break"})
        else:
            sessions = [
                {"time": "10:00–12:00", "subject": "Review", "task": "Review the week's toughest topics", "type": "review"},
                {"time": "12:00–13:00", "subject": "Self-care", "task": "Walk, meditate, or enjoy a hobby 🌿", "type": "exercise"},
            ]
        plan["days"].append({"day": day, "date": f"Day {i+1}", "sessions": sessions, "tip": tip})
    return plan
