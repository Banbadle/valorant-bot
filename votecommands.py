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
    async def addevent(self, ctx, event_name, default_value, event_category="Misc", cooldown=10, public="TRUE"):
        self.client.db.add_credit_event_type(event_name, 
                                             default_value,
                                             event_category=event_category,
                                             cooldown=cooldown,
                                             public=public)
        
    @commands.command()
    @commands.check(is_admin)
    async def modifyevent(self, ctx, event_name, column_name, new_value):
        self.client.db.modify_event(event_name, column_name, new_value)
        
    @commands.command()
    @commands.check(is_admin)
    async def changecategoryname(self, ctx, category_name_old, category_name_new):
        self.client.db.change_category_name(category_name_old, category_name_new)
        
async def setup(client):
    await client.add_cog(VoteCommands(client))