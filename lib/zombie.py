import random, os, sys

directory = os.path.realpath('.')
absolute_directory = os.path.join(directory, 'lib')
sys.path.append(absolute_directory)
import color

random.seed()

class Zombie:
    
    def __init__(self, game, name, kind, health, power, xp):
        self.game = game
        self.name = name
        self.kind = kind
        self.health = random.randint(*health)
        self.power = power
        self.xp = random.randint(*xp)
        self.alive = True

    def take_damage(self, damage):
        self.health -= damage
        self.game.display(color.RED + "You hit the zombie! -%d" % damage + color.END)
        self.check_dead()

    def check_dead(self):
        if self.health <= 0:
            self.game.display(color.RED + "KO! You killed the %s!" % self.kind.lower() + color.END)
            self.game.player.give_xp(self.xp)
            self.alive = False

    def attack(self, player):
        damage = random.randint(*self.power)
        player.take_damage(damage)

    def info(self):
        self.game.display(color.MAGENTA, newLine = False)
        self.game.display("%s health: %d" % (self.kind, self.health))
        self.game.display("Attack Strength: %d to %d" % (self.power[0], self.power[1]))
        self.game.display(color.END, newLine = False)


