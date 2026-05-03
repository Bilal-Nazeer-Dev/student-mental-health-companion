from flask import Flask
from flask_cors import CORS

from app.api.auth import auth_bp
from app.api.chat import chat_bp
from app.api.dashboard import dashboard_bp
from app.api.emergency import emergency_bp
from app.api.mood import mood_bp
from app.api.relaxation import relaxation_bp
from app.api.study import study_bp
from app.core.config import Config
from app.core.extensions import db, jwt, migrate


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    register_blueprints(app)

    @app.get("/health")
    def health_check():
        return {"status": "ok", "service": "student-companion-api"}, 200

    with app.app_context():
        db.create_all()

    return app


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(mood_bp, url_prefix="/api/mood")
    app.register_blueprint(study_bp, url_prefix="/api/study")
    app.register_blueprint(relaxation_bp, url_prefix="/api/relaxation")
    app.register_blueprint(emergency_bp, url_prefix="/api/emergency")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
