import discord
from discord_components import Button, ActionRow, ButtonStyle, SelectOption, Select
from discord.ext import commands
import sys
from checks import is_admin

CREDIT_NAME = "social credits"

class CreditVoting(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(sys.argv[0])


def setup(client):
    client.add_cog(CreditVoting(client))
