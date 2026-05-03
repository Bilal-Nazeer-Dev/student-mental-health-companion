from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from passlib.hash import pbkdf2_sha256

from app.core.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()

    if not email or not password or not name:
        return {"error": "email, password, and name are required"}, 400

    if User.query.filter_by(email=email).first():
        return {"error": "email already registered"}, 409

    user = User(
        email=email,
        password_hash=pbkdf2_sha256.hash(password),
        name=name,
        age_group=data.get("age_group"),
        consent_agreed=bool(data.get("consent_agreed", False)),
        emergency_contact=data.get("emergency_contact"),
    )
    db.session.add(user)
    db.session.commit()

    access = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "consent_agreed": user.consent_agreed,
        },
        "access_token": access,
        "refresh_token": refresh,
    }, 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not pbkdf2_sha256.verify(password, user.password_hash):
        return {"error": "invalid credentials"}, 401

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "consent_agreed": user.consent_agreed,
        },
        "access_token": create_access_token(identity=str(user.id)),
        "refresh_token": create_refresh_token(identity=str(user.id)),
    }, 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    return {"access_token": create_access_token(identity=user_id)}, 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return {"error": "user not found"}, 404

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "age_group": user.age_group,
        "consent_agreed": user.consent_agreed,
        "emergency_contact": user.emergency_contact,
    }, 200


@auth_bp.post("/consent-update")
@jwt_required()
def consent_update():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return {"error": "user not found"}, 404

    data = request.get_json() or {}
    user.consent_agreed = bool(data.get("consent_agreed", user.consent_agreed))
    if "emergency_contact" in data:
        user.emergency_contact = data.get("emergency_contact")
    db.session.commit()

    return {"status": "updated", "consent_agreed": user.consent_agreed}, 200
