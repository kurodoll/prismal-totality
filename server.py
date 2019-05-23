from log import log
from Game import Manager

import json
import os

import eventlet
import socketio


# -----------------------------------------------------------------------------
#                                                                    Game Setup
# -----------------------------------------------------------------------------
manager = Manager.Manager()

# Message Of The Day
motd = 'MOTD: Welcome to v0.000...001 of Prismal Totality!'


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
#                                                         Socket.io Interaction
# -----------------------------------------------------------------------------
clients = {}  # A dictionary of clients, including ones that have disconnected

# When a client connects, begin to store their information
@sio.on('connect')
def connect(sid, env):
    log('server.py', f'Connected: {sid}', 'debug')

    clients[sid] = {
        'online': True
    }

# When a client disconnects, mark them as such
@sio.on('disconnect')
def disconnect(sid):
    log('server.py', f'Disconnected: {sid}', 'debug')

    clients[sid]['online'] = False
    clients[sid]['logged in'] = False

    manager.removePlayer(sid)
    manager.emitUpdates(sio)

# A user has logged in
@sio.on('login')
def login(sid, username):
    log('server.py', f'Login of {username}')

    clients[sid]['username'] = username
    clients[sid]['logged in'] = True

    manager.addPlayer(sid, username)
    manager.emitUpdates(sio)

    sio.emit('login success', room=sid)
    sio.emit('msg', motd, room=sid)

# A user has requested the data of the level they're on.
# After they're sent the level, they'll want to recieve updates for
#     anything that happens on the level, so they need to be "linked" with the
#     level as well
@sio.on('request present level')
def request_present_level(sid):
    level = manager.getPresentLevel(sid)

    if level:
        # Remove inactive entities first
        for e in level['entities'][:]:
            if not e['active']:
                level['entities'].remove(e)

        # Send the level to the client
        sio.emit('present level', level, room=sid)
        manager.linkPlayerToLevel(sid, level['id'])

        log(
            'server.py',
            f'Sent level {level["id"]} to {clients[sid]["username"]}',
            'debug'
        )

# Handles a user action
@sio.on('action')
def action(sid, action_type, details):
    manager.action(sid, action_type, details)

    # Emit any changes that the action might have caused
    manager.emitUpdates(sio)


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
