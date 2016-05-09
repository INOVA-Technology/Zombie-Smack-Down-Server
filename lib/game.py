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
        self.player = Player()
        self.round = 1
        self.zombie = None
        self.socket = socket
        self.server = server

    def quit(self):
        self.server.disconnect(self.socket)

    def start(self):
        self.generate_zombie()

    def generate_zombie(self):
        self.zombie = Zombie(*ZOMBIE_TYPES[(self.round - 1) // 3])
        self.zombie.name = names.get_first_name()
        self.socket.send((self.zombie.name + '\n').encode())

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
        cmds['^kick$'] = (lambda x:
            self.display('Woa there, hold your horses.'))

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



