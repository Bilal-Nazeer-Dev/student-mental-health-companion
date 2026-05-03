"""
Gemini AI Service — uses the google-generativeai SDK.
"""
import json
import google.generativeai as genai
from google.generativeai import types
from config import Config

# ── System prompt ────────────────────────────────────────────────
<<<<<<< HEAD
SYSTEM_INSTRUCTION = """You are Feelora, an AI-powered student mental health companion.

=======
SYSTEM_INSTRUCTION = """You are Sage, an AI-powered student mental health companion.
>>>>>>> 852b4a1e82c1bad35b79ecaddd2b23ce7037eb60
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
<<<<<<< HEAD

def chat_with_gemini(message: str, conversation_history: list, app_context: str = "") -> dict:
    client = _get_client()
    if not client:
=======
def chat_with_gemini(message: str, conversation_history: list) -> dict:
    if not Config.GEMINI_API_KEY:
>>>>>>> 852b4a1e82c1bad35b79ecaddd2b23ce7037eb60
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
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTION)
        chat = model.start_chat(history=[])
        
        # Add conversation history
        for msg in conversation_history[-10:]:
            role = 'user' if msg['role'] == 'user' else 'model'
<<<<<<< HEAD
            history.append(
                types.Content(role=role, parts=[types.Part(text=msg['content'])])
            )

        chat = client.chats.create(
            model='gemini-flash-latest',
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.8,
                max_output_tokens=512,
            ),
            history=history,
        )
        
        if app_context:
            enhanced_message = f"[SYSTEM CONTEXT - DO NOT REPEAT THIS: The user's current live app state is: '{app_context}'. You may casually acknowledge this if it relates to their message.]\n\n{message}"
        else:
            enhanced_message = message

        response = chat.send_message(enhanced_message)

=======
            chat.history.append(types.Content(role=role, parts=[types.Part(text=msg['content'])]))
        
        response = chat.send_message(message)
>>>>>>> 852b4a1e82c1bad35b79ecaddd2b23ce7037eb60
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
<<<<<<< HEAD

def generate_study_plan(subjects: str, deadlines: str, available_hours: str, break_style: str, energy_level: str = "Medium", learning_style: str = "Visual", latest_mood: str = "Neutral") -> dict:
    client = _get_client()
    if not client:
=======
def generate_study_plan(subjects: str, deadlines: str, available_hours: str, break_style: str) -> dict:
    if not Config.GEMINI_API_KEY:
>>>>>>> 852b4a1e82c1bad35b79ecaddd2b23ce7037eb60
        return _fallback_plan(subjects, available_hours)
    
    current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    
    try:
<<<<<<< HEAD
        prompt = f"""You are Feelora, an expert academic coach. Create a highly personalized, realistic, and dynamic study schedule for a student.

CURRENT REAL-WORLD DATE & TIME: {current_time}

=======
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""Create a balanced 7-day study schedule for a student.
>>>>>>> 852b4a1e82c1bad35b79ecaddd2b23ce7037eb60
Subjects/Topics: {subjects}
Upcoming Deadlines: {deadlines}
Available study hours per day: {available_hours} hours
Preferred break style: {break_style}
<<<<<<< HEAD
Energy Level: {energy_level}
Learning Style: {learning_style}
Latest Mood: {latest_mood} (USE THIS TO ADJUST STUDY INTENSITY: If Mood is Low/Anxious, suggest lighter tasks. If Mood is High, suggest tackling harder topics.)

Instructions:
1. ANALYZE DEADLINES & TIME: The current time is {current_time}. Generate a schedule that starts exactly from the next available hour today, and extends for ONLY the necessary days (e.g. 1-3 days if exams are imminent). Do not use generic labels like "Day 1"; use actual dates (e.g. "Today", "May 4th").
2. TAILOR THE SESSIONS: Adapt the task suggestions to match their {learning_style} learning style. Also adjust the intensity of the tasks to match their {energy_level} energy level.
3. INCLUDE WELLNESS: Add quick mindfulness breaks based on their preferred break style.

Return ONLY a valid JSON object (no markdown, no code blocks) with this EXACT structure:
{{
  "overview": "A dynamic, personalized overview explaining WHY you structured the plan this way (e.g., 'Since your exam is tomorrow, we are focusing on intensive review today...')",
  "days": [
    {{
      "day": "Day of week (e.g., Today, Tomorrow, Monday)",
      "date": "Day 1",
      "sessions": [
        {{
          "time": "e.g., 9:00 AM - 10:30 AM",
          "subject": "Subject Name",
          "task": "Highly specific task (e.g., 'Solve 5 past paper questions on Integration')",
          "type": "study"
        }}
      ],
      "tip": "A highly relevant wellness or focus tip for this specific day"
    }}
  ]
=======
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
>>>>>>> 852b4a1e82c1bad35b79ecaddd2b23ce7037eb60
}}
Types allowed: study, break, review, exercise
Rules:
<<<<<<< HEAD
- NEVER return more days than necessary based on the deadlines.
- Tasks must be actionable and specific, not just 'study chapter 1'.
- Return ONLY raw JSON, nothing else."""

        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                max_output_tokens=2048,
            )
        )
=======
- Include proper breaks based on break style
- Prioritize subjects with closer deadlines
- Include self-care/exercise at least once
- Keep it realistic
- Return ONLY raw JSON, nothing else"""
        response = model.generate_content(prompt)
>>>>>>> 852b4a1e82c1bad35b79ecaddd2b23ce7037eb60
        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1]) if lines[-1].strip() == '```' else '\n'.join(lines[1:])
        return json.loads(text.strip())
    except Exception:
        return _fallback_plan(subjects, available_hours)

# ── Weekly insight ────────────────────────────────────────────────
<<<<<<< HEAD

def generate_weekly_insight(logs, checkins_this_week):
    client = _get_client()
    if not client:
        return "I'm offline right now, but remember that every step counts. Keep taking care of yourself."

    if not logs:
        return "You haven't logged your mood recently. Start tracking to get personalized insights and see how you're growing over time."
    
    score_sum = sum(l['score'] for l in logs)
    avg_score = score_sum / len(logs)
    
    prompt = f"""You are Feelora. Analyze this student's week:
Average Mood: {avg_score:.1f}/5
Check-ins: {checkins_this_week} this week
Logs: {[f"Score: {l['score']}, Text: {l['description']}, Emotion: {l['emotion_tag']}" for l in logs]}

Write a warm, insightful, and motivating 2-sentence summary.
Point out a trend if you see one. Do NOT just repeat the numbers.
Keep it personal, warm, and NOT clinical."""

    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=150
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error (Insight): {e}")
        return "I see you've been reflecting on your mood. Keep it up, tracking is the first step to feeling better."

def generate_mood_reflection(score: int, description: str, triggers: str) -> str:
    client = _get_client()
    if not client:
        return "I'm here for you! Taking a moment to reflect is a great step."
        
    prompt = f"""You are Feelora. The student just logged their mood.
Score: {score}/5
Description: {description}
Context Tags/Triggers: {triggers}

Write a very short (2 sentences max), highly empathetic, and supportive response directly to them based on their description and tags. 
If they have a low score, offer a tiny, actionable coping step (like a deep breath). 
If they have a high score, celebrate it with them!
Do not include any formatting or hashtags."""

    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=150
            )
        )
        return response.text.strip()
=======
def generate_weekly_insight(mood_logs: list, checkin_count: int) -> str:
    if not Config.GEMINI_API_KEY or not mood_logs:
        return "Keep checking in daily to unlock your personalized AI insights! 🌟"
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTION)
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
        response = model.generate_content(prompt)
        return response.text
>>>>>>> 852b4a1e82c1bad35b79ecaddd2b23ce7037eb60
    except Exception:
        return "Thank you for sharing. Remember that whatever you're feeling is valid."

def generate_mood_question(score: int) -> str:
    client = _get_client()
    if not client:
        return "What's on your mind today?"
        
    prompt = f"""You are Feelora, an empathetic AI companion. The student just clicked a {score}/5 on the mood scale.
Ask a single, highly engaging, empathetic question to get them to talk about their day.
For example, if score is 1-2, ask something gentle like 'I'm so sorry you're feeling down. Has something specific been weighing on you?'
If score is 4-5, ask something cheerful like 'That's amazing! What made today so good?'
Return ONLY the question, nothing else. No formatting."""

    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=50
            )
        )
        return response.text.strip()
    except Exception:
        return "Would you like to share what's on your mind today?"


def generate_weekly_report(logs: list) -> str:
    client = _get_client()
    if not client:
        return "Connect your API key to see your AI mental health reports! 💙"
    
    # Format logs for AI
    log_text = "\n".join([f"- Score: {l['score']}/5, Description: {l['description']}, Emotion: {l['emotion_tag']}" for l in logs])
    
    prompt = f"""
    Analyze the following 7 days of student mental health logs and write a 'Weekly Wellbeing Report'.
    Structure it as follows:
    1. **Trend Analysis**: Summarize the overall mood trend.
    2. **Key Challenges**: Identify repeating triggers or stressors.
    3. **Path Forward**: Provide 3 personalized, supportive recommendations for the upcoming week.
    
    Keep the tone supportive, professional, and compassionate.
    
    LOGS:
    {log_text}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            config=types.GenerateContentConfig(
                system_instruction="You are Feelora's Clinical Psychology Module.",
                temperature=0.7,
            ),
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"I couldn't generate the report right now. Keep logging your mood, and we'll try again soon! 💙"


# ── Fallback plan (no API key) ────────────────────────────────────
def _fallback_plan(subjects: str, available_hours: str) -> dict:
    subjects_list = [s.strip() for s in subjects.split(',') if s.strip()] or ['General Study']
    days_info = [
        ('Monday', 'Focus on your hardest subject first. 💪'),
        ('Tuesday', 'Stay hydrated and take regular breaks.'),
        ('Wednesday', 'Halfway through — celebrate small wins! 🎉'),
        ('Thursday', 'Review notes from earlier this week.'),
        ('Friday', 'Light study day — prepare for the weekend.'),
        ('Saturday', 'Rest and recharge — you deserve it! 🌿'),
        ('Sunday', 'Plan and set intentions for next week.'),
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
