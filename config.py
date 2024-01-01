import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = False

# Secret key for session management.
SECRET_KEY = 'CHANGE_ME'

# Spotify API credentials.
SPOTIPY_CLIENT_ID = 'CHANGE_ME'
SPOTIPY_CLIENT_SECRET = 'CHANGE_ME'
SPOTIPY_REDIRECT_URI = 'CHANGE_ME'

# /Pub Calendar information.
PUB_GOOGLE_CALENDAR_ID = 'CHANGE_ME'
PUB_GOOGLE_CALENDAR_API_KEY = 'CHANGE_ME'

# Tokens that can be used to access everything.
TOKENS = 'CHANGE_ME CHANGE_ME_TOO'
