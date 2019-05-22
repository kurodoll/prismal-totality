from log import log
import json


# Manages the levels of the game world
class WorldManager:
    def __init__(self):
        self.levels = {}

        # Load in the list of defined levels
        filename = 'Game/data/world/defined_levels.json'

        try:
            self.defined_levels = json.load(open(filename, 'r'))
            log('WorldManager', f'Loaded {filename}')
        except IOError:
            log('WorldManager', f'Failed to open {filename}', 'fatal error')
            exit()
        except json.decoder.JSONDecodeError:
            log(
                'WorldManager',
                f'Failed to parse {filename} (empty?)',
                'warning'
            )

    # Returns the ID of the default level (where new players will start)
    def defaultLevel(self):
        return 'test'

    # Loads a level into memory. Returns True on success
    def loadLevel(self, level_id):
        log('WorldManager', 'Loading level ' + level_id, 'debug')

        if level_id in self.defined_levels.keys():
            level_filename = self.defined_levels[level_id]

            try:
                level_data = json.load(open(level_filename, 'r'))
            except IOError:
                log(
                    'WorldManager',
                    f'Failed to open {level_filename}',
                    'error'
                )

                return False
            except json.decoder.JSONDecodeError:
                log(
                    'WorldManager',
                    f'Failed to parse {level_filename} (empty?)',
                    'warning'
                )

            self.levels[level_id] = level_data
            log('WorldManager', f'Loaded level {level_id}')

            return True

        return False

    def levelLoaded(self, level_id):
        return level_id in self.levels.keys()

    def getLevel(self, level_id):
        if level_id in self.levels.keys():
            return self.levels[level_id]

        log('WorldManager', f'Request for unloaded level {level_id}', 'error')
