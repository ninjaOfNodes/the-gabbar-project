from flask import Blueprint, request, jsonify, render_template, Response
from .ollama_utils import chat_with_model, is_code_request
import json
import os
import uuid
from datetime import datetime

main_bp = Blueprint('main', __name__)

CHAT_HISTORY_PATH = os.path.join(os.path.dirname(__file__), 'chat_history.json')

def load_chats():
    if not os.path.exists(CHAT_HISTORY_PATH):
        return {}
    try:
        with open(CHAT_HISTORY_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def save_chats(chats):
    with open(CHAT_HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(chats, f, ensure_ascii=False, indent=2)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/api/chats', methods=['GET'])
def get_chats():
    chats = load_chats()
    chat_list = [
        {'id': cid, 'name': c['name'], 'created_at': c.get('created_at', '')} for cid, c in chats.items()
    ]
    chat_list.sort(key=lambda c: c['created_at'], reverse=True)
    return jsonify(chat_list)

@main_bp.route('/api/chats', methods=['POST'])
def create_chat():
    data = request.get_json()
    first_message = data.get('message', '').strip()
    if not first_message:
        return jsonify({'error': 'First message required'}), 400
    chat_id = str(uuid.uuid4())
    chats = load_chats()
    now = datetime.utcnow().isoformat()
    chats[chat_id] = {
        'name': first_message[:40],
        'created_at': now,
        'history': [{'role': 'user', 'content': first_message, 'timestamp': now}]
    }
    save_chats(chats)
    return jsonify({'id': chat_id, 'name': first_message[:40], 'created_at': now})

@main_bp.route('/api/chats/<chat_id>', methods=['GET'])
def get_chat_history(chat_id):
    chats = load_chats()
    chat = chats.get(chat_id)
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    # Sort by timestamp (newest first)
    history = sorted(chat['history'], key=lambda m: m.get('timestamp', ''), reverse=True)
    return jsonify(history)

@main_bp.route('/api/chats/<chat_id>/message', methods=['POST'])
def chat(chat_id):
    data = request.get_json()
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message required'}), 400

    chats = load_chats()
    chat = chats.get(chat_id)
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404

    # Determine model based on content
    if is_code_request(message):
        model = 'codellama'
    else:
        model = 'llama2'

    # Only append if not a duplicate of the last user message
    if not (chat['history'] and chat['history'][-1]['role'] == 'user' and chat['history'][-1]['content'] == message):
        chat['history'].append({'role': 'user', 'content': message, 'timestamp': datetime.utcnow().isoformat()})
        save_chats(chats)

    def generate_and_save():
        bot_response = ''
        # Full history as context
        history_context = chat['history']

        for chunk in chat_with_model(history_context, model=model, stream=True):
            try:
                data = json.loads(chunk)
                content = data.get('message', {}).get('content')
                if content:
                    bot_response += content
            except Exception:
                pass
            yield chunk + '\n'

        if bot_response.strip():
            chat['history'].append({'role': 'bot', 'content': bot_response.strip(), 'timestamp': datetime.utcnow().isoformat()})
            save_chats(chats)

    return Response(generate_and_save(), mimetype='text/plain')

@main_bp.route('/api/chats/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    chats = load_chats()
    if chat_id in chats:
        del chats[chat_id]
        save_chats(chats)
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Chat not found'}), 404
