from flask import Flask, request, make_response, jsonify
from datetime import datetime
from .database.conversation.conversation import (get_or_create_conversation, add_message_to_conversation, generate_rag_response)


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
    response_data = {
        "title": "Histórico",
        "subtitle": "Ver mais",
        "cards": []
    }

    return jsonify(response_data)


@app.route('/v1/send-question', methods=['POST'])
def send_chat_question():
    try:
        data = request.get_json()
        user_question = data.get('message')
        user_timestamp = data.get('timestamp')
        user_sender = data.get('sender')
        bot_sender = 'chatbot'
        doctor_id = 'doctor_001'
        conversation_id = data.get('conversation_id')

        if not user_question:
            return jsonify({"error": "The 'question' field is required."}), 400

        # add user message to mongo
        conversation = get_or_create_conversation(conversation_id=conversation_id, doctor_id=doctor_id)
        add_message_to_conversation(conversation["_id"], user_sender, user_question, user_timestamp, doctor_id)
        # call gemini passing the question
        bot_respose = generate_rag_response(user_question)
        # add gemini message to mongo
        current_timestamp = datetime.utcnow().isoformat() + "Z"
        add_message_to_conversation(conversation["_id"], bot_sender, bot_respose, current_timestamp, doctor_id)

        response_data = {
            "message": bot_respose,
            "sender": bot_sender,
            "timestamp": current_timestamp
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run()
