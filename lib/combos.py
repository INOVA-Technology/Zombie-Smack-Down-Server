import random

class Combo:

    def __init__(self, game, name, price, damage, func = None):
        self.game = game
        self.name = name
        self.price = price
        self.damage = random.randint(*damage)
        self.func = func

    def do_extra(self):
        if self.func != None:
            self.func(self)


COMBOS = [
    ["kick punch", 2, [3, 9]],
    ["trip stomp", 3, [5, 11]],
    ["punch punch kick", 5, [5, 14]],
    ["knee punch face slap", 5, [3, 13]],
    ["heal fury", 5, [5, 10], lambda c: c.game.player.heal(random.randint(3, 9)) ],
    ["elbow fist knee fist knee body slam", 7, [8, 17]],
    ["kick kick kick kick kick kick kick kick kick kick", 9, [11, 16]],
]




