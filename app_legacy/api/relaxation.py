from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.core.extensions import db
from app.models import RelaxationSession

relaxation_bp = Blueprint("relaxation", __name__)

EXERCISES = [
    {
        "id": "breath-4-4-4-4",
        "title": "Box Breathing",
        "type": "breathing",
        "duration": 5,
        "instructions": [
            "Inhale for 4 seconds.",
            "Hold for 4 seconds.",
            "Exhale for 4 seconds.",
            "Hold for 4 seconds and repeat.",
        ],
    },
    {
        "id": "mindful-5",
        "title": "5-Minute Mindful Reset",
        "type": "meditation",
        "duration": 5,
        "instructions": [
            "Sit comfortably and relax your shoulders.",
            "Notice your breathing without changing it.",
            "Gently return your focus when your mind drifts.",
        ],
    },
]


@relaxation_bp.get("/exercises")
@jwt_required()
def get_exercises():
    ex_type = request.args.get("type")
    if ex_type:
        result = [item for item in EXERCISES if item["type"] == ex_type]
    else:
        result = EXERCISES
    return {"exercises": result}, 200


@relaxation_bp.post("/session/start")
@jwt_required()
def start_session():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    exercise_type = data.get("exercise_type", "breathing")
    duration = int(data.get("duration_minutes", 5))

    session = RelaxationSession(
        user_id=user_id,
        exercise_type=exercise_type,
        duration_minutes=duration,
        completed=False,
    )
    db.session.add(session)
    db.session.commit()

    return {
        "session_id": session.id,
        "exercise_type": session.exercise_type,
        "duration_minutes": session.duration_minutes,
    }, 201


@relaxation_bp.post("/session/complete")
@jwt_required()
def complete_session():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    session_id = data.get("session_id")

    if not session_id:
        return {"error": "session_id is required"}, 400

    session = RelaxationSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return {"error": "session not found"}, 404

    session.completed = True
    db.session.commit()

    return {"status": "completed", "session_id": session.id}, 200
