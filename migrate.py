#!/usr/bin/env python3

import sqlite3, os

DB_FILE = "zsd_data.db"
DID_EXIST = os.path.isfile(DB_FILE)

DB = sqlite3.connect(DB_FILE)

C = DB.cursor()

if not DID_EXIST:
    C.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username, password_hash, has_healed, number_of_games_played, punch_upgrade, kick_upgrade, total_kills, rank, kills_since_last_rank_up, new_game, current_kills, wave, xp, health)')
    C.execute("CREATE TABLE migrations (id INTEGER PRIMARY KEY AUTOINCREMENT, identifier, description)")

# random strings generated like so: ruby -e 'require "securerandom"; puts SecureRandom.base64'

C.execute("SELECT identifier FROM migrations WHERE identifier = '8pTt6l631OuLFmDpa5AIkw=='")
if not C.fetchone():
    C.execute("INSERT INTO migrations VALUES (NULL, '8pTt6l631OuLFmDpa5AIkw==', 'added statistics')")
    C.execute("CREATE TABLE stats (id INTEGER PRIMARY KEY AUTOINCREMENT, record, float_value, string_value)")
    C.execute("INSERT INTO stats VALUES (NULL, 'total kills', 0, NULL)")
    C.execute("INSERT INTO stats VALUES (NULL, 'total users', 0, NULL)")


DB.commit()


