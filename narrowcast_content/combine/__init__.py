from flask import Blueprint, render_template, abort, request

combine = Blueprint('combine', __name__,
                    template_folder='templates', static_folder='static',
                    url_prefix='/combine')


@combine.route('/')
def show():
    """
    Parse the URLs and sizes that are in the query parameters, and render the urls with those sizes using iframes.
    """
    url_sizes = []
    for i in range(100):
        url_key = 'url' + str(i)
        size_key = 'size' + str(i)
        if url_key in request.args and size_key in request.args:
            url_sizes.append((request.args[url_key], request.args[size_key]))
        elif i == 0:
            abort(400, "Provide at least url0 and size0")
        else:
            break

    return render_template('combine/index.jinja2', url_sizes=url_sizes)
