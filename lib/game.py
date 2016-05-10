import os, sys, socket, re
from collections import OrderedDict

directory = os.path.realpath('.')
absolute_directory = os.path.join(directory, 'lib')
sys.path.append(absolute_directory)
import color
from zombie import Zombie
from zombie_list import ZOMBIE_TYPES
from player import Player

class Game:

    def __init__(self, socket, server):
        self.player = Player(self)
        self.round = 0
        self.zombie = None
        self.socket = socket
        self.server = server
        self.wave = 1

    def quit(self):
        self.server.disconnect(self.socket)

    def start(self):
        self.display(color.MAGENTA + 'Type help or ? for help' + color.END)
        self.display('> ', newLine = False)
        self.generate_zombie()

    def generate_zombie(self):
        self.round += 1
        if self.round % 3 == 0:
            self.wave += 1
        self.zombie = Zombie(self, *ZOMBIE_TYPES[self.wave - 1])

    def display(self, string, newLine = True):
        if newLine: string += '\n'
        try:
            self.socket.send(string.encode())
        except OSError:
            pass

    def check_regex(self, feedback, regex_str):
        match = re.compile(regex_str).match(feedback)
        if match:
            return match.groups()
        else:
            return None

    def parse_input(self, feedback):
        feedback = feedback.strip().lower()
        cmds = OrderedDict()
        cmds['^kick$'] = lambda x: self.kick()
        cmds['^punch$'] = lambda x: self.punch()
        cmds['^info$'] = lambda x: self.info()
        cmds['^quit|exit$'] = lambda x: self.quit()
        cmds['^heal( (\d+))?$'] = lambda x: self.player.heal(x[1])
        cmds['^\s*$'] = lambda x: None

        match = None
        cmd_found = None
        for key in cmds.keys():
            match = self.check_regex(feedback, key)
            if match is not None:
                cmd_found = key
                break

        if match is None:
            self.display('What?')
        else:
            cmds[cmd_found](match)

        if not (feedback == "quit" or feedback == "exit"):
            self.display('> ', newLine = False)

    def kick(self):
        self.player.kick(self.zombie)
        self.finish_attack()

    def punch(self):
        self.player.punch(self.zombie)
        self.finish_attack()

    def finish_attack(self):
        if self.zombie.alive:
            self.zombie.attack(self.player)
        else:
            self.generate_zombie()

    def info(self):
        self.player.info()
        self.display('')
        self.zombie.info()

        


