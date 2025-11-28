from logging.config import dictConfig
from pathlib import Path

from flask import Flask, request, abort, session

from narrowcast_content.buienradar_graph import buienradar_graph
from narrowcast_content.cache import cache
from narrowcast_content.combine import combine
from narrowcast_content.image import image
from narrowcast_content.pub_timer import pub_timer
from narrowcast_content.spotify_now_playing import spotify_now_playing
from narrowcast_content.upcoming_activities import upcoming_activities
from narrowcast_content.shuttr import shuttr

app = Flask(__name__)
app.config.from_object('config')
app.config.from_prefixed_env()

cache.init_app(app)

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {"level": "WARN", "handlers": ["console"]},
    }
)

# Add all the blueprints
app.register_blueprint(buienradar_graph)
app.register_blueprint(spotify_now_playing)
app.register_blueprint(combine)
app.register_blueprint(image)
app.register_blueprint(pub_timer)
app.register_blueprint(upcoming_activities)
app.register_blueprint(shuttr)

# Parse the tokens
tokens = app.config['TOKENS'].split()

app.config['DATA_DIR'] = Path(app.config['DATA_PATH'])
app.config['DATA_DIR'].mkdir(parents=True, exist_ok=True)

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
