import os, sys, socket, re, sqlite3, bcrypt
from collections import OrderedDict

directory = os.path.realpath('.')
absolute_directory = os.path.join(directory, 'lib')
sys.path.append(absolute_directory)
import color
from zombie import Zombie
from zombie_list import ZOMBIE_TYPES
from player import Player
from combos import Combo, COMBOS
from commands import Command, Attack

class Game:

    def __init__(self, socket, server):
        self.round = 0
        self.zombie = None
        self.socket = socket
        self.server = server
        self.account_name = ''
        self.account_password_hash = ''
        self.account_info = ()
        self.has_started = False
        self.combo_found = False
        self.create_commands()
        Attack.create_attacks(self)

    def quit(self):
        if not self.has_started:
            self.server.disconnect(self.socket)
        else:
            self.display(color.YELLOW + "Save yo game? Yes or no?" + color.END)
            return self.maybe_quit

    def maybe_quit(self, text):
        res = text.strip().lower()
        if res == 'yes':
            self.save()
        elif res != 'no':
            return self.quit()

        self.server.disconnect(self.socket)

    def save(self):
        c = self.server.db.cursor()
        c.execute('UPDATE users SET has_healed=?, number_of_games_played=?, punch_upgrade=?, kick_upgrade=?, total_kills=?, rank=?, kills_since_last_rank_up=?, new_game=?, current_kills=?, wave=?, xp=?, health=? WHERE username = ?', self.player.info_to_save())
        c.execute("SELECT float_value FROM stats WHERE record = 'total kills'")
        c.execute("UPDATE stats SET float_value = float_value + ? WHERE record = 'total kills'", (self.player.current_kills,))
        self.server.db.commit()
        self.display(color.YELLOW + "Game saved!" + color.END)
    
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
        self.account_password_hash = bcrypt.hashpw(text.encode(), bcrypt.gensalt(12))
        self.create_account()
        self.start()

    def create_account(self):
        c = self.server.db.cursor()
        c.execute('INSERT INTO users VALUES (NULL, ?, ?, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0)', (self.account_name, self.account_password_hash))
        c.execute("UPDATE stats SET float_value = float_value + 1 WHERE record = 'total users'")
        self.server.db.commit()
        self.display('Account created!')
        self.player = Player(self, self.account_name, False, 0, 0, 0, 0, 1, 0, True, 0, 0, 0, 0)

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
        if bcrypt.hashpw(text.encode(), self.account_info[2]) == self.account_info[2]:
            a = self.account_info[1:]
            self.display('Welcome %s!' % a[0])
            self.player = Player(self, a[0], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10], a[11], a[12], a[13])
            self.start()
        else:
            self.display(color.YELLOW + 'Wrong passoword.' + color.END)
            self.quit()

    #### END SERVER/ACCOUNT CRAP ####

    def start(self):
        self.display(color.MAGENTA + 'Type help or ? for help' + color.END)
        self.display('> ', newLine = False)
        self.generate_zombie()
        self.has_started = True

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

        match = None
        cmd_found = None
        for command in self.commands:
            match = self.check_regex(feedback, command.regex)
            if match is not None:
                cmd_found = command.func
                break

        status = None
        if match is None:
            attack = Attack.ATTACKS.get(feedback)
            if attack:
                status = self.player.attack(self.zombie, attack)
            else:
                self.display("What?")
        else:
            status = cmd_found(match)

        self.print_prompt(feedback)

        return status if status else self.parse_input

    def create_commands(self):
        self.commands = []

        tmp = [
            ['^info$', 'info', 'Gives info', lambda x: self.info() ],
            ['^(help|\?)( ([\w\s]+))?$', 'help', 'Gives help', lambda x: self.help(x[2]) ],
            ['^quit|exit$', 'quit', 'If you want to leave.', lambda x: self.quit() ],
            ['^heal( (\d+))?$', 'heal', 'It heals you.', lambda x: self.player.heal(x[1]) ],
            ['^save$', 'save', 'It saves the game', lambda x: self.save() ],
            ['^combolist$', 'combolist', 'It lists the combos you have unlocked.', lambda x: self.combolist() ]
        ]

        for tmpJr in tmp:
            self.commands.append(Command(*tmpJr))

        
    def print_prompt(self, feedback = ""):
        if not (feedback == "quit" or feedback == "exit"):
            self.display('> ', newLine = False)

    def combolist(self):
        combo_count = 1
        self.display(color.MAGENTA + 'Unlocked combos:' + color.END)
        for a in Attack.ATTACK_KEYS:
            attack = Attack.ATTACKS[a]
            if attack.isCombo:
                if combo_count <= self.player.rank:
                    attack.describe()
                    combo_count += 1


    def info(self):
        self.player.info()
        self.display('')
        self.zombie.info()

    def help(self, cmd = None):
        if not cmd:
            names = ", ".join([str(command.name) for command in self.commands])
            self.display('Here are some helpful commands: ' + names)
            # also explain/mention kick and punch

        else:
            # handle the case of cmd being an attack
            cmd = cmd.lower().strip()
            for command in self.commands:
                if cmd == command.name:
                    the_command = command

            self.display(color.MAGENTA + the_command.name)
            self.display(the_command.desc + color.END)

