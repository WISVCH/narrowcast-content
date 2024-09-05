from waitress import serve
from . import app
from paste.translogger import TransLogger

serve(TransLogger(app, setup_console_handler=False),
      host='0.0.0.0',
      port=8080,
      connection_limit=500,
      threads=8,
      )