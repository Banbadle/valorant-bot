import discord
import datetime
import time
from discord.ext import commands, tasks
from collections import defaultdict

import authordetails

import asyncio
import nest_asyncio

class CheckInCog(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        '''called when cog is loaded'''
        print("checkin.py loaded")
        await self.checkin_loop() # Inital pass of checkin
        
    @tasks.loop(minutes = 15)
    async def checkin_loop(self):
        '''Loop to run checkin every 15 minutes'''
        MINUTES = 15
        GRACE_PERIOD = 3
        
        curr_timestamp = int(time.time())
        wait_time = (MINUTES*60) - (curr_timestamp % (MINUTES*60)) + GRACE_PERIOD*60

        react_stamp = curr_timestamp + wait_time - GRACE_PERIOD*60

        print(f"current time: {datetime.datetime.now()}")
        print(f"wait time until execution: {wait_time//60} mins, {wait_time % 60} seconds")
        await asyncio.sleep(wait_time)

        reaction_list = self.client.db.get_current_time_reactions(react_stamp)

        msg_dict = defaultdict(list)
        for message_id, user_id in reaction_list:
            msg_dict[message_id].append(user_id)

        for message_id, user_id_list in msg_dict.items():
            await self.checkin(message_id, user_id_list)

    async def checkin(self, message_id, user_id_list):
        '''checks for people who are "late" and responds if appropriate'''

        print("CHECKING IN")
        print(message_id)
        print(user_id_list)

        guild_id = self.client.db.get_guild_id(message_id)

        flake_list = []
        
        #Stop if no reacted users are in a voice channel
        if not self.client.db.get_users_in_voice(message_id): 
            return           

        for react_user_id in user_id_list:

            voice_guild_id = self.client.db.get_user_voice_guild(react_user_id)
            if not voice_guild_id:                             
                flake_list.append(react_user_id)

        if flake_list != []:
            channel_id  = self.client.db.get_channel_id(message_id)
            message     = await self.client.get_channel(channel_id).fetch_message(message_id)
            await self.post_checkin(message, flake_list)
            


    async def update_checkin_embed(self, message):
        '''Updates the checkin embed of message'''
        embed = message.embeds[0]
        embedDic = embed.to_dict()
        newFieldList = [embedDic["fields"][0]]
        newFieldList.append({'inline': False, 'name': "__Coming Now__", 'value': "\u200b"})
        newFieldList.append({'inline': True, 'name': "__Need More Time__", 'value': "\u200b"})
        newFieldList.append({'inline': True, 'name': "__Not Coming__", 'value': "\u200b"})

        for react in message.reactions:
            pass
        
    async def post_checkin(self, trigger_message, user_id_list):

        newEmbed = discord.Embed(title="__Check In__", color=0xff8800)
        value_string = "\n".join([f"<@{user_id}>" for user_id in user_id_list])
        newEmbed.add_field(name="The following people reacted to the reqeust, but do not appear to have joined:", value=value_string, inline=False)

        author_text, author_icon = authordetails.get_author_pair()
        newEmbed.set_author(name=author_text, icon_url=author_icon)

        checkin_message = await trigger_message.reply(embed=newEmbed)

        self.client.db.add_message(checkin_message, trigger_message, 2)
        
async def setup(client):
    await client.add_cog(CheckInCog(client))