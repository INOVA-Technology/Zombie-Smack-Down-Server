import random, os, sys

directory = os.path.realpath('.')
absolute_directory = os.path.join(directory, 'lib')
sys.path.append(absolute_directory)
import color

random.seed()

class Player:

    def __init__(self, game, username, has_healed, number_of_games_played, punch_upgrade, kick_upgrade, total_kills, rank, new_game, current_kills, wave, xp, health):
        self.game = game
        self.username = username
        self.has_healed = has_healed
        self.number_of_games_played = number_of_games_played
        self.punch_upgrade = punch_upgrade
        self.kick_upgrade = kick_upgrade
        self.total_kills = total_kills
        self.rank = rank
        self.new_game = new_game
        if not new_game:
            self.current_kills = current_kills
            self.wave = wave
            self.xp = xp
            self.health = health
        else:
            self.current_kills = 0
            self.wave = 1
            self.xp = 5
            self.health = 25

    def kick(self, zombie):
        damage = random.randint(4, 6)
        zombie.take_damage(damage)

    def punch(self, zombie):
        damage = random.randint(3, 7)
        zombie.take_damage(damage)

    def take_damage(self, damage):
        self.health -= damage
        self.game.display(color.RED + "The zombie beat the heck out of you! -%d" % damage + color.END)
        self.check_dead()

    def check_dead(self):
        if self.health <= 0:
            self.game.display(color.RED + "You died!" + color.END)
            self.game.quit()

    def info(self):
        self.game.display(color.MAGENTA, newLine = False)
        self.game.display("Health: %d" % self.health)
        self.game.display("XP: %d" % self.xp)
        self.game.display("Rank: %d" % self.rank)
        self.game.display("Wave: %d" % self.wave)
        self.game.display("Kills: %d" % self.current_kills) 
        self.game.display(color.END, newLine = False)

    def give_xp(self, amount):
        self.xp += amount
        self.game.display(color.CYAN + "+%d xp!" % amount + color.END)

    def add_kill(self):
        self.current_kills += 1
        self.total_kills += 1
        if self.current_kills % 3 == 0:
            self.wave += 1

    def heal(self, amount):
        amount = int(amount)
        if amount and amount > 0:
            if self.xp >= amount:
                self.health += amount
                self.xp -= amount
                self.game.display(color.CYAN + '+%d health!' % amount + color.END)
                self.game.display(color.RED + '-%d xp' % amount + color.END)
            else:
                self.game.display(color.YELLOW + 'You don\'t have enough xp!' + color.END)
        else:
            self.game.display(color.MAGENTA, newLine = False)
            self.game.display('Usage: heal amount')
            self.game.display('amount must be an integer greater then 0.')
            self.game.display('For each hp you heal, you will lose one xp.')
            self.game.display(color.END, newLine = False)



