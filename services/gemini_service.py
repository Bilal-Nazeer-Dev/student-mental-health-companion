"""
Gemini AI Service — uses the google-generativeai SDK.
"""
import json
import google.generativeai as genai
from google.generativeai import types
from config import Config
from datetime import datetime

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
        model = genai.GenerativeModel(Config.GEMINI_MODEL, system_instruction=SYSTEM_INSTRUCTION)
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
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
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
           - The 'days' array in your JSON response must contain EXACTLY ONE entry.
           - This entry should be titled 'Urgent: Until Exam Morning' or 'Next 24 Hours'.
           - Break down the syllabus into specific hourly sessions (e.g., 8pm-9pm, 9pm-10pm) to finish the remaining topics before the exam time.
        2. IF NO URGENT DEADLINE: You may create a standard 3-7 day plan.
        3. SYLLABUS COMPLETION: If the user hasn't specified what is ALREADY completed (e.g., "I've done 50%"), use the 'overview' to explicitly ask: "How much of the syllabus have you already completed? I've made this plan assuming you need to cover everything, but I can refine it if you tell me what's left."
        4. NO FILLER: Focus on task completion, not 'long-term growth'.

        Return ONLY a valid JSON object:
        {{
          "overview": "Direct response. If deadline is tomorrow, start with: 'Here is your urgent breakdown until tomorrow morning...'. Ask about syllabus status if missing.",
          "days": [
            {{
              "day": "Urgent Plan (Next 24 Hours)",
              "date": "{current_time}",
              "sessions": [
                {{
                  "time": "Specific Time (e.g., 10:00 PM - 11:30 PM)",
                  "subject": "Subject",
                  "task": "Specific chapter or topic to FINISH",
                  "type": "study"
                }}
              ],
              "tip": "High-intensity focus tip"
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
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
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
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
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
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
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
    
    # Check if the user mentioned "tomorrow" in subjects (poor man's NLP for fallback)
    is_urgent = 'tomorrow' in subjects.lower()
    
    plan = {
        "overview": "I'm currently in high-urgency mode. Here is a focused plan to help you finish your remaining syllabus.",
        "days": []
    }
    
    if is_urgent:
        # Urgent case: 1 day, multiple sessions
        sessions = [
            {"time": "Now - 2 Hours", "subject": subjects_list[0], "task": "Intensive Review of Core Topics", "type": "study"},
            {"time": "Next 2 Hours", "subject": subjects_list[0], "task": "Practice Past Papers/Key Questions", "type": "study"},
            {"time": "Before Sleep", "subject": subjects_list[0], "task": "Final Syllabus Check", "type": "study"}
        ]
        plan["days"].append({
            "day": "Urgent Plan (Next 24 Hours)",
            "date": "Today/Tomorrow",
            "sessions": sessions,
            "tip": "Focus on high-yield topics only. You've got this!"
        })
        plan["overview"] = "Here is your urgent breakdown for the next 24 hours. Please tell me how much of the syllabus is already completed for a better plan!"
    else:
        # Standard case: 7 days
        days_info = [('Monday', 'Focus!'), ('Tuesday', 'Hydrate!'), ('Wednesday', 'Win!'), ('Thursday', 'Review!'), ('Friday', 'Rest!'), ('Saturday', 'Recharge!'), ('Sunday', 'Plan!')]
        for i, (day, tip) in enumerate(days_info):
            sessions = [{"time": "9:00 AM", "subject": subjects_list[0], "task": "Study session", "type": "study"}]
            plan["days"].append({"day": day, "date": f"Day {i+1}", "sessions": sessions, "tip": tip})

    return plan
