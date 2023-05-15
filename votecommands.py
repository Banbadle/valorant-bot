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
    @commands.command()
    @commands.check(is_admin)
    async def modifyevent(self, ctx, event_name, column_name, new_value):
        self.client.db.modify_event(event_name, column_name, new_value)
        
async def setup(client):
    await client.add_cog(VoteCommands(client))