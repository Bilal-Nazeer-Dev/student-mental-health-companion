from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.core.extensions import db
from app.models import StudyPlan, StudyTask

study_bp = Blueprint("study", __name__)


@study_bp.post("/plan/create")
@jwt_required()
def create_plan():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    title = data.get("title") or "Weekly Plan"
    tasks = data.get("tasks", [])

    plan = StudyPlan(user_id=user_id, title=title)
    db.session.add(plan)
    db.session.flush()

    created_tasks = []
    for item in tasks:
        task = StudyTask(
            plan_id=plan.id,
            subject=item.get("subject", "General"),
            deadline=item.get("deadline"),
            priority=item.get("priority", "medium"),
            duration_minutes=int(item.get("duration_minutes", 50)),
        )
        db.session.add(task)
        created_tasks.append(task)

    db.session.commit()

    return {
        "plan_id": plan.id,
        "title": plan.title,
        "schedule": [
            {
                "task_id": task.id,
                "subject": task.subject,
                "recommended_time": f"{task.duration_minutes} minutes",
                "break_tip": "Take a 10-minute break after each session.",
            }
            for task in created_tasks
        ],
    }, 201


@study_bp.post("/task/update")
@jwt_required()
def update_task():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    task_id = data.get("task_id")

    if not task_id:
        return {"error": "task_id is required"}, 400

    task = (
        StudyTask.query.join(StudyPlan, StudyTask.plan_id == StudyPlan.id)
        .filter(StudyTask.id == task_id, StudyPlan.user_id == user_id)
        .first()
    )

    if not task:
        return {"error": "task not found"}, 404

    if "status" in data:
        task.status = data["status"]
    db.session.commit()

    return {
        "status": "updated",
        "task": {
            "id": task.id,
            "subject": task.subject,
            "state": task.status,
        },
        "next_recommendation": "If tired, do 5 minutes of breathing before your next focus block.",
    }, 200


@study_bp.get("/recommendations")
@jwt_required()
def recommendations():
    return {
        "suggested_break_type": "box breathing",
        "next_task": "Review one high-priority subject",
        "estimated_time": "25 minutes",
        "relaxation_suggestion": "Try a short neck and shoulder release routine.",
    }, 200
