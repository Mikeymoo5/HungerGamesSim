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
    cur.execute('''
        INSERT INTO tributes (game_id, handle, nickname, pronouns) VALUES (?, ?, ?, ?)
    ''', ())