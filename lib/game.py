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
from commands import Command

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
        self.server.db.commit()
    
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
        c.execute('INSERT INTO users VALUES (?, ?, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0)', (self.account_name, self.account_password_hash))
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
        if bcrypt.hashpw(text.encode(), self.account_info[1]):
            self.display('Welcome %s!' % self.account_info[0])
            a = self.account_info
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

    # for debugging purposes
    def hack(self):
        self.player.kills_since_last_rank_up = 11

    def parse_input(self, feedback):
        feedback = feedback.strip().lower()
        cmds = OrderedDict()
        cmds['^heal( (\d+))?$'] = lambda x: self.player.heal(x[1])
        cmds['^\s*$'] = lambda x: None

        #cmds['h@ck'] = lambda x: self.hack()

        match = None
        cmd_found = None
        for command in self.commands:
            match = self.check_regex(feedback, command.regex)
            if match is not None:
                cmd_found = command.func
                break

        status = None
        if match is None:
            status = self.try_combo(feedback)
            if not self.combo_found:
                self.display('What?')

            self.combo_found = False
        else:
            status = cmd_found(match)

        self.print_prompt(feedback)

        return status if status else self.parse_input

    def create_commands(self):
        self.commands = []
        
        self.commands.append(Command('^kick$', 'kick', 'It\'s what it sounds like.', 'Noob', 0.4))
        self.commands.append(Command('^punch$', 'punch', 'When one takes his fingers and folds them into the palm, projecting it at a zombie.', 'Noob', 0.2))    
        self.commands.append(Command('^info$', 'info', 'Gives info'))            
        self.commands.append(Command('^(help|\?)( ([\w\s]+))?$', 'help', 'Gives help'))            
        self.commands.append(Command('^quit|exit$', 'quit', 'If you want to leave.'))            
        self.commands.append(Command('^heal( (\d+))?$', 'heal', 'It heals you.'))    
        
        self.commands[0].func = lambda x: self.kick()    
        self.commands[1].func = lambda x: self.punch()
        self.commands[2].func = lambda x: self.info()
        self.commands[3].func = lambda x: self.help(x[2])   # LOL
        self.commands[4].func = lambda x: self.quit()
        self.commands[5].func = lambda x: self.player.heal(x[1])

    def try_combo(self, combo_name):
        c = None
        for combo in COMBOS:
            if combo[0] == combo_name:
                c = combo
                self.combo_found = True
                break

        if c:
            combo = Combo(self, *c)
            # check for enough xp, and use it
            if self.player.xp >= combo.price:
                self.player.take_xp(combo.price)
                combo.do_extra()
                stat = self.player.attack(self.zombie, combo.damage)
                return self.finish_attack(stat)
            else:
                self.display("You don't have enough xp.")
            

    def print_prompt(self, feedback = ""):
        if not (feedback == "quit" or feedback == "exit"):
            self.display('> ', newLine = False)

    def kick(self):
        stat = self.player.kick(self.zombie)
        return self.finish_attack(stat)

    def punch(self):
        stat = self.player.punch(self.zombie)
        return self.finish_attack(stat)

    def finish_attack(self, stat):
        if self.zombie.alive:
            return self.zombie.attack(self.player)
        else:
            if stat:
                return stat
            else:
                self.generate_zombie()

    def info(self):
        self.player.info()
        self.display('')
        self.zombie.info()

    def help(self, cmd = None):
        if not cmd:
            names = ", ".join([str(command.name) for command in self.commands])
            self.display('Here are some helpful commands: ' + names)

        else:
            cmd = cmd.lower().strip()
            for command in self.commands:
                if cmd == command.name:
                    the_command = command

            self.display(color.MAGENTA + the_command.name)
            self.display(color.MAGENTA + the_command.desc + color.END)

