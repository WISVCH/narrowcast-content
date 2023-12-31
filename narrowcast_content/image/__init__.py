from flask import Blueprint, render_template, abort, request

image = Blueprint('image', __name__,
                    template_folder='templates', static_folder='static',
                    url_prefix='/image')


@image.route('/')
def show():
    if 'url' not in request.args:
        abort(400, "Provide a url")

    return render_template('image/index.jinja2', url=request.args.get('url'))
