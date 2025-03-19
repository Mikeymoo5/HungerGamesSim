from discord import User, Guild
from utils.connector import con, cur
def init_tribute(
    user: User,
    guild: Guild,
    game_id: int,
    nickname: str,
    pronouns: str,
) -> None:
    cur.execute('''
        UPDATE tributes 
        SET nickname = ?, pronouns = ?, registered = 1
        WHERE game_id = ? AND user_id = ?
    ''', (nickname, pronouns, game_id, user.id))
    # return cur.lastrowid