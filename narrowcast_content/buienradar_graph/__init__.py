from flask import Blueprint, render_template, abort, request

buienradar_graph = Blueprint('buienradar_graph', __name__,
                             template_folder='templates', static_folder='static',
                             url_prefix='/buienradar_graph')


@buienradar_graph.route('/')
def show():
    """
    Parse the lat and lon parameters, and render the buienradar graph, with those coordinates.
    :return:
    """
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

    return render_template('buienradar_graph/index.jinja2', lat=lat, lon=lon)
