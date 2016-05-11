import os, sys, socket, re, sqlite3, bcrypt
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
        self.round = 0
        self.zombie = None
        self.socket = socket
        self.server = server
        self.account_name = ''
        self.account_password_hash = ''
        self.account_info = ()

    def quit(self):
        self.server.disconnect(self.socket)

    def signin(self, text = None):
        self.display(color.MAGENTA + 'Welcome to Zombie Smack Down!' + color.END)
        self.display("Enter 'signin' if you've been here before and have an account, or enter 'signup' to create an account.")
        self.display("An account is only necessary to save your progress. If you wish to play as a guest, simply enter 'guest'.") 
        self.display("If you hate fun therefore do not wish to play zombie smack down, enter 'quit'.")

        return self.do_signin

    def do_signin(self, text):
        method = text.strip().lower()
        if method == 'sign in' or method == 'signin':
            self.display('Username: ', newLine = False)
            return self.signin_username
        elif method == 'sign up' or method == 'signup':
            self.display('Enter a username: ', newLine = False)
            return self.create_account_name
        elif method == 'quit':
            self.display('Bye!')
            self.quit()
        else:
            self.display('What?')
            return self.do_signin

    def create_account_name(self, text):
        self.account_name = text.strip()
        c = self.server.db.cursor()
        c.execute('SELECT username FROM users WHERE username = ?', (self.account_name,))
        if c.fetchone():
            self.display(color.YELLOW + 'That username is already taken. Please pick another ;(' + color.END)
            self.display('Username: ', newLine = False)
            return self.create_account_name
        self.display('Enter a password: ', newLine = False)
        self.socket.send(b'\xff\xfb\x01')
        return self.create_account_password

    def create_account_password(self, text):
        self.socket.send(b'\xff\xfc\x01')
        self.account_password_hash = bcrypt.hashpw(text, bcrypt.gensalt(12))
        self.create_account()
        self.start()

    def create_account(self):
        c = self.server.db.cursor()
        c.execute('INSERT INTO users VALUES (?, ?, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0)', (self.account_name, self.account_password_hash))
        self.server.db.commit()
        self.display('Account created!')
        self.player = Player(self, self.account_name, False, 0, 0, 0, 0, 1, True, 0, 0, 0, 0)

    def signin_username(self, text):
        name = text.strip()
        c = self.server.db.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (name,))
        self.account_info = c.fetchone()
        if self.account_info:
            self.display('Password: ', newLine = False)
            self.socket.send(b'\xff\xfb\x01')
            return self.signin_password
        else:
            self.display(color.YELLOW + 'Unknown username.' + color.END)
            self.quit()

    def signin_password(self, text):
        self.socket.send(b'\xff\xfc\x01\n')
        if bcrypt.checkpw(text, self.account_info[1]):
            self.display('Welcome %s!' % self.account_info[0])
            a = self.account_info
            self.player = Player(self, a[0], a[2], [3], a[4], a[5], a[6], a[7], a[8], a[9], a[10], a[11], a[12])
            self.start()
        else:
            self.display(color.YELLOW + 'Wrong passoword.' + color.END)
            self.quit()

    def start(self):
        self.display(color.MAGENTA + 'Type help or ? for help' + color.END)
        self.display('> ', newLine = False)
        self.generate_zombie()

    def generate_zombie(self):
        self.zombie = Zombie(self, *ZOMBIE_TYPES[self.player.wave - 1])

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
            status = cmds[cmd_found](match)

        if not (feedback == "quit" or feedback == "exit"):
            self.display('> ', newLine = False)

        return status if status else self.parse_input

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

        


