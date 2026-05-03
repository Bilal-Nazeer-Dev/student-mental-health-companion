"""
Gemini AI Service — uses the google-generativeai SDK.
"""
import json
import google.generativeai as genai
from google.generativeai import types
from config import Config
from datetime import datetime

# ── System prompt ────────────────────────────────────────────────
SYSTEM_INSTRUCTION = """You are Feelora, an AI-powered student mental health companion.
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

def init_gemini():
    """Initialize the Gemini client. Called once at app startup."""
    if Config.GEMINI_API_KEY:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        return True
    return False

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
def chat_with_gemini(message: str, conversation_history: list, app_context: str = "") -> dict:
    if not Config.GEMINI_API_KEY:
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
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_INSTRUCTION)
        chat = model.start_chat(history=[])
        
        # Add conversation history
        for msg in conversation_history[-10:]:
            role = 'user' if msg['role'] == 'user' else 'model'
            chat.history.append(types.Content(role=role, parts=[types.Part(text=msg['content'])]))
        
        if app_context:
            enhanced_message = f"[SYSTEM CONTEXT: The user's current live app state is: '{app_context}'].\n\n{message}"
        else:
            enhanced_message = message

        response = chat.send_message(enhanced_message)
        return {
            'response': response.text,
            'emotion': detect_emotion(message),
            'emergency': check_emergency(message)
        }
    except Exception as e:
        return {
            'response': f"⚠️ API Error: {str(e)}\n\nPlease check your terminal logs or API key.",
            'emotion': 'neutral',
            'emergency': False,
            'error': str(e)
        }

# ── Study plan generation ─────────────────────────────────────────
def generate_study_plan(subjects: str, deadlines: str, available_hours: str, break_style: str, energy_level: str = "Medium", learning_style: str = "Visual", latest_mood: str = "Neutral") -> dict:
    if not Config.GEMINI_API_KEY:
        return _fallback_plan(subjects, available_hours)
    
    current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""You are Feelora, an expert academic coach. Create a highly personalized study schedule.
        
        CURRENT DATE & TIME: {current_time}
        Subjects/Topics: {subjects}
        Upcoming Deadlines: {deadlines}
        Available study hours per day: {available_hours} hours
        Preferred break style: {break_style}
        Energy Level: {energy_level}
        Learning Style: {learning_style}
        Latest Mood: {latest_mood} (USE THIS: If Mood is Low, suggest lighter tasks.)

        Return ONLY a valid JSON object with this structure:
        {{
          "overview": "Explanation of the plan structure",
          "days": [
            {{
              "day": "Today/Tomorrow/Monday",
              "date": "Day 1",
              "sessions": [
                {{
                  "time": "9:00 AM - 10:30 AM",
                  "subject": "Subject Name",
                  "task": "Actionable task",
                  "type": "study"
                }}
              ],
              "tip": "Daily wellness tip"
            }}
          ]
        }}"""

        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1]) if lines[-1].strip() == '```' else '\n'.join(lines[1:])
        return json.loads(text.strip())
    except Exception:
        return _fallback_plan(subjects, available_hours)

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
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "I see you've been reflecting on your mood. Keep it up!"

def generate_mood_reflection(score: int, description: str, triggers: str) -> str:
    if not Config.GEMINI_API_KEY:
        return "I'm here for you! Taking a moment to reflect is a great step."
        
    prompt = f"""You are Feelora. The student just logged their mood.
    Score: {score}/5. Description: {description}. Triggers: {triggers}.
    Write a short (2 sentences max), highly empathetic response."""

    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "I'm here for you! Taking a moment to reflect is a great step."

def generate_mood_question(score: int) -> str:
    if not Config.GEMINI_API_KEY:
        return "What's on your mind today?"
        
    prompt = f"Ask an empathetic question to a student who just clicked {score}/5 on a mood scale."

    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "Would you like to share what's on your mind today?"

def generate_weekly_report(logs: list) -> str:
    if not Config.GEMINI_API_KEY or not logs:
        return "Connect your API key to see your AI reports! 💙"
    
    log_text = "\n".join([f"- Score: {l['score']}/5, Description: {l['description']}" for l in logs])
    prompt = f"Analyze these student logs and provide a 3-part wellbeing report: Trend, Challenges, Path Forward.\n\nLOGS:\n{log_text}"
    
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "I couldn't generate the report right now. Keep logging your mood!"

# ── Fallback plan (no API key) ────────────────────────────────────
def _fallback_plan(subjects: str, available_hours: str) -> dict:
    subjects_list = [s.strip() for s in subjects.split(',') if s.strip()] or ['General Study']
    days_info = [('Monday', 'Focus!'), ('Tuesday', 'Hydrate!'), ('Wednesday', 'Win!'), ('Thursday', 'Review!'), ('Friday', 'Rest!'), ('Saturday', 'Recharge!'), ('Sunday', 'Plan!')]
    plan = {"overview": "Here is a balanced plan to get you started! 🚀", "days": []}
    for i, (day, tip) in enumerate(days_info):
        sessions = [{"time": "9:00 AM", "subject": subjects_list[0], "task": "Study hard", "type": "study"}]
        plan["days"].append({"day": day, "date": f"Day {i+1}", "sessions": sessions, "tip": tip})
    return plan
