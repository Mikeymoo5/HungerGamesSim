import discord
from litellm import acompletion
from utils import secrets
from views.guild_setup_flow import SetupFlow
from views.game_setup_flow import GameFlow
import json
import sqlite3
from  templates.response_schema import ResponseSchema

# Init the discord bot
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
bot = discord.Bot(intents=intents)

# Connect to the database
con = sqlite3.connect('database.db')
cur = con.cursor()

# Load the system prompt
SYSTEM_PROMPT: str = None
with open('templates/system_prompt.txt') as f:
    SYSTEM_PROMPT = f.read()
    f.close()

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
    
    tribute_id = cur.execute("SELECT tribute_role FROM settings WHERE guild_id = ?;", (guild.id,)).fetchall()[0][0]

    tribute_role = guild.get_role(int(tribute_id))
    users = tribute_role.members

    for u in users:
        view = GameFlow()
        await u.send("We regret to inform you that you have been chosen to participate in the Hunger Games. Please confirm your identity.", view=view)
    await ctx.respond("Sent messages to all tributes.")
    
@bot.slash_command(name="start_game", description="Start a game", guild_ids=[1344427022377549946,])
async def start_game(ctx: discord.ApplicationContext):
    guild: discord.Guild = ctx.guild
    gm_id = cur.execute("SELECT gamemaker_role FROM settings WHERE guild_id = ?;", (guild.id,)).fetchall()[0][0]
    if not any(role.id == int(gm_id) for role in ctx.author.roles):
        await ctx.respond("You must be a game maker to run this command.")
        return
    await ctx.defer(ephemeral=False)
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
                "content": str(users) + "\nStart on day 1 at the cornucopia."
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