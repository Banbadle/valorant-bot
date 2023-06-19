import discord
import os
from discord.ext import commands
from database import Database
from checks import is_admin, slash_is_admin
import toml
from git import Repo
import requests
import asyncio

import nest_asyncio
nest_asyncio.apply()

with open('config.toml', 'r') as f:
    config = toml.loads(f.read())

client = commands.Bot(command_prefix='?', case_insensitive=True, intents=discord.Intents.all())

client.db = Database()

@client.command()
@commands.check(is_admin)
async def sync(ctx):
    await client.tree.sync()

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
async def sendmsg(ctx, *, msg):
    await ctx.send(msg)

@client.command()
@commands.check(is_admin)
async def setbotimage(ctx, url):
    img = requests.get(url).content
    await client.user.edit(avatar=img)
    
@client.tree.command()
@commands.check(slash_is_admin)
async def sqlforce(interaction: discord.Interaction, query: str):
    client.db.set_sql_query(query)
    await interaction.response.send_message("Query Completed", ephemeral=True)

@client.tree.command()
@commands.check(slash_is_admin)
async def sqlget(interaction: discord.Interaction, query: str):
    output = client.db.return_sql_query(query)
    if not output:
        await interaction.response.send_message(content="Query returned nothing", ephemeral=True)
        
    output_dict = {key: [] for key in output[0]}
        
    for res in output:
        for key, val in res.items():
            output_dict[key].append(str(val))
    new_embed = discord.Embed(title="Query Result")
    for key, vals in output_dict.items():
        new_embed.add_field(name=key, value="\n".join(vals), inline=True)
    
    await interaction.response.send_message(embed=new_embed, ephemeral=True)


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

async def load_cogs():

    load_list = ["valorantranks.py", 
                 "randomselections.py", 
                 "valorantbot.py", 
                 "timezones.py", 
                 "notifications.py", 
                 "stratroulette.py", 
                 "creditvoting.py",
                 "votecommands.py",
                 "games.blackjack.py"]
    
    for filename in load_list:
        try:
            await client.load_extension(filename[:-3])
        except commands.ExtensionNotFound:
            print(f"Could not find {filename}")

async def start():
    await load_cogs()
    await client.run(config['discord']['key'])
    
asyncio.run(start())



