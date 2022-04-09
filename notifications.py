from discord_components import Select, SelectOption, Button, ActionRow, ButtonStyle
from discord.ext import commands

class Notifications(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("notifications.py loaded")
        
    @commands.command()
    async def notifications(self, ctx, arg=""):
        if arg.lower() == "on":
            self.client.db.set_notifications(ctx.author, 1)
            await ctx.reply("You have turned notifications on")
        elif arg.lower() == "off":
            self.client.db.set_notifications(ctx.author, 0)
            await ctx.reply("You have turned notifications off")
        else:
            status_bool = self.client.db.get_notifications(ctx.author.id)
            status = "on" if status_bool == 1 else "off"
            await ctx.reply(f"Your notifications are currently turned {status}.\nYou can change this setting using '?notifications on' or '?notifications off'")
        
def setup(client):
    client.add_cog(Notifications(client))