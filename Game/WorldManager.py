from log import log

import json
import random


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

        # Define tiles that can be moved on
        self.valid_movements = [
            'ground',
            'tall grass',
            'stairs down'
        ]

    # Returns the ID of the default level (where new players will start)
    def defaultLevel(self):
        return 'test'

    # Loads a level into memory. Returns True on success
    def loadLevel(self, level_id, entity_manager):
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

            # If the level needs to be generated, generate it
            if 'generator' in level_data['level'].keys():
                self.generateLevel(level_data)

            # Set up extra entity data
            entity_manager.loadEntities(level_data)

            return True

        return False

    def generateLevel(self, level):
        if level['level']['generator'] == 'cave':
            total_tiles = level['level']['width'] * level['level']['height']
            fill_tiles = int(total_tiles / 3)  # How many tiles to generate

            # Start in the middle of the level space
            cur_x = int(level['level']['width'] / 2)
            cur_y = int(level['level']['height'] / 2)

            # Tiles that are allowed to be generated.
            # Multiple entries are used as a simple weighting system for now
            possible_tiles = [
                'ground',
                'ground',
                'tall grass'
            ]

            # Tiles where a spawn point could be placed
            spawnable_tiles = []

            # Create an empty level
            level['level']['tiles'] = []
            for i in range(0, total_tiles):
                level['level']['tiles'].append('empty')

            # Randomly create a floor space using a random walk algorithm
            for i in range(0, fill_tiles):
                # Choose a tile type to place
                tile_type = random.randint(0, len(possible_tiles) - 1)

                tile_index = int(cur_y * level['level']['width'] + cur_x)
                level['level']['tiles'][tile_index] = possible_tiles[tile_type]

                spawnable_tiles.append({
                    'x': cur_x,
                    'y': cur_y
                })

                # Move the "cursor" randomly until a suitable next spot to
                #     place a tile is found
                while True:
                    if random.random() > 0.5:
                        if random.random() > 0.5:
                            cur_x += 1
                        else:
                            cur_x -= 1
                    else:
                        if random.random() > 0.5:
                            cur_y += 1
                        else:
                            cur_y -= 1

                    if cur_x < 0 or cur_x >= level['level']['width']:
                        cur_x = int(level['level']['width'] / 2)

                    if cur_y < 0 or cur_y >= level['level']['height']:
                        cur_y = int(level['level']['height'] / 2)

                    if level['level']['tiles'][cur_y * level['level']['width'] + cur_x] == 'empty':  # noqa
                        break

            # Place a spawn point somewhere random
            spawn_tile = random.randint(0, len(spawnable_tiles) - 1)

            if 'elements' not in level.keys():
                level['elements'] = {}

            level['elements']['spawn'] = spawnable_tiles[spawn_tile]

    def levelLoaded(self, level_id):
        return level_id in self.levels.keys()

    def getLevel(self, level_id):
        if level_id in self.levels.keys():
            return self.levels[level_id]

        log('WorldManager', f'Request for unloaded level {level_id}', 'error')

    # Checks whether a tile can be moved to
    def validMove(self, level_id, coords):
        x = coords['x']
        y = coords['y']
        w = self.levels[level_id]['level']['width']
        h = self.levels[level_id]['level']['height']

        if x < 0 or y < 0 or x >= w or y >= h:
            return {
                'success': False,
                'message': 'You cannot move there'
            }

        tile = self.levels[level_id]['level']['tiles'][y * w + x]

        if tile in self.valid_movements:
            message = None

            if tile == 'tall grass':
                message = 'You rustle through the tall grass'

            # Check for entities on the tile
            for e in self.levels[level_id]['entities']:
                if not e['active']:
                    continue

                if 'position' in e['components']:
                    if e['components']['position']['x'] == x and e['components']['position']['y'] == y:  # noqa
                        if 'type' in e and e['type'].split('.')[0] == 'monsters':  # noqa
                            # Attacked a monster
                            return {
                                'success': False,
                                'message': 'monster',
                                'data': e
                            }

            return {
                'success': True,
                'message': message
            }
        elif tile == 'wall':
            return {
                'success': False,
                'message': 'You bump into the wall'
            }

        return {
            'success': False,
            'message': 'You cannot move there'
        }
