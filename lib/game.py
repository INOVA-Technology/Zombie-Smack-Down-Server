import os, sys
directory = os.path.realpath('.')
absolute_directory = os.path.join(directory, 'lib')
sys.path.append(absolute_directory)
import zombie_list

class Game:

    def __init__(self):
        self.player = Player()
        self.round = 1
        self.zombie = None

    def start(self):
        pass

    def generate_zombie(self):
        self.zombie = Zombie(ZOMBIE_TYPES[(self.round - 1) // 3])


