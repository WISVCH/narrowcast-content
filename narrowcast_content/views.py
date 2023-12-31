from flask import request, abort, render_template
from narrowcast_content import app


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
