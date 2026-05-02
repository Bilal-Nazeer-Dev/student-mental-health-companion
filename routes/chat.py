from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from models import get_or_create_session, update_session_messages
from services.gemini_service import chat_with_gemini

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    if len(message) > 2000:
        return jsonify({'error': 'Message too long (max 2000 characters)'}), 400

    user_id = session['user_id']
    session_id, history = get_or_create_session(user_id)

    result = chat_with_gemini(message, history)

    # Append new exchange to history
    history.append({'role': 'user', 'content': message})
    history.append({'role': 'assistant', 'content': result['response']})
    update_session_messages(session_id, history)

    return jsonify({
        'response': result['response'],
        'emotion': result.get('emotion', 'neutral'),
        'emergency': result.get('emergency', False)
    }), 200


@chat_bp.route('/history', methods=['GET'])
@login_required
def get_history():
    user_id = session['user_id']
    _, history = get_or_create_session(user_id)
    return jsonify({'history': history}), 200


@chat_bp.route('/clear', methods=['POST'])
@login_required
def clear_history():
    user_id = session['user_id']
    session_id, _ = get_or_create_session(user_id)
    update_session_messages(session_id, [])
    return jsonify({'message': 'Conversation cleared'}), 200
