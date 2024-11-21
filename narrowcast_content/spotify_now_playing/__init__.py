import logging
import pickle
import time

import spotipy
from flask import Blueprint, render_template, request, current_app, redirect, url_for

from narrowcast_content import cache

spotify_now_playing = Blueprint('spotify_now_playing', __name__,
                                template_folder='templates', static_folder='static',
                                url_prefix='/spotify_now_playing')

API_BASE = 'https://accounts.spotify.com'
SCOPE = 'user-read-playback-state'

SHOW_DIALOG = False

token_file = 'spotify_token.pickle'

token_info = {}

_LOGGER = logging.getLogger(__name__)

@spotify_now_playing.route("/authorize")
def authorize():
    """
    Redirect to spotify to get a token.
    """
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=current_app.config['SPOTIPY_CLIENT_ID'],
                                           client_secret=current_app.config['SPOTIPY_CLIENT_SECRET'],
                                           redirect_uri=current_app.config['SPOTIPY_REDIRECT_URI'], scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()

    return redirect(auth_url)


@spotify_now_playing.route("/")
def index():
    """
    Render the player page.
    """
    return render_template("spotify_now_playing/index.jinja2", initial_data=currently_playing())


@spotify_now_playing.route("/currently_playing")
@cache.cached(timeout=4)
def currently_playing():
    """
    Get the song that is currently playing, if anything is playing.
    This is cached for 4 seconds.
    """

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

    return result


@spotify_now_playing.route("/api_callback")
def api_callback():
    """
    Spotify callback. After getting the code, it will get a token and stroke it globally.
    :return:
    """
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=current_app.config['SPOTIPY_CLIENT_ID'],
                                           client_secret=current_app.config['SPOTIPY_CLIENT_SECRET'],
                                           redirect_uri=current_app.config['SPOTIPY_REDIRECT_URI'], scope=SCOPE)
    code = request.args.get('code')

    global token_info
    token_info = sp_oauth.get_access_token(code)

    # Store token in file
    with current_app.config['DATA_DIR'].joinpath(token_file).open('wb') as f:
        pickle.dump(token_info, f)

    return redirect(url_for('spotify_now_playing.index'))


def get_token():
    """
    Checks to see if token is valid and gets a new token if not.
    """
    token_valid = False
    global token_info

    # Checking if there is a token stored in a file
    if token_info == {} and current_app.config['DATA_DIR'].joinpath(token_file).is_file():
        try:
            with current_app.config['DATA_DIR'].joinpath(token_file).open('rb') as f:
                token_info = pickle.load(f)
        except:
            token_info = {}

    # Checking if there is a token stored
    if token_info == {}:
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())

    is_token_expired = token_info.get('expires_at') - now < 60

    try:
        # Refreshing token if it has expired
        if is_token_expired:
            # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
            sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=current_app.config['SPOTIPY_CLIENT_ID'],
                                                   client_secret=current_app.config['SPOTIPY_CLIENT_SECRET'],
                                                   redirect_uri=current_app.config['SPOTIPY_REDIRECT_URI'], scope=SCOPE)
            token_info = sp_oauth.refresh_access_token(token_info.get('refresh_token'))

            # Store toke in file
            with current_app.config['DATA_DIR'].joinpath(token_file).open('wb') as f:
                pickle.dump(token_info, f)

        token_valid = True
    except spotipy.oauth2.SpotifyOauthError:
        _LOGGER.exception('')
        token_valid = False

    return token_info, token_valid
