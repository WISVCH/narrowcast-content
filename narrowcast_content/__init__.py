import logging
from logging import Formatter, FileHandler

from flask import Flask, request, abort, session

from narrowcast_content.buienradar_graph import buienradar_graph
from narrowcast_content.cache import cache
from narrowcast_content.combine import combine
from narrowcast_content.image import image
from narrowcast_content.pub_timer import pub_timer
from narrowcast_content.spotify_now_playing import spotify_now_playing

app = Flask(__name__)
app.config.from_object('config')
app.config.from_prefixed_env()

cache.init_app(app)

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# Add all the blueprints
app.register_blueprint(buienradar_graph)
app.register_blueprint(spotify_now_playing)
app.register_blueprint(combine)
app.register_blueprint(image)
app.register_blueprint(pub_timer)

# Parse the tokens
tokens = app.config['TOKENS'].split()


def exclude_from_token(func):
    func._exclude_from_token = True
    return func


@app.route('/health')
@exclude_from_token
def health():
    return "slay"


@app.before_request
def check_auth():
    """
    Checks if the client sends a token, and if the token is valid.
    Puts the token in the session so that it has to be provided only once.
    """

    if request.endpoint in app.view_functions:
        view_func = app.view_functions[request.endpoint]
        check_token = not hasattr(view_func, '_exclude_from_token')
        if not check_token:
            return

    if 'token' not in request.args and 'token' not in session:
        abort(401, "Unauthorized")

    if 'token' in request.args:
        session['token'] = request.args['token']

    if session['token'] not in tokens:
        abort(401, "Unauthorized")
