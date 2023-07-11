import discord
import datetime
import time
import re
import sys
import pytz
from discord.ext import commands
from discord.ui import Button, Select, View
from discord import SelectOption, ButtonStyle

import asyncio
import nest_asyncio
nest_asyncio.apply()

class ValorantBot(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        '''called when cog is loaded'''
        print("valorantbot.py loaded")
        self.request_view = self.RequestView(self)
        self.client.add_view(self.request_view)

    async def update_request_embed(self, message):
        '''Updates the request embed of message'''
        message_id = message.id

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
                e = "✅" if time_str == "Now" else "🕘"
                new_field_list.append({'inline': False, 'name': f"{e} ({time_str})", 'value': ""})
                
                last_react_stamp = react_stamp
                
            extra_str = ""     
            if react_stamp == 0:
                stamp = (reaction['timestamp'])
                unix_timestamp = int(datetime.datetime.timestamp(stamp))
                extra_str = f" -(<t:{unix_timestamp}:t>)"
                
            new_field_list[-1]["value"] += f"\n> <@{reaction['user']}>" + extra_str
            
        if unavailable_field['value'] != "":
            new_field_list.append(unavailable_field)

        embed_dict["fields"] = new_field_list
        new_embed = discord.Embed.from_dict(embed_dict)

        await message.edit(embed=new_embed)

    def get_blank_request_embed(self, author_name, rank="Valorant", embed_color=0xff0000):
        new_embed = discord.Embed(title=f"__{rank} Request__", color=embed_color)
        new_embed.add_field(name=f"{author_name} wants to play", 
                            value="Please respond using the appropriate button.",
                            inline=False)
        
        if rank == "Valorant":
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
        
        new_embed = self.get_blank_request_embed(
            author_name, 
            rank= rank_name.capitalize(),
            embed_color= discord_rank_color)

        message = await ctx.reply(content=discord_rank_id, embed=new_embed, view=self.request_view)
    
        self.client.db.add_message(message, ctx.message, 1)

    class RequestView(View):
        
        def __init__(self, base_cog):
            self.base_cog = base_cog
            super().__init__(timeout=None)
            
            unavailable_button  = self.base_cog.ResponseRequestButton(self.base_cog, -1)
            select_time_button  = self.base_cog.TimeRequestButton(self.base_cog)
            now_button          = self.base_cog.ResponseRequestButton(self.base_cog, 0)
            
            self.add_item(unavailable_button)
            self.add_item(select_time_button)
            self.add_item(now_button)

    class ResponseRequestButton(Button):
        
        def __init__(self, base_cog, stamp):
            self.base_cog   = base_cog
            self.stamp      = stamp if stamp==0 else -1
            
            button_style    = ButtonStyle.green if stamp==0 else ButtonStyle.red
            button_label    = "Now" if stamp==0 else "Unavailable"
            
            super().__init__(
                style=button_style,
                label=button_label, 
                custom_id=button_label)
        
        async def callback(self, interaction):
            msg = interaction.message
            await self.base_cog.update_reaction(interaction, msg, self.stamp) 
        
    class TimeRequestButton(Button):
        
        def __init__(self, base_cog):
            self.base_cog = base_cog
            super().__init__(
                style=ButtonStyle.blurple, 
                label="Select a Time", 
                custom_id="request_Select_Time")
        
        async def callback(self, interaction):
            time_select = self.base_cog.TimeListSelect(self.base_cog, interaction)
            
            view = View()
            view.add_item(time_select)
            
            user            = interaction.user
            user_tz_str     = self.base_cog.client.db.get_timezone(user)
            user_tz         = pytz.timezone(user_tz_str)
            
            await interaction.response.send_message(
                content="Please select a time from the list." +"\n" 
                +f"All times are in '{user_tz}' time." + "\n" 
                +"To change this, use '?timezone'", 
                view= view,
                ephemeral=True)
            
    class TimeListSelect(Select):
        def __init__(self, base_cog, interaction):
            self.base_cog   = base_cog
            self.message_id = interaction.message.id
            option_list = self.base_cog.get_request_time_list(interaction)
                
            super().__init__(
                placeholder="Select a Time", 
                min_values=1, 
                max_values=1, 
                options=option_list)
        
        async def callback(self, interaction):
            message = await interaction.channel.fetch_message(self.message_id)
            timestamp = self.values[0]
            await self.base_cog.update_reaction(interaction, message, timestamp)

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
            await interaction.response.send_message(content=f"You have already selected {old_str}", ephemeral=True)
            return
            
        if old_timestamp != None:
            self.client.db.remove_reaction(message_id, user.id, old_timestamp)
            
        self.client.db.add_reaction(message_id, user, new_timestamp)
        
        extra_string = f"\nYour previous response was: {old_str}" * (old_timestamp!=None)
        await interaction.response.send_message(content=f"You have responded with: {new_str}" + extra_string, ephemeral=True)
        
        nt = self.client.get_cog("Notifications")
        if not (old_timestamp == None and new_timestamp in [-1, "-1"]):
            await nt.notify_react(interaction.user.id, new_timestamp, message.id, message.guild.name)
        
        await self.update_request_embed(message)
    
    def get_request_time_list(self, interaction):
        t_step          = 15 * 60 #time step in seconds
        
        message_id      = interaction.message.id
        user            = interaction.user
        user_timezone   = pytz.timezone(self.client.db.get_timezone(user))
        creation_time   = self.client.db.get_creation_time(message_id)
        creation_unix   = time.mktime(creation_time.timetuple())
        
        first_timestamp = (int(creation_unix // t_step) + 1) * t_step
        
        option_list = []
        for i in range(0,24):   
            new_timestamp = first_timestamp + t_step * i
            local_time = datetime.datetime.fromtimestamp(new_timestamp, user_timezone)
            
            time_str = local_time.strftime("%H:%M")
            new_select = SelectOption(label=time_str, value=new_timestamp)
            option_list.append(new_select)
    
        return option_list
    
    def interact_val_to_str(self, val):
        if val == "0" or val == 0:  
            return "Now" 
        if val == "-1" or val == -1:
            return "Unavailable"
        
        return f"<t:{val}:t>"

    @commands.command(
        help = '''Sets valorant username and tag.
        parameters:
            username: the username and tag, separated by '#'
        Example: ?username FootGirl420#Euw"''')
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
