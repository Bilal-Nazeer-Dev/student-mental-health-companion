from typing import Tuple

CRISIS_TERMS = [
    "kill myself",
    "suicide",
    "end my life",
    "self harm",
    "i want to die",
    "lost all hope",
]


def detect_emergency(text: str) -> Tuple[bool, str]:
    lowered = text.lower()
    for term in CRISIS_TERMS:
        if term in lowered:
            return True, "high"

    stress_terms = ["hopeless", "panic", "breakdown", "cannot cope"]
    for term in stress_terms:
        if term in lowered:
            return True, "medium"

    return False, "none"


def emergency_support_message() -> str:
    return (
        "I am really glad you shared this. You matter, and you do not have to face this alone. "
        "Please contact someone you trust right now, and if you are in immediate danger, call your local emergency services. "
        "If available in your region, contact a crisis helpline or your campus counselor immediately."
    )
