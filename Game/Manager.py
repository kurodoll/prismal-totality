from log import log

from . import WorldManager
from . import EntityManager


# Manages the entire game world
class Manager:
    def __init__(self):
        self.WorldManager = WorldManager.WorldManager()
        self.EntityManager = EntityManager.EntityManager()

        self.players = {}
        self.links = {}  # Links from levels to players to be updated

    def addPlayer(self, sid, username):
        # Create an entity for the player
        player_entity = self.EntityManager.addNew()

        # The player entity needs a sprite
        self.EntityManager.addComponent(
            player_entity,
            'sprite',
            {
                'sprite': 'player'
            }
        )

        # Finish setting up the player object
        self.players[sid] = {
            'username': username,
            'on level': self.WorldManager.defaultLevel(),
            'entity': player_entity
        }

        # The player entity needs a position on the level
        present_level = self.getPresentLevel(sid)

        self.EntityManager.addComponent(
            player_entity,
            'position',
            {
                'x': present_level['elements']['spawn']['x'],
                'y': present_level['elements']['spawn']['y']
            }
        )

        # Add the player's entity to the level they're on
        if 'entities' not in present_level.keys():
            present_level['entities'] = []

        present_level['entities'].append(
            self.EntityManager.getEntity(player_entity))

    def removePlayer(self, sid):
        if sid in self.players.keys():
            ent = self.EntityManager.getEntity(self.players[sid]['entity'])

            ent['active'] = False
            ent['updated'] = True

            log(
                'Manager',
                f'Player removed (entity #{self.players[sid]["entity"]})',
                'debug'
            )

    # Given a player's SID, returns the level that they're on
    def getPresentLevel(self, sid):
        if sid in self.players.keys():
            on_level = self.players[sid]['on level']

            if self.WorldManager.levelLoaded(on_level):
                return self.WorldManager.getLevel(on_level)
            else:
                # The level hasn't been loaded yet, so we need to load it.
                # If loading is a success, then return the level
                log(
                    'Manager',
                    f'Have to load level {on_level} for \
{self.players[sid]["username"]}',
                    'debug'
                )

                if self.WorldManager.loadLevel(on_level):
                    return self.WorldManager.getLevel(on_level)
        else:
            # If the player isn't known, it's a warning
            log('Manager', f'Player with SID {sid} isn\'t known', 'error')

    # "Links" a player to a level, meaning they will be sent any updates
    def linkPlayerToLevel(self, sid, level_id):
        if level_id in self.links.keys():
            if sid not in self.links[level_id]:
                self.links[level_id].append(sid)
        else:
            self.links[level_id] = [sid]

    # Handles a user action
    def action(self, sid, action_type, details):
        if action_type == 'move':
            if sid in self.players.keys():
                ent = self.EntityManager.getEntity(self.players[sid]['entity'])
                pos = ent['components']['position']

                old_x = pos['x']
                old_y = pos['y']

                if 'dir' in details.keys() and details['dir'] == '1':
                    pos['x'] -= 1
                    pos['y'] += 1
                elif 'dir' in details.keys() and details['dir'] == '2':
                    pos['y'] += 1
                elif 'dir' in details.keys() and details['dir'] == '3':
                    pos['x'] += 1
                    pos['y'] += 1
                elif 'dir' in details.keys() and details['dir'] == '4':
                    pos['x'] -= 1
                elif 'dir' in details.keys() and details['dir'] == '6':
                    pos['x'] += 1
                elif 'dir' in details.keys() and details['dir'] == '7':
                    pos['x'] -= 1
                    pos['y'] -= 1
                elif 'dir' in details.keys() and details['dir'] == '8':
                    pos['y'] -= 1
                elif 'dir' in details.keys() and details['dir'] == '9':
                    pos['x'] += 1
                    pos['y'] -= 1

                if self.WorldManager.validMove(
                    self.players[sid]['on level'],
                    pos
                ):
                    # Mark the entity as updated, so that it will be sent to
                    #     users
                    ent['updated'] = True
                else:
                    pos['x'] = old_x
                    pos['y'] = old_y

    # Checks for updated (changed) entities, and sends the updated data to
    #     relevant players (usually players on the same level)
    def emitUpdates(self, sio):
        to_reset = []  # Entities that need their "updated" status reset

        for l in self.links.keys():
            for p in self.links[l]:
                entity_updates = []
                present_level = self.getPresentLevel(p)

                if 'entities' in present_level.keys():
                    for e in present_level['entities']:
                        if e['updated']:
                            entity_updates.append(e)
                            to_reset.append(e)

                sio.emit('entity updates', entity_updates, room=p)

        for e in to_reset:
            e['updated'] = False
