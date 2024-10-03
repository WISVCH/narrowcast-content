from waitress import serve
from . import app

serve(app,
      host='0.0.0.0',
      port=8080,
      connection_limit=500,
      threads=8,
      )