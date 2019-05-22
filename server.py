from log import log

import json
import os

import eventlet
import socketio


# -----------------------------------------------------------------------------
#                                                          Initialize Socket.io
# -----------------------------------------------------------------------------
sio = socketio.Server()

# Try to load the list of static files that the server should reveal
static_files_file = 'config/static_files.json'
static_files = None

try:
    with open(static_files_file) as f:
        static_files = json.load(f)
except IOError:
    log('server.py', f'Failed to open {static_files_file}', 'fatal error')
    exit()
except json.decoder.JSONDecodeError:
    log(
        'server.py',
        f'Failed to parse {static_files_file} (empty?)',
        'warning'
    )

# Define the app itself
app = socketio.WSGIApp(sio, static_files=static_files)


# -----------------------------------------------------------------------------
#                                                                          Main
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    port = 3000

    # Check whether a port is defined as an envvar (e.g. for Heroku)
    if 'PORT' in os.environ.keys():
        port = int(os.environ['PORT'])

    # Actually run the server
    log('server.py', 'Starting server')
    eventlet.wsgi.server(eventlet.listen(('', port)), app)
