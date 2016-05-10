import os, sys, socket, names, re
from collections import OrderedDict

directory = os.path.realpath('.')
absolute_directory = os.path.join(directory, 'lib')
sys.path.append(absolute_directory)
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

    def quit(self):
        self.server.disconnect(self.socket)

    def start(self):
        self.generate_zombie()

    def generate_zombie(self):
        self.round += 1
        self.zombie = Zombie(self, *ZOMBIE_TYPES[(self.round - 1) // 3])
        self.zombie.name = names.get_full_name()

    def display(self, string, newLine = True):
        if newLine: string += '\n'
        self.socket.send(string.encode())

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
        


