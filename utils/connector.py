import sqlite3
import json

# Access the DB if it exists, otherwise create it
con = sqlite3.connect('database.db')
con.row_factory = sqlite3.Row
# Create a cursor object using the cursor() method
cur = con.cursor()

# Initialize the database if it does not contain the required tables
# Required tables: guilds, settings, games, tributes

# Get a list of all table names as strings
# TODO: this might(?) run every import of connector
tables_result = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
table_names = [table[0] for table in tables_result]

if 'guilds' not in table_names:
    cur.execute('''
        CREATE TABLE IF NOT EXISTS guilds (
            guild_id INTEGER PRIMARY KEY UNIQUE,
            guild_name TEXT,
            joined_on TIMESTAMP,
            last_seen TIMESTAMP,
            active_game INT
        );
    ''')
if 'settings' not in table_names:
    cur.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            guild_id INTEGER PRIMARY KEY UNIQUE,
            api_key TEXT,
            llm_model TEXT,
            announcement_channel TEXT,
            gamemaker_role TEXT,
            tribute_role TEXT,
            FOREIGN KEY(guild_id) REFERENCES guilds(guild_id)
        );
    ''')
if 'games' not in table_names:
    cur.execute('''
        CREATE TABLE IF NOT EXISTS games (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            guild_id INTEGER,
            game_num INTEGER,
            arena TEXT,
            status int,
            created_on TIMESTAMP,
            started_on TIMESTAMP,
            FOREIGN KEY(guild_id) REFERENCES guilds(guild_id)
        );
    ''')
if 'tributes' not in table_names:
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tributes (
            tribute_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            game_id INTEGER,
            handle TEXT,
            nickname TEXT,
            pronouns TEXT,
            attribute TEXT,
            status TEXT,
            inventory TEXT,
            alive BOOLEAN,
            FOREIGN KEY(game_id) REFERENCES games(game_id)
        );
    ''')

if 'messaged_users' not in table_names:
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messaged_users (
            game_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            registered BOOLEAN,
            tribute_id INTEGER,
            FOREIGN KEY(game_id) REFERENCES games(game_id)
        )           
    ''')
# Commit the changes
con.commit()