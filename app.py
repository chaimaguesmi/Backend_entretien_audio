from chalice import Chalice, Response

from chalicelib.modules.controller import AudioResponseController, ConversationController

# Initialisation de l'application Chalice
app = Chalice(app_name='careere-audio-responses')

# Configuration
app.debug = True

# Middleware CORS
@app.middleware('cors')
def add_cors_header(event, get_response):
    response = get_response(event)
    response.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    })
    return response

# Gestion des erreurs globales
@app.middleware('http')
def handle_errors(event, get_response):
    try:
        response = get_response(event)
        return response
    except Exception as e:
        return Response(
            body={'error': str(e)},
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )

# Options pour les requêtes CORS

@app.route('/{proxy+}', methods=['OPTIONS'])
def options_handler(proxy):
    return Response(
        body='',
        status_code=200,
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Max-Age': '86400'
        }
    )

# Initialisation des controllers
audio_controller = AudioResponseController(app)
conversation_controller = ConversationController(app)
# Point d'entrée pour les tests locaux
if __name__ == '__main__':
    app.run(debug=True)