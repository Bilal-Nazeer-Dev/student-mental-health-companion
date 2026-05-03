from datetime import datetime

from app.core.extensions import db


class BaseModel:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class User(db.Model, BaseModel):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    age_group = db.Column(db.String(50), nullable=True)
    consent_agreed = db.Column(db.Boolean, default=False, nullable=False)
    emergency_contact = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)


class ChatSession(db.Model, BaseModel):
    __tablename__ = "chat_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False, default="Support Chat")


class ChatMessage(db.Model, BaseModel):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("chat_sessions.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    flagged = db.Column(db.Boolean, default=False, nullable=False)


class MoodEntry(db.Model, BaseModel):
    __tablename__ = "mood_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    emotions_csv = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)


class StudyPlan(db.Model, BaseModel):
    __tablename__ = "study_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False, default="Weekly Plan")


class StudyTask(db.Model, BaseModel):
    __tablename__ = "study_tasks"

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("study_plans.id"), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    deadline = db.Column(db.String(40), nullable=True)
    priority = db.Column(db.String(20), nullable=False, default="medium")
    status = db.Column(db.String(20), nullable=False, default="pending")
    duration_minutes = db.Column(db.Integer, nullable=False, default=50)


class RelaxationSession(db.Model, BaseModel):
    __tablename__ = "relaxation_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    exercise_type = db.Column(db.String(40), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)


class EmergencyFlag(db.Model, BaseModel):
    __tablename__ = "emergency_flags"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("chat_sessions.id"), nullable=True)
    severity = db.Column(db.String(20), nullable=False)
    excerpt = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
