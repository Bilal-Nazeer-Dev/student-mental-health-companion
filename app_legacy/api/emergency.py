from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models import EmergencyFlag, User

emergency_bp = Blueprint("emergency", __name__)


@emergency_bp.get("/my-flags")
@jwt_required()
def my_flags():
    user_id = int(get_jwt_identity())
    rows = EmergencyFlag.query.filter_by(user_id=user_id).order_by(EmergencyFlag.created_at.desc()).all()
    return {
        "emergencies": [
            {
                "id": row.id,
                "severity": row.severity,
                "excerpt": row.excerpt,
                "status": row.status,
                "timestamp": row.created_at.isoformat(),
            }
            for row in rows
        ]
    }, 200


@emergency_bp.get("/admin/all")
@jwt_required()
def admin_all():
    user = User.query.get(int(get_jwt_identity()))
    if not user or not user.is_admin:
        return {"error": "forbidden"}, 403

    rows = EmergencyFlag.query.order_by(EmergencyFlag.created_at.desc()).limit(100).all()
    return {
        "emergencies": [
            {
                "id": row.id,
                "user_id": row.user_id,
                "severity": row.severity,
                "excerpt": row.excerpt,
                "status": row.status,
                "timestamp": row.created_at.isoformat(),
            }
            for row in rows
        ]
    }, 200
