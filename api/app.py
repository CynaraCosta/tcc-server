from flask import Flask, request, make_response, jsonify
from datetime import datetime
from .database.conversation.conversation import (
    get_or_create_conversation, add_message_to_conversation, generate_rag_response, get_conversations, get_messages_by_conversation_id)


app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>ChatAI TCC - Cynara Costa</h1>'


@app.route('/v1/home', methods=['GET'])
def get_widgets():
    response_data = {
        "widgets": [
            {
                "id": "explorerCarousel",
                "state": "loading",
                "path": "/v1/explorer-carousel",
                "data": {},
                "style": {
                    "bounds": {
                        "top": "soma_spacing_inline_md",
                        "left": "soma_spacing_inline_xs",
                        "right": "soma_spacing_inline_xs"
                    }
                }
            },
            {
                "id": "historyCards",
                "state": "loading",
                "path": "/v1/history-cards",
                "data": {},
                "style": {
                    "bounds": {
                        "top": "soma_spacing_inline_md",
                        "left": "soma_spacing_inline_xs",
                        "right": "soma_spacing_inline_xs"
                    }
                }
            }
        ]
    }

    return jsonify(response_data)


@app.route('/v1/explorer-carousel', methods=['GET'])
def get_explorer_carousel():
    response_data = {
        'title': 'Explorar',
        'cards': [
            {
                "title": "Chat AI",
                "subtitle": "Start New Conversation",
                "icon": "message",
                "deeplink": "/chat"
            }
        ]
    }

    return jsonify(response_data)


@app.route('/v1/history-cards', methods=['GET'])
def get_history_cards():
    cards = get_conversations()
    subtitle = ''
    selected_cards = []

    if len(cards) > 3:
        subtitle = 'Ver mais'

    if len(cards) <= 3:
        selected_cards = cards 
    else:
        selected_cards = cards[-3:]

    response_data = {
        "title": "Histórico",
        "subtitle": subtitle,
        "cards": selected_cards
    }

    return jsonify(response_data)

@app.route('/v1/get-conversation', methods=['GET'])
def get_conversation():
    data = request.get_json()
    conversation_id = data.get('conversationId')

    messages = get_messages_by_conversation_id(conversation_id=conversation_id)

    formated_messages = [
        {
            "text": message['message'],
            "isUser": message["sender"] == "doctor", 
            "conversationId": conversation_id,
        } for message in messages
    ]
    response = {
        "messages": formated_messages
    }
    return jsonify(response)


@app.route('/v1/send-question', methods=['POST'])
def send_chat_question():
    try:
        data = request.get_json()
        user_question = data.get('message')
        user_timestamp = data.get('timestamp')
        user_sender = data.get('sender')
        bot_sender = 'chatbot'
        doctor_id = 'doctor_001'
        conversation_id = request.args.get('conversationId')

        if not user_question:
            return jsonify({"error": "The 'question' field is required."}), 400

        
        conversation = get_or_create_conversation(
            conversation_id=conversation_id, doctor_id=doctor_id)
        add_message_to_conversation(
            conversation["_id"], user_sender, user_question, user_timestamp, doctor_id)
        
        bot_respose = generate_rag_response(user_question)
        
        current_timestamp = datetime.utcnow().isoformat() + "Z"
        add_message_to_conversation(
            conversation["_id"], bot_sender, bot_respose, current_timestamp, doctor_id)

        response_data = {
            "_id": conversation["_id"],
            "message": bot_respose,
            "sender": bot_sender,
            "timestamp": current_timestamp
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run()
