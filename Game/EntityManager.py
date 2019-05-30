from log import log

import json
import random


class EntityManager:
    def __init__(self):
        self.id = 0
        self.entities = {}

        # Load pre-defined entities
        self.entity_types = {
            "monsters": json.load(
                open('Game/data/entities/monsters.json', 'r')
            )
        }

    def addNew(self):
        ent_id = self.id
        self.id += 1

        self.entities[ent_id] = {
            'id': ent_id,
            'active': True,
            'components': {},
            'updated': True  # Whether entity data has changed and needs to be
                             #     sent to concerned players. True by default
                             #     so that new entities get sent out
        }

        log('EntityManager', f'New entity added #{ent_id}', 'debug')
        return ent_id

    def addExistingEntity(self, entity):
        ent_id = self.id
        self.id += 1

        entity['id'] = ent_id
        entity['active'] = True
        entity['updated'] = True

        self.entities[ent_id] = entity
        log('EntityManager', f'Existing entity added #{ent_id}', 'debug')

    def replace(self, ent_id, entity):
        self.entities[ent_id] = entity

    def addComponent(self, entity_id, component_type, component_data):
        self.entities[entity_id]['components'][component_type] = component_data

    def getEntity(self, entity_id):
        return self.entities[entity_id]

    def loadEntity(self, e):
        self.addExistingEntity(e)

        # Load entity data from pre-defined entity types
        if 'type' in e.keys():
            a = e['type'].split('.')[0]
            b = e['type'].split('.')[1]

            e['components'].update(
                self.entity_types[a][b]['components']
            )

    def loadEntities(self, level):
        if 'entities' in level.keys():
            for e in level['entities']:
                self.loadEntity(e)

    # Like loadEntities, but only handles entities with a certain flag
    def loadNewEntities(self, level):
        if 'entities' in level.keys():
            for e in level['entities']:
                if 'new' in e.keys() and e['new']:
                    self.loadEntity(e)
                    e['new'] = False

    def entityMakeMove(self, entity_id, level_id, world_manager):
        e = self.entities[entity_id]

        if e['components']['movement'] == 'random':
            x = e['components']['position']['x']
            y = e['components']['position']['y']

            adjacent_spots = [
                {'x': x - 1, 'y': y - 1},
                {'x': x, 'y': y - 1},
                {'x': x + 1, 'y': y - 1},
                {'x': x - 1, 'y': y},
                {'x': x + 1, 'y': y},
                {'x': x - 1, 'y': y + 1},
                {'x': x, 'y': y + 1},
                {'x': x + 1, 'y': y + 1}
            ]

            possible_spots = []

            for a in adjacent_spots:
                if world_manager.validMove(level_id, a)['success']:
                    possible_spots.append(a)

            res = random.randint(0, len(possible_spots) - 1)

            e['components']['position'] = possible_spots[res]
            e['updated'] = True

    # If a player is in combat, tell their opponent(s) that they can make a
    #     move
    def playerInCombatMoved(self, sid, level, world_manager):
        if 'entities' in level.keys():
            for e in level['entities']:
                try:
                    if e['combat']['opponent'] == sid:
                        self.entityMakeMove(e['id'], level['id'], world_manager)  # noqa
                except KeyError:
                    pass
