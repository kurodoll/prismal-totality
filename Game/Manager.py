from log import log

from . import WorldManager
from . import EntityManager


# Manages the entire game world
class Manager:
    def __init__(self):
        self.WorldManager = WorldManager.WorldManager()
        self.EntityManager = EntityManager.EntityManager()

        self.players = {}

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
        pass
