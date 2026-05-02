from flask import Blueprint, jsonify, session
from routes.auth import login_required
from models import get_mood_logs, get_checkin_streak, get_checkin_count
from services.mood_analyzer import analyze_mood_trends, get_emotion_distribution, format_chart_data
from services.gemini_service import generate_weekly_insight

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@login_required
def stats():
    user_id = session['user_id']

    logs_30 = get_mood_logs(user_id, 30)
    logs_7 = get_mood_logs(user_id, 7)

    analysis = analyze_mood_trends(logs_30)
    chart_data = format_chart_data(logs_30)
    emotion_dist = get_emotion_distribution(logs_30)
    streak = get_checkin_streak(user_id)
    checkins_7 = get_checkin_count(user_id, 7)

    weekly_insight = generate_weekly_insight(logs_7, checkins_7)

    return jsonify({
        'mood_average': analysis.get('average', 0),
        'mood_trend': analysis.get('trend', 'no_data'),
        'streak_alert': analysis.get('streak_alert', False),
        'insights': analysis.get('insights', []),
        'chart_data': chart_data,
        'emotion_distribution': emotion_dist,
        'checkin_streak': streak,
        'checkins_this_week': checkins_7,
        'total_mood_logs': analysis.get('total_entries', 0),
        'weekly_insight': weekly_insight
    }), 200
