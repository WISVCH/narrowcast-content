import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Secret key for session management. You can generate random strings here:
SECRET_KEY = 'CHANGE_ME'

SPOTIPY_CLIENT_ID='CHANGE_ME'
SPOTIPY_CLIENT_SECRET='CHANGE_ME'
SPOTIPY_REDIRECT_URI='http://localhost:5000/spotify_now_playing/api_callback'

PUB_GOOGLE_CALENDAR_ID='CHANGE_ME'
PUB_GOOGLE_CALENDAR_API_KEY='CHANGE_ME'
TOKENS='CHANGE_ME CHANGE_ME_TOO'
