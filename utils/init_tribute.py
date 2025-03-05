from discord import User, Guild
from utils.connector import con, cur
def init_tribute(
    user: User,
    guild: Guild,
    game_id: int,
    nickname: str,
    pronouns: str,
) -> None:
    #TODO: go through messaged_tributes list and update status
    messaged_usr = cur.execute('''
        INSERT INTO (registered) SELECT * FROM messaged_users WHERE game_id = ? AND 
    ''')
    cur.execute('''
        INSERT INTO tributes (game_id, user_id, nickname, pronouns) VALUES (?, ?, ?, ?)
    ''', (game_id, user.id, nickname, pronouns,))