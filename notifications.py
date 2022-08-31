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
        
    @commands.command(help = "View and change whether you recieve notifications from KAY/O.\n"+\
                      "With notifications on, KAY/O will send private messages to you when someone responds to a message you have expressed interest in.\n"
                      "parameters:\n    arg: 'on', 'off', or None")
    async def notifications(self, ctx, arg=""):
        '''View and change whether you recieve notifications from KAY/O.'''
        if arg.lower() == "on":
            self.client.db.set_notifications(ctx.author, 1)
            await ctx.reply("You have turned notifications on")
        elif arg.lower() == "off":
            self.client.db.set_notifications(ctx.author, 0)
            await ctx.reply("You have turned notifications off")
        else:
            status_bool = self.client.db.get_notifications(ctx.author)
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
                await notify_user.send(f"<@{poster_user_id}> also wants to play " + "at "*(react_stamp_str!="Now") + f"{react_stamp_str} in {guild_name}.")
                
    # async def notify_join(self, join_user_id, join_channel):
    #     user_set = set()
    #     join_guild = join_channel.guild
    #     guild_name = join_guild.name
        
    #     print(join_guild.id)
    #     message_id_list = self.client.db.get_active_messages(join_guild.id)
    #     for message_id in message_id_list:
    #         user_list = self.client.db.get_users_to_notify(message_id)
    #         for react_user in user_list:
    #             user_set.add(react_user)

    #     for notify_user_id in user_set:
    #         if notify_user_id != join_user_id:
    #             if self.client.db.get_user_voice_guild(message_id) != join_guild:
    #                 notify_user = self.client.get_user(notify_user_id)
    #                 await notify_user.send(f"<@poster_user_id> has joined a voice channel in {guild_name}")

    # @commands.Cog.listener()
    # async def on_voice_state_update(self, user, leave, join):

    #     new_channel = None if join == None else join.channel
    #     old_channel = None if leave == None else leave.channel
        
    #     new_guild = None if new_channel == None else new_channel.guild
    #     old_guild = None if old_channel == None else old_channel.guild
        
    #     if new_guild == old_guild: 
    #         return
        
    #     if new_channel != None:
    #         await self.notify_join(user.id, new_channel)
    
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