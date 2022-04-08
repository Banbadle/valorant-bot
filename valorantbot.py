import discord
from discord_components import Select, SelectOption, Button, ActionRow, ButtonStyle
import datetime
import time
import re
import sys
import pytz
from discord.ext import commands, tasks
from collections import defaultdict

import authordetails

import asyncio
import nest_asyncio
nest_asyncio.apply()

clock_map = {"✅":"Now","🕛":"12:00","🕧":"12:30","🕐":"01:00","🕜":"01:30","🕑":"02:00",\
             "🕝":"02:30","🕒":"03:00","🕞":"03:30","🕓":"04:00","🕟":"04:30","🕔":"05:00",\
                 "🕠":"05:30","🕕":"06:00","🕡":"06:30","🕖":"07:00","🕢":"07:30","🕗":"08:00",\
                     "🕣":"08:30","🕘":"09:00","🕤":"09:30","🕙":"10:00","🕥":"10:30","🕚":"11:00","🕦":"11:30","❌": None}

class ValorantBot(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        '''called when cog is loaded'''
        print(sys.argv[0])
        await self.checkin_loop() # Inital pass of checkin

    def get_ordered_emoji_list(self, start_time):
        '''returns an ordered list of emojis (corresponding to times after the given start_time), and a datetime object of the time of the first occurrence after start_time'''
        wait_time   = 5 + 29 - ((start_time.minute - 1) % 30)
        first_time  = start_time.replace(second=0, microsecond=0, minute=start_time.minute, hour=start_time.hour) + datetime.timedelta(minutes = wait_time - 5)

        emoji_list          = list(clock_map)[1:-1] * 2
        slice_emoji         = list(key for key, val in clock_map.items() if val == first_time.strftime("%I:%M"))[0]
        slice_index         = emoji_list.index(slice_emoji)
        ordered_emoji_list  = emoji_list[slice_index: slice_index+24]

        return ordered_emoji_list, first_time

    @tasks.loop(minutes = 30)
    async def checkin_loop(self):
        '''Loop to run checkin every 30 minutes'''
        grace_period = 5
        tz = pytz.timezone('Europe/London')
        curr_time = datetime.datetime.now(tz)
        wait_time = 30 - (((curr_time.minute - 1 - grace_period) % 30) + 1)

        print(f"current time: {curr_time}")
        print(f"wait time until execution: {wait_time} mins")
        await asyncio.sleep(wait_time * 60)

        new_time = curr_time.replace(second=0, microsecond=0, minute=curr_time.minute, hour=curr_time.hour) + datetime.timedelta(minutes = wait_time - grace_period)
        time_str = new_time.strftime("%I:%M")
        curr_emoji = list(key for key, val in clock_map.items() if val == time_str)[0]

        reaction_list = self.client.db.get_current_time_reactions(curr_emoji)

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

        if not self.client.db.get_users_in_voice(message_id): return           #Stop if no reacted users are in a voice channel

        for react_user_id in user_id_list:
            # Continue if reaction is by bot
            if react_user_id == self.client.user.id: continue

            voice_guild_id = self.client.db.get_user_voice_guild(react_user_id)
            if voice_guild_id: continue                                        # Do not add if user is in voice channel

            flake_list.append(react_user_id)

        if flake_list != []:
            channel_id  = self.client.db.get_channel_id(message_id)
            message     = await self.client.get_channel(channel_id).fetch_message(message_id)
            await self.post_checkin(message, flake_list)

        # for user_id in user_id_list:
        #     if user_id in flake_list:   self.client.db.add_social_credit(-200)
        #     else:                       self.client.db.add_social_credit(200)

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

    async def update_request_embed(self, message):
        '''Updates the request embed of message'''
        message_id = message.id
        start_datetime = self.client.db.get_creation_time(message_id)
        start_time = int(time.mktime(start_datetime.timetuple()))

        base_embed      = message.embeds[0]
        embed_dict      = base_embed.to_dict()
        new_field_list  = [embed_dict["fields"][0]]

        last_react_stamp = None
        unavailable_field = {'inline': False, 'name': ":x: (Unavailable)", 'value': ""}
        
        for reaction in self.client.db.get_reactions(message_id):
            react_stamp = reaction['react_stamp']
            
            if react_stamp == -1:
                unavailable_field["value"] += f"\n> <@{reaction['user']}>"
                continue
            
            if react_stamp != last_react_stamp:
                time_str = self.interact_val_to_str(react_stamp)
                e = "🕘" # ADJUST TO CLOSEST TIME EMOJI
                new_field_list.append({'inline': False, 'name': f"{e} ({time_str})", 'value': ""})
                
                last_react_stamp = react_stamp
                
            new_field_list[-1]["value"] += f"\n> <@{reaction['user']}>"
            
        if unavailable_field['value'] != "":
            new_field_list.append(unavailable_field)

        embed_dict["fields"] = new_field_list
        new_embed = discord.Embed.from_dict(embed_dict)

        await message.edit(embed=new_embed)

    async def post_checkin(self, trigger_message, user_id_list):

        newEmbed = discord.Embed(title="__Check In__", color=0xff8800)
        value_string = "\n".join([f"<@{user_id}>" for user_id in user_id_list])
        newEmbed.add_field(name="The following people reacted to the reqeust, but do not appear to have joined:", value=value_string, inline=False)

        author_text, author_icon = authordetails.get_author_pair()
        newEmbed.set_author(name=author_text, icon_url=author_icon)

        checkin_message = await trigger_message.reply(embed=newEmbed)

        self.client.db.add_message(checkin_message, trigger_message, 2)

        # await message.add_reaction("❌")
        # await message.add_reaction("✅")


    def is_request(self, message_id):
        return self.client.db.get_message_type(message_id) == 1

    def is_checkin(self, message_id):
        return self.client.db.get_message_type(message_id) == 2

    def get_blank_request_embed(self, author_name):
        new_embed = discord.Embed(title="__Valorant Request__", color=0xff0000)
        tz = pytz.timezone('Europe/London')
        curr_time = datetime.datetime.now(tz).strftime("%H:%M")
        new_embed.add_field(name=f"{author_name} wants to play Valorant", 
                            value=f"If interested, please select a time from the drop-down list.\n(This request was sent at {curr_time} UK Time)",
                            inline=False)
        new_embed.set_thumbnail(url="https://preview.redd.it/buzyn25jzr761.png?width=1000&format=png&auto=webp&s=c8a55973b52a27e003269914ed1a883849ce4bdc")

        return new_embed

    @commands.command()
    @commands.guild_only()
    async def valorant(self, ctx):
        '''Creates a valorant request message'''
        new_embed = self.get_blank_request_embed(ctx.author.name)

        agentsID = discord.utils.get(ctx.guild.roles,name="Agents").mention
        
        button_yes = Button(label="Select a Time", style=ButtonStyle(3), custom_id="rqst_yes")
        button_no  = Button(label="Unavailable", style=ButtonStyle(4), custom_id="rqst_no")
        button_row = ActionRow(button_no, button_yes)

        message = await ctx.reply(agentsID, embed=new_embed, components=[button_row])
        print("MESSAGE SENT")
    
        self.client.db.add_message(message, ctx.message, 1)
    
    async def update_reaction(self, interaction, message, new_timestamp):  
        user = interaction.user 
        message_id = message.id
        
        new_str = self.interact_val_to_str(new_timestamp)
        old_timestamp = self.client.db.get_user_reaction(message_id, user.id)
        old_str = self.interact_val_to_str(old_timestamp)
        if old_timestamp == new_timestamp:
            await interaction.send(content=f"You have already selected {old_str}")
            return
            
        if old_timestamp != None:
            self.client.db.remove_reaction(message_id, user.id, old_timestamp)
            
        self.client.db.add_reaction(message_id, user, new_timestamp)
        
        extra_string = f"\nYour previous response was: {old_str}" * (old_timestamp!=None)
        await interaction.send(content=f"You have responded with: {new_str}" + extra_string)
        
        await self.update_request_embed(message)
    
    async def send_request_time_list(self, interaction):
        t_step          = 15 * 60 #time step in seconds
        
        message_id      = interaction.message.id
        user_id         = interaction.user.id
        user_timezone   = pytz.timezone(self.client.db.get_timezone(user_id))
        creation_time   = self.client.db.get_creation_time(message_id)
        creation_unix   = time.mktime(creation_time.timetuple())
        
        first_timestamp = (int(creation_unix // t_step) + 1) * t_step
        
        option_list = [SelectOption(label = "Now", value = f"rqst_time_0_{message_id}")]
        for i in range(0,24):   
            new_timestamp = first_timestamp + t_step * i
            local_time = datetime.datetime.fromtimestamp(new_timestamp, user_timezone)
            
            time_str = local_time.strftime("%H:%M")
            new_select = SelectOption(label = f"{time_str}", value = f"rqst_time_{new_timestamp}_{message_id}")
            option_list.append(new_select)
    
        await interaction.send(content=f"Please select a time from the list.\nAll times are in '{user_timezone}' time.", components = [Select(placeholder= "Select a time", options=option_list)])
    
    def interact_val_to_str(self, val):
        if val == "0" or val == 0:  
            return "Now" 
        if val == "-1" or val == -1:
            return "Unavailable"
        
        return f"<t:{val}:t> (Local Time)"
    
    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        message_id = interaction.message.id

        if self.is_request(message_id):
            if interaction.custom_id == "rqst_yes":
                await self.send_request_time_list(interaction)
            elif interaction.custom_id == "rqst_no":
                await self.update_reaction(interaction, interaction.message, -1)          
    
    @commands.Cog.listener()
    async def on_select_option(self, interaction):
        val = interaction.values[0]
        
        RQST_PREFIX = "rqst_time"
        if val[0:len(RQST_PREFIX)] == RQST_PREFIX:
            _,_,timestamp,message_id = val.split("_")
            
            message = await interaction.channel.fetch_message(message_id)
            await self.update_reaction(interaction, message, timestamp)
            return
            
        if self.is_checkin(message_id):
            pass

    @commands.command()
    async def username(self, ctx):
        '''Sets valorant username and tag. eg: ?username FootGirl420#Euw'''
        print(ctx.message.content)
        match = re.fullmatch(r'\?username (?P<user>[^#]*)#(?P<tag>.{3,5})', ctx.message.content)
        print(match)
        if not match:
            return

        self.client.db.set_valorant_username(ctx.author.id, match.group('user'), match.group('tag'))

        await ctx.message.add_reaction("✅")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        message_id = payload.message_id
        channel_id = payload.channel_id

        if not self.client.db.is_message_in_db(message_id): return

        message = await self.client.get_channel(channel_id).fetch_message(message_id)
        self.client.db.remove_reaction(message_id, payload.user_id, payload.emoji.name)
        await self.update_request_embed(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        this_emoji  = payload.emoji.name
        channel_id  = payload.channel_id
        message_id  = payload.message_id
        user_id     = payload.user_id
        bot_id      = self.client.user.id

        if not self.client.db.is_message_in_db(message_id): return

        #If reaction was from bot
        if user_id == bot_id:
            return

        user = await self.client.fetch_user(user_id)
        message = await self.client.get_channel(channel_id).fetch_message(message_id)

        #Removes unwanted reactions
        if this_emoji not in clock_map:
            await message.remove_reaction(this_emoji, user)
            return

        # Check if there is already a reaction in the database
        if self.client.db.get_user_reaction(message_id, user_id):
            # Remove the new reaction if there is
            await message.remove_reaction(this_emoji, user)
            return

        # Add the new reaction to the database
        self.client.db.add_reaction(message_id, user, this_emoji)

        if self.is_request(message_id):
            print("Message: Request")
            await self.update_request_embed(message)

        elif self.is_checkin(message_id):
            print("Message: Check In")
            if this_emoji not in ["❌", "✅"]:
                await message.remove_reaction(payload.emoji, user)
                return

            await self.update_checkin_embed(message)

    @commands.Cog.listener()
    async def on_voice_state_update(self, user, leave, join):

        if join.channel != None:    self.client.db.user_join(user, join.channel)
        if leave.channel != None:   self.client.db.user_leave(user, leave.channel)

    @commands.Cog.listener()
    async def on_message_delete(self, ctx):
        msg = self.client.db.get_message_from_trigger(ctx.id)
        if not msg:
            return

        message = await ctx.channel.fetch_message(msg['id'])
        await message.delete()

def setup(client):
    client.add_cog(ValorantBot(client))
