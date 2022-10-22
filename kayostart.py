import discord
from discord_components import ComponentsBot
import os
from discord.ext import commands
from database import Database
from checks import is_admin
import toml
from git import Repo
import requests

import nest_asyncio
nest_asyncio.apply()

with open('config.toml', 'r') as f:
    config = toml.loads(f.read())

client = ComponentsBot(command_prefix='?', case_insensitive=True, intents=discord.Intents.all())

client.db = Database()

@client.command()
@commands.check(is_admin)
async def load(ctx, extension):
    client.load_extension(extension)

@client.command()
@commands.check(is_admin)
async def unload(ctx, extension):
    client.unload_extension(extension)

@client.command()
@commands.check(is_admin)
async def version(ctx):
    repo = Repo(os.getcwd())
    hash = repo.head.commit.binsha.hex()[:7]
    await ctx.reply(f"`{hash}`")

@client.command()
@commands.check(is_admin)
async def setbotname(ctx, name):
    await client.user.edit(username=name)

@client.command()
@commands.check(is_admin)
async def setbotimage(ctx, url):
    img = requests.get(url).content
    await client.user.edit(avatar=img)

@client.event
async def on_command_error(ctx, error):
    if type(error) in [
        commands.CheckFailure,
        commands.CommandOnCooldown
    ]:
        await ctx.message.add_reaction("❌")

@client.event
async def on_command_completion(ctx):
    await ctx.message.add_reaction("✅")

load_list = ["valorantranks.py", "randomselections.py", "valorantbot.py", "timezones.py", "notifications.py", "stratroulette.py", "sweepstake.py"]

for filename in os.listdir(os.getcwd()):
    if filename in load_list:
        load_list.remove(filename)
        client.load_extension(filename[:-3])

if len(load_list) != 0:
    print(f"The following cogs were not found in the current directory, and have not been loaded:\n{load_list}")

client.run(config['discord']['key'])
