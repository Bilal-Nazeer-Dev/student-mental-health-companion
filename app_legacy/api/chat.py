from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.core.extensions import db
from app.models import ChatMessage, ChatSession, EmergencyFlag
from app.services.gemini_client import get_chat_response
from app.services.safety import detect_emergency, emergency_support_message

chat_bp = Blueprint("chat", __name__)


@chat_bp.post("/message")
@jwt_required()
def send_message():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    message = (data.get("message") or "").strip()

    if not message:
        return {"error": "message is required"}, 400

    session_id = data.get("session_id")
    if session_id:
        chat_session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
    else:
        chat_session = None

    if not chat_session:
        chat_session = ChatSession(user_id=user_id)
        db.session.add(chat_session)
        db.session.flush()

    user_msg = ChatMessage(session_id=chat_session.id, role="user", content=message)
    db.session.add(user_msg)

    emergency, severity = detect_emergency(message)

    if emergency:
        ai_text = emergency_support_message()
        db.session.add(
            EmergencyFlag(
                user_id=user_id,
                session_id=chat_session.id,
                severity=severity,
                excerpt=message[:500],
            )
        )
    else:
        history = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(ChatMessage.id.asc()).all()
        context = [{"role": row.role, "content": row.content} for row in history]
        ai_text = get_chat_response(message, context)

    ai_msg = ChatMessage(
        session_id=chat_session.id,
        role="assistant",
        content=ai_text,
        flagged=emergency,
    )
    db.session.add(ai_msg)
    db.session.commit()

    return {
        "session_id": chat_session.id,
        "ai_response": ai_text,
        "detected_issues": ["emergency"] if emergency else [],
        "recommended_action": "seek_support" if emergency else "continue_chat",
    }, 200


@chat_bp.get("/history")
@jwt_required()
def history():
    user_id = int(get_jwt_identity())
    session_id = request.args.get("session_id", type=int)

    if not session_id:
        return {"error": "session_id is required"}, 400

    session = ChatSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return {"error": "session not found"}, 404

    rows = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.id.asc()).all()
    return {
        "messages": [
            {
                "id": row.id,
                "role": row.role,
                "content": row.content,
                "flagged": row.flagged,
                "timestamp": row.created_at.isoformat(),
            }
            for row in rows
        ]
    }, 200
