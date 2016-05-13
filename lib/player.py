import random, os, sys

directory = os.path.realpath('.')
absolute_directory = os.path.join(directory, 'lib')
sys.path.append(absolute_directory)
import color

random.seed()

class Player:

    # adding new saved property checklist: add to player.init, player.info_to_save, server.init_db, game.save, game.create_account, and game.signin_password
    # also somehow update all existing records in the db

    def __init__(self, game, username, has_healed, number_of_games_played, punch_upgrade, kick_upgrade, total_kills, rank, kills_since_last_rank_up, new_game, current_kills, wave, xp, health):
        self.game = game
        self.username = username
        self.has_healed = bool(has_healed)
        self.number_of_games_played = number_of_games_played
        self.punch_upgrade = punch_upgrade
        self.kick_upgrade = kick_upgrade
        self.total_kills = total_kills
        self.rank = rank
        self.kills_since_last_rank_up = kills_since_last_rank_up
        self.new_game = bool(new_game)
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
            self.give_xp((self.rank - 1) * 2, printMessage = False)

        self.new_game = False
        self.max_upgrade = 7

    def kick(self, zombie):
        damage = random.randint(4, 6) + self.kick_upgrade
        return self.attack(zombie, damage)

    def punch(self, zombie):
        damage = random.randint(3, 7) + self.punch_upgrade
        return self.attack(zombie, damage)

    def attack(self, zombie, damage):
        return zombie.take_damage(damage)

    def take_damage(self, damage):
        self.health -= damage
        self.game.display(color.RED + "The zombie beat the heck out of you! -%d" % damage + color.END)
        return self.check_dead()

    def check_dead(self):
        if self.health <= 0:
            self.game.display(color.RED + "You died!" + color.END)
            self.new_game = True
            self.number_of_games_played += 1
            return self.game.quit()

    def info(self):
        self.game.display(color.MAGENTA, newLine = False)
        self.game.display("Health: %d" % self.health)
        self.game.display("XP: %d" % self.xp)
        self.game.display("Rank: %d" % self.rank)
        self.game.display("Wave: %d" % self.wave)
        self.game.display("Kills: %d" % self.current_kills) 
        self.game.display(color.END, newLine = False)

    def give_xp(self, amount, printMessage = True):
        self.xp += amount
        if printMessage: self.game.display(color.CYAN + "+%d xp!" % amount + color.END)

    def take_xp(self, amount):
        self.xp -= amount
        self.game.display(color.CYAN + "-%d xp" % amount + color.END)

    def add_kill(self):
        self.current_kills += 1
        self.total_kills += 1
        self.kills_since_last_rank_up += 1
        if self.current_kills % 3 == 0:
            self.next_wave()
        if self.kills_since_last_rank_up % round(12*(1.1)**((self.rank - 1)/2)) == 0:
            return self.rank_up()

    def next_wave(self):
        self.wave += 1
        amount = self.wave + 2
        self.give_xp(amount, printMessage = False)
        self.game.display(color.CYAN + 'Wave %d, +%d xp' % (self.wave, amount) + color.END)

    def rank_up(self):
        self.rank += 1
        self.game.display(color.CYAN + 'Rank up! You are now rank %d. You unlocked a new combo.' % self.rank + color.END)
        return self.upgrade()

    def heal(self, amount):
        if amount and int(amount) > 0:
            amount = int(amount)
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

    def upgrade(self):
        if self.kick_upgrade >= self.max_upgrade and self.punch_upgrade >= self.max_upgrade:
            return

        self.game.display(color.CYAN + 'What would you like to upgrade? (punch or kick)' + color.END)
        return self.do_upgrade

    def do_upgrade(self, text):
        if self.kick_upgrade >= self.max_upgrade and self.punch_upgrade >= self.max_upgrade:
            return

        warning = color.YELLOW + '%s is at the max level.' + color.END
        skill = text.strip().lower()
        if skill == "kick":
            if self.kick_upgrade < self.max_upgrade:
                self.kick_upgrade += 1
            else:
                self.game.display(warning % "kick")
                return self.upgrade()
        elif skill == "punch":
            if self.punch_upgrade < self.max_upgrade:
                self.punch_upgrade += 1
            else:
                self.game.display(warning % "punch")
                return self.upgrade()
        else:
            self.game.display(color.YELLOW + "You can't upgrade that." + color.END)
            return self.upgrade()

        self.game.display(color.CYAN + '%s upgraded!' % skill + color.END)

        self.game.generate_zombie()
        self.game.print_prompt()


    def info_to_save(self):
        return (int(self.has_healed), self.number_of_games_played, self.punch_upgrade, self.kick_upgrade, self.total_kills, self.rank, self.kills_since_last_rank_up, int(self.new_game), self.current_kills, self.wave, self.xp, self.health, self.username)




