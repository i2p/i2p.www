#!env/bin/python
from i2p2www import app
import os

# This code enable hot-reload of content and eliminates the
# need of restarting the server for changes in html files,
# most likely python files as well.
# To enable this, run with:
# DEV=whatever ./runserver.py
is_development = False
try:
  os.environ['DEV']
  is_development = True
except KeyError:
  pass


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=is_development)
