from discord_components import Select, SelectOption, Button, ActionRow, ButtonStyle
from discord.ext import commands

class Notifications(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("notifications.py loaded")
        
    def interact_val_to_str(self, val):
        if val == "0" or val == 0:  
            return "Now" 
        if val == "-1" or val == -1:
            return "Unavailable"
        
        return f"<t:{val}:t>"
        
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

    async def notify_react(self, poster_user_id, poster_react_stamp, message_id,  guild_name):
        user_list = self.client.db.get_users_to_notify(message_id)
        for notify_user_id in user_list:
            if notify_user_id != poster_user_id:
                notify_user = self.client.get_user(notify_user_id)
                
                react_stamp_str = self.interact_val_to_str(poster_react_stamp)
                if react_stamp_str == "Unavailable":
                    await notify_user.send(f"<@{poster_user_id}> is now Unavailable.")
                    return
                await notify_user.send(f"<@{poster_user_id}> wants to play valorant " + "at "*(react_stamp_str!="Now") + f"{react_stamp_str} in {guild_name}.")
    
    @commands.Cog.listener()
    async def on_select_option(self, interaction):
        val = interaction.values[0]
        
        RQST_PREFIX = "rqst_time"
        if val[0:len(RQST_PREFIX)] == RQST_PREFIX:
            _,_,timestamp,message_id = val.split("_")
            poster_user_id = interaction.user.id
            guild_name = interaction.guild.name
            await self.notify_react(poster_user_id, timestamp, message_id, guild_name)    
            
    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        
        message_id = interaction.message.id
        guild_name = interaction.guild.name
        user_id = interaction.user.id
        
        old_timestamp = self.client.db.get_user_reaction(message_id, interaction.user.id)
        
        if interaction.custom_id == "rqst_no":
            if old_timestamp != -1:
                await self.notify_react(user_id, -1, message_id, guild_name) 
        
def setup(client):
    client.add_cog(Notifications(client))