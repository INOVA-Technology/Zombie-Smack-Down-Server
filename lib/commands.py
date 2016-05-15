import random

class Command:

    def __init__(self, regex, name, desc, func):
        self.regex = regex
        self.name = name
        self.desc = desc
        self.func = func

class Attack:

    ATTACKS = {}

    def __init__(self, game, isCombo, name, price, damage_range, _type, func = None):
        self.game = game
        self.isCombo = isCombo
        self.name = name
        self.price = price
        self.damage_range = damage_range
        self.type = _type
        self.func = func

    def get_damage(self):
        return random.randint(*self.damage_range)

    def variance(self):
        return (damage_range[1] / damage_range[0]) - 1

    def do_extra(self):
        if self.func != None:
            self.func(self)

    @staticmethod
    def create_attacks(game):
        combos_list = [
            ["kick punch", 2, [3, 9], "beginner"],
            ["trip stomp", 3, [5, 11], "beginner"],
            ["punch punch kick", 5, [5, 14], "apprentice"],
            ["knee punch face slap", 5, [3, 13], "apprentice"],
            ["heal fury", 5, [5, 10], "apprentice", lambda c: c.game.player.heal(random.randint(3, 9), False) ],
            ["elbow fist knee fist knee body slam", 7, [8, 17], "advanced"],
            ["kick kick kick kick kick kick kick kick kick kick", 9, [11, 16], "advanced"],
        ]

        for c in combos_list:
            Attack.ATTACKS[c[0]] = Attack(game, True, *c)

        Attack.ATTACKS['kick'] = Attack(game, False, 'kick', 0, [3, 7], "noob")
        Attack.ATTACKS['punch'] = Attack(game, False, 'punch', 0, [4, 6], "noob")



        

    
