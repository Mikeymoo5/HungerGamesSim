from utils.connector import con, cur
from utils import secrets
from discord import Guild
import time
def init_guild(
        api_key: int, 
        model_name: str, 
        channel_id: str, 
        gamemaker_role_id: str,
        tribute_role_id: str,
        guild: Guild):
    
    # Remove the guild from the DB if it already exists
    cur.execute('''
        DELETE FROM guilds WHERE guild_id = ?;
    ''', (guild.id,))
    cur.execute('''
        DELETE FROM settings WHERE guild_id = ?;
    ''', (guild.id,))

    cur.execute('''
        INSERT INTO guilds (guild_id, guild_name, joined_on, last_seen) VALUES (?, ?, ?, ?);
    ''', (guild.id, guild.name, time.time(), time.time()))
    cur.execute('''
        INSERT INTO settings (guild_id, api_key, llm_model, announcement_channel, gamemaker_role, tribute_role) VALUES (?, ?, ?, ?, ?, ?);
    ''', (guild.id, api_key, model_name, channel_id, gamemaker_role_id, tribute_role_id))
    con.commit()
    