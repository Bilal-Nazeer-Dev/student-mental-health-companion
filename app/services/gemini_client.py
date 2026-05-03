from flask import current_app

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None

SYSTEM_INSTRUCTION = """
You are an AI-powered student mental health assistant.

Your role is to:
- Provide emotional support to students
- Help manage stress, anxiety, and academic pressure
- Suggest healthy study habits and relaxation techniques

Behavior Rules:
- Be empathetic, calm, and supportive
- Never judge the user
- Keep responses simple and clear
- Offer practical, actionable advice
- Do not provide medical diagnosis
- Encourage seeking real help in serious situations

Response Style:
- Friendly and human-like
- Short to medium length
- Use encouraging tone
- Avoid complex words

If user expresses extreme distress:
- Respond with care
- Suggest contacting trusted people or professionals
""".strip()


def _normalize_model_name(model_name: str) -> str:
    cleaned = (model_name or "").strip()
    if not cleaned or cleaned.startswith("gemini-1.5"):
        return "gemini-2.5-flash"
    return cleaned


def get_chat_response(user_message: str, context: list[dict]) -> str:
    api_key = current_app.config.get("GEMINI_API_KEY")
    model_name = _normalize_model_name(current_app.config.get("GEMINI_MODEL", "gemini-2.5-flash"))

    if not api_key or genai is None:
        return (
            "I hear you. Thank you for sharing this. Let us take one gentle step now: "
            "drink some water, take 5 slow breaths, and choose one small study task for 20 minutes."
        )

    genai.configure(api_key=api_key)

    prompt_parts = [SYSTEM_INSTRUCTION, "\nRecent context:"]
    for item in context[-10:]:
        role = item.get("role", "user")
        content = item.get("content", "")
        prompt_parts.append(f"{role}: {content}")

    prompt_parts.append(f"user: {user_message}")
    prompt_parts.append("assistant:")
    prompt = "\n".join(prompt_parts)

    model = genai.GenerativeModel(model_name)
    result = model.generate_content(prompt)
    text = getattr(result, "text", "")

    if not text:
        return (
            "I am here with you. Could you tell me a little more about what feels hardest right now?"
        )

    return text.strip()
