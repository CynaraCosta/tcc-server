from flask import Flask, request, make_response, jsonify
from datetime import datetime


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

        if not user_question:
            return jsonify({"error": "The 'question' field is required."}), 400

        # add user message to mongo
        # call gemini passing the question
        # add gemini message to mongo

        current_timestamp = datetime.utcnow().isoformat() + "Z"
        response_data = {
            "message": f"Response coming from the RAG for the question: '{user_question}'",
            "sender": "chatbot",
            "timestamp": current_timestamp
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run()
