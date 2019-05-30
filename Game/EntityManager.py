from log import log
import json


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
