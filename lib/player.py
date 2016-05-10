import random

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
        self.game.display("The zombie hurt you! -%d" % damage)
        self.check_dead()

    def check_dead(self):
        if self.health <= 0:
            self.game.display("You died!")
            self.game.quit()



