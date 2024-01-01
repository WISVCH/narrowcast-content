import logging
from logging import Formatter, FileHandler

from flask import Flask, request, abort, session

from narrowcast_content.buienradar_graph import buienradar_graph
from narrowcast_content.combine import combine
from narrowcast_content.image import image
from narrowcast_content.pub_timer import pub_timer
from narrowcast_content.spotify_now_playing import spotify_now_playing

app = Flask(__name__)
app.config.from_object('config')
app.config.from_prefixed_env()

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


@app.before_request
def check_auth():
    """
    Checks if the client sends a token, and if the token is valid.
    Puts the token in the session so that it has to be provided only once.
    """
    if 'token' not in request.args and 'token' not in session:
        abort(401, "Unauthorized")

    if 'token' in request.args:
        session['token'] = request.args['token']

    if session['token'] not in tokens:
        abort(401, "Unauthorized")


@app.after_request
def apply_caching(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response
