import discord
import datetime
import time
import re
import sys
import pytz
from discord.ext import commands, tasks
from discord.ui import Button, Select, View
from discord import SelectOption, ButtonStyle
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
        self.request_view = self.RequestView(self)
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
                if time_str == "Now":
                    e = "✅"
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
        new_embed.add_field(name=f"{author_name} wants to play Valorant", 
                            value="Please respond using the appropriate button.",
                            inline=False)
        new_embed.set_thumbnail(url="https://preview.redd.it/buzyn25jzr761.png?width=1000&format=png&auto=webp&s=c8a55973b52a27e003269914ed1a883849ce4bdc")

        return new_embed

    @commands.command(help = "Creates a game request message for a given rank")
    @commands.guild_only()
    async def game(self, ctx, rank_name):
        '''Creates a game request message for a given rank'''
        author_name = ctx.author.name
        
        discord_rank = discord.utils.get(ctx.guild.roles,name=rank_name)
        if discord_rank == None:
            await ctx.reply(f"I couldn't find any rank called '{rank_name}', please try again. Note that ranks are case sensitive.")
            return
            
        discord_rank_id = discord_rank.mention
        discord_rank_color = discord_rank.color
        
        new_embed = discord.Embed(title=f"__{rank_name} Request__", color=discord_rank_color)
        new_embed.add_field(name=f"{author_name} wants to play", 
                            value="Please respond using the appropriate button.",
                            inline=False)

        button_yes = Button(label="Select a Time", style=ButtonStyle(3), custom_id="rqst_yes")
        button_no  = Button(label="Unavailable", style=ButtonStyle(4), custom_id="rqst_no")
        button_row = ActionRow(button_no, button_yes)

        message = await ctx.reply(discord_rank_id, embed=new_embed, components=[button_row])
    
        self.client.db.add_message(message, ctx.message, 1)

    class RequestView(View):
        
        def __init__(self, base_cog):
            self.base_cog = base_cog
            super().__init__(timeout=None)
            
            unavailable_button = self.base_cog.UnavailableRequestButton()
            select_time_button = self.base_cog.TimeRequestButton()
            
            self.add_item(unavailable_button)
            self.add_item(select_time_button)

    class UnavailableRequestButton(Button):
        
        def __init__(self):
            super().__init__(style=ButtonStyle.red, label="Unavailable", custom_id="request_Unavailable")
        
        async def callback(self, interaction):
            await self.view.base_cog.update_reaction(interaction, interaction.message, -1) 
        
    class TimeRequestButton(Button):
        
        def __init__(self):
            super().__init__(style=ButtonStyle.green, label="Select a Time", custom_id="request_Select_Time")
        
        async def callback(self, interaction):
            await self.view.base_cog.send_request_time_list(interaction)

    @commands.command(help = "Creates a valorant request message")
    @commands.guild_only()
    async def valorant(self, ctx):
        '''Creates a valorant request message'''
        new_embed = self.get_blank_request_embed(ctx.author.name)

        agentsID = discord.utils.get(ctx.guild.roles,name="Agents").mention

        message = await ctx.reply(content=agentsID, embed=new_embed, view=self.request_view)
        print("MESSAGE SENT")
    
        self.client.db.add_message(message, ctx.message, 1)
    
    async def update_reaction(self, interaction, message, new_timestamp):  
        user = interaction.user 
        message_id = message.id
        
        new_str = self.interact_val_to_str(new_timestamp)
        old_timestamp = self.client.db.get_user_reaction(message_id, user.id)
        old_str = self.interact_val_to_str(old_timestamp)
        if old_timestamp == new_timestamp:
            await interaction.response.send_message(content=f"You have already selected {old_str}")
            return
            
        if old_timestamp != None:
            self.client.db.remove_reaction(message_id, user.id, old_timestamp)
            
        self.client.db.add_reaction(message_id, user, new_timestamp)
        
        extra_string = f"\nYour previous response was: {old_str}" * (old_timestamp!=None)
        await interaction.response.send_message(content=f"You have responded with: {new_str}" + extra_string)
        
        await self.update_request_embed(message)
    
    async def send_request_time_list(self, interaction):
        t_step          = 15 * 60 #time step in seconds
        
        message_id      = interaction.message.id
        user            = interaction.user
        user_timezone   = pytz.timezone(self.client.db.get_timezone(user))
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
    
        await interaction.send(content=f"Please select a time from the list.\nAll times are in '{user_timezone}' time. To change this, use '?timezone'", components = [Select(placeholder= "Select a time", options=option_list)])
    
    def interact_val_to_str(self, val):
        if val == "0" or val == 0:  
            return "Now" 
        if val == "-1" or val == -1:
            return "Unavailable"
        
        return f"<t:{val}:t>"
    
    @commands.Cog.listener()
    async def on_button_click(self, interaction):

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
            
        message_id = interaction.message.id
        if self.is_checkin(message_id):
            pass

    @commands.command(help = "Sets valorant username and tag.\n" +\
                      "parameters:\n    username: the username and tag, separated by '#'\n" +\
                      "Example: ?username FootGirl420#Euw")
    async def username(self, ctx, username):
        '''Sets valorant username and tag.'''
        print(username)
        match = re.fullmatch(r'(?P<user>[^#]*)#(?P<tag>.{3,5})', username)
        print(match)
        if not match:
            return

        self.client.db.set_valorant_username(ctx.author.id, match.group('user'), match.group('tag'))

        await ctx.message.add_reaction("✅")


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

async def setup(client):
    await client.add_cog(ValorantBot(client))
