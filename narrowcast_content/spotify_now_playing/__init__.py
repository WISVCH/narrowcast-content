import time
from datetime import datetime, timedelta

from flask import Blueprint, render_template, abort, request, current_app, redirect, session, url_for, json
import spotipy

spotify_now_playing = Blueprint('spotify_now_playing', __name__,
                                template_folder='templates', static_folder='static',
                                url_prefix='/spotify_now_playing')

API_BASE = 'https://accounts.spotify.com'
SCOPE = 'user-read-playback-state'

SHOW_DIALOG = False

token_info = {}
prev_result = None
prev_result_time = None


@spotify_now_playing.route("/authorize")
def authorize():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=current_app.config['SPOTIPY_CLIENT_ID'],
                                           client_secret=current_app.config['SPOTIPY_CLIENT_SECRET'],
                                           redirect_uri=current_app.config['SPOTIPY_REDIRECT_URI'], scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()

    return redirect(auth_url)


@spotify_now_playing.route("/")
def index():
    return render_template("spotify_now_playing/index.jinja2")


@spotify_now_playing.route("/currently_playing")
def currently_playing():
    global prev_result, prev_result_time

    if prev_result and prev_result_time and datetime.now() - prev_result_time < timedelta(seconds=4):
        return prev_result

    local_token_info, authorized = get_token()

    if authorized:
        sp = spotipy.Spotify(auth=local_token_info.get('access_token'))
        response = sp.currently_playing()
    else:
        response = None

    result = {'authorized': authorized}

    anything_playing = True if response else False

    if authorized:
        result['anything_playing'] = anything_playing

    if authorized and anything_playing:
        result['album'] = response['item']['album']['name']
        result['album_cover'] = response['item']['album']['images'][0]['url']
        result['artist'] = ', '.join([a['name'] for a in response['item']['artists']])
        result['title'] = response['item']['name']
        result['is_playing'] = response['is_playing']

    prev_result = result
    prev_result_time = datetime.now()

    return result


# authorization-code-flow Step 2.
# Have your application request refresh and access tokens;
# Spotify returns access and refresh tokens
@spotify_now_playing.route("/api_callback")
def api_callback():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=current_app.config['SPOTIPY_CLIENT_ID'],
                                           client_secret=current_app.config['SPOTIPY_CLIENT_SECRET'],
                                           redirect_uri=current_app.config['SPOTIPY_REDIRECT_URI'], scope=SCOPE)
    code = request.args.get('code')

    global token_info
    token_info = sp_oauth.get_access_token(code)

    return redirect(url_for('spotify_now_playing.index'))


# Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    global token_info

    # Checking if there is a token stored
    if token_info == {}:
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())

    is_token_expired = token_info.get('expires_at') - now < 60

    # Refreshing token if it has expired
    if is_token_expired:
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=current_app.config['SPOTIPY_CLIENT_ID'],
                                               client_secret=current_app.config['SPOTIPY_CLIENT_SECRET'],
                                               redirect_uri=current_app.config['SPOTIPY_REDIRECT_URI'], scope=SCOPE)
        token_info = sp_oauth.refresh_access_token(token_info.get('refresh_token'))

    token_valid = True
    return token_info, token_valid
