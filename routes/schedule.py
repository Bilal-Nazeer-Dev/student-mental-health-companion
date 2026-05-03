from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from models import save_schedule, get_latest_schedule
from services.gemini_service import generate_study_plan

schedule_bp = Blueprint('schedule', __name__)


@schedule_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    data = request.get_json() or {}
    subjects = data.get('subjects', '').strip()
    deadlines = data.get('deadlines', 'No specific deadlines').strip()
    available_hours = data.get('available_hours', '4')
    break_style = data.get('break_style', 'Pomodoro (25 min study, 5 min break)')
    energy_level = data.get('energy_level', 'Medium')
    learning_style = data.get('learning_style', 'Visual')

    if not subjects:
        return jsonify({'error': 'Please enter at least one subject'}), 400

    from models import get_latest_mood
    user_id = session['user_id']
    latest_m = get_latest_mood(user_id)
    mood_tag = latest_m['emotion_tag'] if latest_m else "Neutral"

    plan = generate_study_plan(subjects, deadlines, str(available_hours), break_style, energy_level, learning_style, mood_tag)
    user_id = session['user_id']
    save_schedule(user_id, plan, subjects)

    return jsonify({'schedule': plan}), 200


@schedule_bp.route('/latest', methods=['GET'])
@login_required
def latest():
    user_id = session['user_id']
    schedule = get_latest_schedule(user_id)
    return jsonify({'schedule': schedule}), 200
