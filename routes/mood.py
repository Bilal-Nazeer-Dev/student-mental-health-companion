from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from models import log_mood, get_mood_logs, get_latest_mood
from services.gemini_service import detect_emotion
from services.mood_analyzer import analyze_mood_trends, get_emotion_distribution, format_chart_data

mood_bp = Blueprint('mood', __name__)

MOOD_LABELS = {1: 'Very Bad', 2: 'Bad', 3: 'Okay', 4: 'Good', 5: 'Excellent'}
MOOD_EMOJIS = {1: '😞', 2: '😕', 3: '😐', 4: '😊', 5: '😄'}


@mood_bp.route('/log', methods=['POST'])
@login_required
def log():
    data = request.get_json() or {}
    score = data.get('score')
    description = data.get('description', '').strip()

    if score is None or not isinstance(score, int) or score not in range(1, 6):
        return jsonify({'error': 'Score must be an integer between 1 and 5'}), 400

    emotion_tag = detect_emotion(description) if description else 'neutral'
    user_id = session['user_id']
    log_id = log_mood(user_id, score, description, emotion_tag)

    return jsonify({
        'message': 'Mood logged successfully',
        'id': log_id,
        'score': score,
        'label': MOOD_LABELS[score],
        'emoji': MOOD_EMOJIS[score],
        'emotion_tag': emotion_tag
    }), 201


@mood_bp.route('/logs', methods=['GET'])
@login_required
def get_logs():
    days = request.args.get('days', 30, type=int)
    user_id = session['user_id']
    logs = get_mood_logs(user_id, days)
    analysis = analyze_mood_trends(logs)
    chart_data = format_chart_data(logs)
    emotion_dist = get_emotion_distribution(logs)

    return jsonify({
        'logs': logs,
        'analysis': analysis,
        'chart_data': chart_data,
        'emotion_distribution': emotion_dist
    }), 200


@mood_bp.route('/latest', methods=['GET'])
@login_required
def latest():
    user_id = session['user_id']
    log = get_latest_mood(user_id)
    if log:
        log['label'] = MOOD_LABELS.get(log['score'], 'Unknown')
        log['emoji'] = MOOD_EMOJIS.get(log['score'], '😐')
    return jsonify({'latest': log}), 200
