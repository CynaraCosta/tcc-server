from flask import Flask, request, make_response, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Hello world!</h1>'


@app.route('/hello')
def hello():
    response = make_response('Hello world\n')
    response.status_code = 202
    response.headers['content-type'] = 'text/plain'
    return response


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
                "deeplink": "/chatia"
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
