class CombatManager:
    def attack(self, attacker, defender):
        damage = attacker['components']['stats']['strength']
        defender['components']['stats']['health'] -= damage

        if defender['components']['stats']['health'] <= 0:
            defender['active'] = False
            defender['updated'] = True

            return 'You defeated ' + defender['components']['name'] + ' [' + str(damage) + ' damage]'  # noqa
        else:
            return 'You attacked ' + defender['components']['name'] + ' for ' + str(damage) + ' damage'  # noqa
