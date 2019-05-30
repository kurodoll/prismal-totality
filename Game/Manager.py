from log import log

from . import WorldManager
from . import EntityManager
from . import CombatManager


# Manages the entire game world
class Manager:
    def __init__(self):
        self.WorldManager = WorldManager.WorldManager()
        self.EntityManager = EntityManager.EntityManager()
        self.CombatManager = CombatManager.CombatManager()

        self.players = {}
        self.links = {}  # Links from levels to players to be updated

        # A list of entity IDs that clients need to destroy
        self.entities_to_destroy = []

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

        self.EntityManager.addComponent(
            player_entity,
            'sid',
            {
                'sid': sid
            }
        )

        self.EntityManager.addComponent(
            player_entity,
            'stats',
            {
                'health': 10,
                'strength': 5
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

                if self.WorldManager.loadLevel(on_level, self.EntityManager):
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

    def unlinkPlayerFromLevel(self, sid, level_id):
        if level_id in self.links.keys():
            if sid in self.links[level_id]:
                self.links[level_id].remove(sid)

    # Handles a user action
    def action(self, sid, action_type, details):
        if action_type == 'move':
            if sid in self.players.keys():
                ent = self.EntityManager.getEntity(self.players[sid]['entity'])
                pos = ent['components']['position']

                old_x = int(pos['x'])
                old_y = int(pos['y'])

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

                response = self.WorldManager.validMove(
                    self.players[sid]['on level'],
                    pos
                )

                if response['success']:
                    # Mark the entity as updated, so that it will be sent to
                    #     users
                    ent['updated'] = True

                    # Update combat stuff
                    self.WorldManager.checkForCombat(
                        self.players[sid]['on level'],
                        ent
                    )

                    if 'combat' in ent.keys() and ent['combat']['in_combat']:
                        self.EntityManager.playerInCombatMoved(
                            sid,
                            self.getPresentLevel(sid),
                            self.WorldManager
                        )

                    if response['message']:
                        return {
                            'response': 'message',
                            'data': response['message']
                        }
                else:
                    # Player attacked a monster
                    if response['message'] == 'monster':
                        response['message'] = self.CombatManager.attack(ent, response['data'])  # noqa

                    pos['x'] = old_x
                    pos['y'] = old_y

                    # Update combat stuff
                    self.WorldManager.checkForCombat(
                        self.players[sid]['on level'],
                        ent
                    )

                    if 'combat' in ent.keys() and ent['combat']['in_combat']:
                        self.EntityManager.playerInCombatMoved(
                            sid,
                            self.getPresentLevel(sid),
                            self.WorldManager
                        )

                    return {
                        'response': 'message',
                        'data': response['message']
                    }

        # If a user goes down some stairs, we have to change their level
        elif action_type == 'stairs down':
            if sid in self.players.keys():
                on_level = self.players[sid]['on level']
                level = self.WorldManager.getLevel(on_level)

                if 'stairs down' in level['elements']:
                    player_entity = None

                    # Remove the player's entity from its current level
                    for i in range(0, len(level['entities'])):
                        if 'sid' in level['entities'][i]['components']:
                            if level['entities'][i]['components']['sid']['sid'] == sid:  # noqa
                                stairs_pos = self.WorldManager.getTilePos(on_level, 'stairs down')  # noqa

                                # If the player isn't on stairs, ignore
                                if stairs_pos != level['entities'][i]['components']['position']:  # noqa
                                    return

                                self.entities_to_destroy.append(
                                    {
                                        'level': on_level,
                                        'id': level['entities'][i]['id']
                                    }
                                )

                                player_entity = level['entities'].pop(i)
                                self.unlinkPlayerFromLevel(sid, on_level)

                                break

                    # Set the player to be on the new level
                    target = level['elements']['stairs down']['target']
                    self.players[sid]['on level'] = target

                    self.linkPlayerToLevel(sid, target)

                    # Load the level if it hasn't been already
                    if not self.WorldManager.levelLoaded(target):
                        self.WorldManager.loadLevel(target, self.EntityManager)

                    target_level = self.WorldManager.getLevel(target)

                    # Set up the player's entity to be on the new level
                    spawn_x = target_level['elements']['spawn']['x']
                    spawn_y = target_level['elements']['spawn']['y']

                    player_entity['components']['position']['x'] = spawn_x
                    player_entity['components']['position']['y'] = spawn_y
                    player_entity['updated'] = True

                    # Put the player entity into the data of the new level
                    if 'entities' not in target_level.keys():
                        target_level['entities'] = []

                    target_level['entities'].append(player_entity)

                    # Since the old player entity was removed, we also need to
                    #     update the entry in the entity manager
                    self.EntityManager.replace(
                        player_entity['id'],
                        player_entity
                    )

                    return {
                        'response': 'level change',
                        'data': target
                    }

    # Checks for updated (changed) entities, and sends the updated data to
    #     relevant players (usually players on the same level)
    def emitUpdates(self, sio):
        # First emit entities that need to be destroyed
        for e in self.entities_to_destroy:
            log('Manager', f'Destroy entity {e["id"]} (client-side)', 'debug')

            for p in self.links[e['level']]:
                sio.emit('destroy entity', e['id'], room=p)

        self.entities_to_destroy = []

        # Then emit updates
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

                if len(entity_updates) > 0:
                    sio.emit('entity updates', entity_updates, room=p)

        for e in to_reset:
            e['updated'] = False

    # Handle all periodic updates to the world
    def doUpdates(self):
        self.WorldManager.spawnMonsters(self.EntityManager)
        self.WorldManager.updateMonsters(self.EntityManager)
