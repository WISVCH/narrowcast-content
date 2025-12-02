from flask import Blueprint, render_template, abort, request, current_app
import requests
import random

from narrowcast_content import cache

shuttr = Blueprint(
    'shuttr',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/shuttr'
)

@shuttr.route('/')
@cache.cached(timeout=10)
def show():
    """
    Render a random shuttr album
    """
    albums = fetch_albums()
    weights = [0.8**i for i in range(len(albums))]
    selected_album = random.choices(albums, weights=weights, k=1)[0]
    album = fetch_album(selected_album['slug'])
    seed = random.randrange(2**52)

    return render_template('shuttr/index.jinja2', album=album, base_domain=current_app.config['SHUTTR_DOMAIN'], seed=seed)

@cache.memoize(15*60)
def fetch_album(slug):
    r = requests.get(current_app.config['SHUTTR_DOMAIN'] + "/api/albums/" + slug)
    return r.json()

@cache.cached(timeout=10*60)
def fetch_albums():
    r = requests.get(current_app.config['SHUTTR_DOMAIN'] + "/api/albums")
    return r.json()[:20]