
from chalice import Chalice
from chalicelib.modules import schemas
from chalicelib.modules.controller import api
from pymongoose import methods
app = Chalice(app_name='careere-audio-responses')

app.debug = True

app.experimental_feature_flags.update(['BLUEPRINTS'])

app.register_blueprint(api)

if __name__ == '__main__':
    app.run(debug=True)

def handler(event, context):
    return app(event, context)