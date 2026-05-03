from flask import Flask, render_template
from config import Config
from models import init_db
from services.gemini_service import init_gemini


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    init_db()
    init_gemini()

    from routes.auth import auth_bp
    from routes.chat import chat_bp
    from routes.mood import mood_bp
    from routes.schedule import schedule_bp
    from routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(mood_bp, url_prefix='/api/mood')
    app.register_blueprint(schedule_bp, url_prefix='/api/schedule')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

    return app

app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/app')
def app_page():
    return render_template('app.html')


app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)
