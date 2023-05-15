from discord.ext import commands
from discord import app_commands, Interaction
from checks import is_admin
import discord

class VoteCommands(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        
        print("votecommands.py loaded")
async def setup(client):
    await client.add_cog(VoteCommands(client))