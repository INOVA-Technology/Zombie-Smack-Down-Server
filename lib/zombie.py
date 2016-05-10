import random

random.seed()

class Zombie:
    
    def __init__(self, game, name, kind, health, power):
        self.game = game
        self.name = name
        self.kind = kind
        self.health = random.randint(*health)
        self.power = power
        self.alive = True

    def take_damage(self, damage):
        self.health -= damage
        self.game.display("-%d!" % damage)
        self.check_dead()

    def check_dead(self):
        if self.health <= 0:
            self.game.display("You killed %s, the %s" % (self.name, self.kind))
            self.alive = False

    def attack(self, player):
        damage = random.randint(*self.power)
        player.take_damage(damage)


