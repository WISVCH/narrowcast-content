from flask import Flask, render_template, request, abort
import logging
from logging import Formatter, FileHandler

app = Flask(__name__)
app.config.from_object('config')


@app.route('/buienradar')
def buienradar():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if lat is None or lon is None:
        abort(400, "Provide lat and lon parameters")

    try:
        lat = float(lat)
    except ValueError:
        abort(400, 'Cannot convert lat to float')

    try:
        lon = float(lon)
    except ValueError:
        abort(400, 'Cannot convert lon to float')

    return render_template('buienradar/index.jinja2', lat=lat, lon=lon)


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# Default port:
if __name__ == '__main__':
    app.run()
