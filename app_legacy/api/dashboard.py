from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models import MoodEntry, RelaxationSession, StudyPlan, StudyTask

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/overview")
@jwt_required()
def overview():
    user_id = int(get_jwt_identity())

    moods = MoodEntry.query.filter_by(user_id=user_id).all()
    avg_mood = round(sum(item.score for item in moods) / len(moods), 2) if moods else None

    plan_ids = [item.id for item in StudyPlan.query.filter_by(user_id=user_id).all()]
    total_tasks = 0
    completed_tasks = 0
    if plan_ids:
        tasks = StudyTask.query.filter(StudyTask.plan_id.in_(plan_ids)).all()
        total_tasks = len(tasks)
        completed_tasks = len([task for task in tasks if task.status == "completed"])

    relaxation_done = RelaxationSession.query.filter_by(user_id=user_id, completed=True).count()

    return {
        "mood_avg": avg_mood,
        "study_consistency": {
            "tasks_completed": completed_tasks,
            "tasks_total": total_tasks,
        },
        "relaxation_sessions": relaxation_done,
        "insights": [
            "Small consistent steps reduce stress better than long cramming sessions.",
            "Pair each 25-50 minute focus block with a short break.",
        ],
    }, 200
