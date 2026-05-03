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

    if not subjects:
        return jsonify({'error': 'Please enter at least one subject'}), 400

    plan = generate_study_plan(subjects, deadlines, str(available_hours), break_style)
    user_id = session['user_id']
    save_schedule(user_id, plan, subjects)

    return jsonify({'schedule': plan}), 200


@schedule_bp.route('/latest', methods=['GET'])
@login_required
def latest():
    user_id = session['user_id']
    schedule = get_latest_schedule(user_id)
    return jsonify({'schedule': schedule}), 200
