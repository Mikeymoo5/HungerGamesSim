import discord
from litellm import acompletion
from utils import secrets
from views.guild_setup_flow import SetupFlow
from views.tribute_setup_flow import TributeSetupFlow
from views.game_setup_flow import GameModal
import json
import sqlite3
from utils.connector import cur, con
from  templates.response_schema import ResponseSchema
import inflect
import time

# Init the discord bot
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
bot = discord.Bot(intents=intents)

# Connect to the database
# con = sqlite3.connect('database.db')
# cur = con.cursor()

# Load the system prompt
SYSTEM_PROMPT: str = None
with open('templates/system_prompt.txt') as f:
    SYSTEM_PROMPT = f.read()
    f.close()

# Inflection engine
I_ENGINE = inflect.engine()

# Load the response schema
# RESPONSE_SCHEMA: json = None
# with open('templates/response_schema.json') as f:
#     RESPONSE_SCHEMA = json.load(f)
#     f.close()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.event
async def on_guild_join(guild: discord.Guild):
    print(f"Joined guild: {guild.name}")
    system_channel = guild.system_channel
    if system_channel.permissions_for(guild.me).send_messages:
        await system_channel.send("Succesfully joined server. Please run /init to enter the setup wizard.")    

@bot.slash_command(name="init", description="Initialize the bot for the current server.", guild_ids=[1344427022377549946])
@discord.commands.default_permissions(administrator=True)
async def server_init(ctx: discord.ApplicationContext):
    # Create the view
    view = SetupFlow(ctx.author)
    # Send it to the user (using await)
    await ctx.respond("Please configure your guild.", view=view)  # This needs to be awaited

@bot.slash_command(name="create_game", description="Create a new game.", guild_ids=[1344427022377549946,])
async def create_game(ctx: discord.ApplicationContext):
    guild: discord.Guild = ctx.guild
    gm_id = cur.execute("SELECT gamemaker_role FROM settings WHERE guild_id = ?;", (guild.id,)).fetchall()[0][0]
    if not any(role.id == int(gm_id) for role in ctx.author.roles):
        await ctx.respond("You must be a game maker to run this command.")
        return
    
    # TODO: Implement game setup wizard
    game_modal = GameModal(title="Create a game")
    await ctx.send_modal(game_modal)
    await game_modal.wait() # Wait for the user to submit the modal
    game_num = game_modal.num
    game_description = game_modal.description

    # Create the game in the database
    # Status is an int, which will be parsed into an enum. 0=created 1=in-progress 2=finished
    # Would normally have a started on time but that is being omitted here - It should only have a value if it has already been started
    cur.execute("INSERT INTO games (guild_id, game_num, arena, status, created_on) VALUES (?, ?, ?, ?, ?)",
        (guild.id, game_num, game_description, 0, time.time(),)
    )

    game_id = cur.lastrowid # TODO: use a new cursor for this
    con.commit()

    # Send messages to users asking for name and pronouns
    tribute_id = cur.execute("SELECT tribute_role FROM settings WHERE guild_id = ?;", (guild.id,)).fetchall()[0][0]
    #TODO: tf is this
    tribute_role = guild.get_role(int(tribute_id))
    users = tribute_role.members
    game_num = 1
    for u in users:
        view = TributeSetupFlow(game_id) #TODO: pass in the game_id

        # Creates a row in the tributes table - This is done prior to the tribute's input to keep tally of who has yet to enter their information
        cur.execute('''
            INSERT INTO tributes (game_id, user_id, registered) VALUES (?, ?, 0)
        ''', (game_id, u.id,))
        con.commit()
        await u.send(f"{u.mention} has been selected to partake in *{guild.name}'s {I_ENGINE.ordinal(game_num)} annual Hunger Game.", view=view)
    await ctx.respond(f"The game has been created, and messages have been sent to all tributes. Your game ID is {game_id}. Please remember it as you cannot start the game without it.")
    
@bot.slash_command(name="start_game", description="Start a game", guild_ids=[1344427022377549946,])
@discord.option("game_id", type=discord.SlashCommandOptionType.integer)
async def start_game(ctx: discord.ApplicationContext, game_id: int):
    #TODO: Run tribute check. Convert to view with cancel and start anyways button if not all tributes are setup.
    #TODO: Make sure the guild this is being started in is the guild the game was created in
    guild: discord.Guild = ctx.guild
    gm_id = cur.execute("SELECT gamemaker_role FROM settings WHERE guild_id = ?;", (guild.id,)).fetchall()[0][0]
    if not any(role.id == int(gm_id) for role in ctx.author.roles):
        await ctx.respond("You must be a game maker to run this command.")
        return
    await ctx.defer(ephemeral=False)

    # Horrible naming scheme. A list of tributes who have yet to fill out the tribute modal
    awaiting_tributes = cur.execute("SELECT * FROM tributes WHERE game_id = ? AND registered = 0", (game_id,)).fetchall()
    if len(awaiting_tributes) > 0:
        ihatemyselfstring = ""
        for row in awaiting_tributes:
            mention = bot.get_user(int(row['user_id'])).name
            ihatemyselfstring = ihatemyselfstring + f"{mention},"
        #TODO: make the last user have ,and instead of , and also fix the beginning
        print(f"IHATEMYSELF STRING: {ihatemyselfstring}")
        await ctx.respond(f"Unable to start the game. The following tributes have yet to verify their identity: {ihatemyselfstring}")
        return
    print(f"AWAITING ON THESE TRIBUTES: {awaiting_tributes}")
    game = cur.execute("SELECT * FROM games WHERE game_id = ?;", (game_id,)).fetchone()
    description = game['arena']
    
    model = cur.execute("SELECT llm_model FROM settings WHERE guild_id = ?;", (guild.id,)).fetchall()[0][0]
    api_key = cur.execute("SELECT api_key FROM settings WHERE guild_id = ?;", (guild.id,)).fetchall()[0][0]

    tribute_role_id = cur.execute("SELECT tribute_role FROM settings WHERE guild_id = ?;", (guild.id,)).fetchall()[0][0]

    tribute_role = guild.get_role(int(tribute_role_id))
    users = tribute_role.members

    completion = await acompletion(
        model=model,
        api_key=api_key,
        temperature=1,
        response_format=ResponseSchema,
        max_tokens=4096,
        messages=[
            {
                "role": "system", 
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": "Arena description: " + description + "\nList of users: " + str(users) + "\nInstructions: Start on day 1 at the cornucopia."
            }
            ]
    )
    response_raw = completion.choices[0].message.content
    print(response_raw)
    response: ResponseSchema = ResponseSchema.model_validate_json(response_raw)
    # for e in test.events:
    #     print(f"EVENT: {str(e.summary)}")
    events = response.events
    events_string =  "\n\n".join([str(e.summary) + f" @ {str(e.time.hour)}:{str(e.time.minute)}" for e in events])
    await ctx.followup.send(events_string, ephemeral=False)
print("Running the bot...")
bot.run(secrets.BOT_TOKEN)