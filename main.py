import discord
from litellm import acompletion
from utils import secrets
from views.setup_flow import SetupFlow  # Make sure the class name matches exactly
import json
import sqlite3

# Init the discord bot
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
bot = discord.Bot(intents=intents)

# Connect to the database
con = sqlite3.connect('database.db')
cur = con.cursor()

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
    users = [m.id for m in tribute_role.members]
    await ctx.respond(users)
    
@bot.slash_command(name="start_game", description="Start a game", guild_ids=[1344427022377549946,])
async def start_game(ctx: discord.ApplicationContext):
    guild: discord.Guild = ctx.guild
    gm_id = cur.execute("SELECT gamemaker_role FROM settings WHERE guild_id = ?;", (guild.id,)).fetchall()[0][0]
    if not any(role.id == int(gm_id) for role in ctx.author.roles):
        await ctx.respond("You must be a game maker to run this command.")
        return
    await ctx.defer(ephemeral=True)
    model = cur.execute("SELECT llm_model FROM settings WHERE guild_id = ?;", (guild.id,)).fetchall()[0][0]
    api_key = cur.execute("SELECT api_key FROM settings WHERE guild_id = ?;", (guild.id,)).fetchall()[0][0]

    completion = await acompletion(
        model=model,
        api_key=api_key,
        temperature=2,
        max_tokens=250,
        messages=[{"role": "user", "content": "tell the user -in a quirky way- that this function is NOT implemented yet, ocasionally using funny math related jokes, preferably from a pre-calc class. be AS FUNNY AS POSSIBLE, APPEALING TO AN AUDIENCE OF HIGH-SCHOOLERS"}]
    )
    response = completion.choices[0].message.content
    await ctx.followup.send(response)
print("Running the bot...")
bot.run(secrets.BOT_TOKEN)