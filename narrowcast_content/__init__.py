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

import narrowcast_content.views
