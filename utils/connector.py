import sqlite3
import json

# Access the DB if it exists, otherwise create it
con = sqlite3.connect('database.db')

# Create a cursor object using the cursor() method
cur = con.cursor()

# Initialize the database if it does not contain the required tables
# Required tables: guilds, settings, games, tributes

# Get a list of all table names as strings
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
            tribute_role TEXT
        );
    ''')
if 'games' not in table_names:
    cur.execute('''
        CREATE TABLE IF NOT EXISTS games (
            game_id INTEGER PRIMARY KEY UNIQUE ,
            guild_id INTEGER,
            game_name TEXT,
            created_on TIMESTAMP,
            started_on TIMESTAMP
        );
    ''')
if 'tributes' not in table_names:
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tributes (
            tribute_id INTEGER PRIMARY KEY UNIQUE,
            game_id INTEGER,
            handle TEXT,
            nickname TEXT,
            attribute TEXT,
            status TEXT,
            inventory TEXT,
            alive BOOLEAN
        );
    ''')

# Commit the changes
con.commit()