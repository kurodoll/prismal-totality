from log import log


class EntityManager:
    def __init__(self):
        self.id = 0
        self.entities = {}

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

    def replace(self, ent_id, entity):
        self.entities[ent_id] = entity

    def addComponent(self, entity_id, component_type, component_data):
        self.entities[entity_id]['components'][component_type] = component_data

    def getEntity(self, entity_id):
        return self.entities[entity_id]
