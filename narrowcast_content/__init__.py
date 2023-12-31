from flask import Flask, render_template, request, abort
import logging
from logging import Formatter, FileHandler

app = Flask(__name__)
app.config.from_object('config')

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

from narrowcast_content.buienradar_graph import buienradar_graph

app.register_blueprint(buienradar_graph)

from narrowcast_content.spotify_now_playing import spotify_now_playing

app.register_blueprint(spotify_now_playing)

from narrowcast_content.combine import combine

app.register_blueprint(combine)
