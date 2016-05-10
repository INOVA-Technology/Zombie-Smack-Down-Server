import random, os, sys

directory = os.path.realpath('.')
absolute_directory = os.path.join(directory, 'lib')
sys.path.append(absolute_directory)
import color

random.seed()

class Player:

    def __init__(self, game):
        self.game = game
        self.health = 25
        self.money = 5

    def kick(self, zombie):
        damage = random.randint(4, 6)
        zombie.take_damage(damage)

    def punch(self, zombie):
        damage = random.randint(3, 7)
        zombie.take_damage(damage)

    def take_damage(self, damage):
        self.health -= damage
        self.game.display(color.RED + "The zombie beat the heck you! -%d" % damage + color.END)
        self.check_dead()

    def check_dead(self):
        if self.health <= 0:
            self.game.display(color.RED + "You died!" + color.END)
            self.game.quit()



