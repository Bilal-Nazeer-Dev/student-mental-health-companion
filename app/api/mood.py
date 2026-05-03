from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.core.extensions import db
from app.models import MoodEntry

mood_bp = Blueprint("mood", __name__)


@mood_bp.post("/log")
@jwt_required()
def log_mood():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    score = int(data.get("score", 0))
    if score < 1 or score > 10:
        return {"error": "score must be between 1 and 10"}, 400

    emotions = data.get("emotions", [])
    if isinstance(emotions, list):
        emotions_csv = ",".join([str(item).strip() for item in emotions if str(item).strip()])
    else:
        emotions_csv = str(emotions)

    entry = MoodEntry(
        user_id=user_id,
        score=score,
        emotions_csv=emotions_csv,
        notes=data.get("notes"),
    )
    db.session.add(entry)
    db.session.commit()

    return {
        "mood_entry_id": entry.id,
        "score": entry.score,
        "emotions": emotions_csv.split(",") if emotions_csv else [],
        "timestamp": entry.created_at.isoformat(),
    }, 201


@mood_bp.get("/trends")
@jwt_required()
def trends():
    user_id = int(get_jwt_identity())
    rows = MoodEntry.query.filter_by(user_id=user_id).order_by(MoodEntry.created_at.asc()).all()

    if not rows:
        return {
            "avg_score": None,
            "trend": "no-data",
            "common_emotions": [],
            "recommendations": ["Log your mood daily to get personalized insights."],
        }, 200

    avg = round(sum(row.score for row in rows) / len(rows), 2)
    trend = "stable"
    if len(rows) >= 2:
        delta = rows[-1].score - rows[0].score
        trend = "up" if delta > 0 else "down" if delta < 0 else "stable"

    emotion_count = {}
    for row in rows:
        for emotion in (row.emotions_csv or "").split(","):
            emotion = emotion.strip().lower()
            if not emotion:
                continue
            emotion_count[emotion] = emotion_count.get(emotion, 0) + 1

    top = sorted(emotion_count.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "avg_score": avg,
        "trend": trend,
        "common_emotions": [name for name, _ in top],
        "recommendations": [
            "Keep a short evening reflection.",
            "Use a 5-minute breathing exercise during high-stress periods.",
        ],
    }, 200
