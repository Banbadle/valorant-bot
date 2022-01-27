import discord
import datetime
import re
import sys
from discord.ext import commands, tasks
from collections import defaultdict

import authordetails

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
        print(sys.argv[0])
        
    @tasks.loop()
    async def checkin_loop(self):
        curr_time = datetime.datetime.now()
        wait_time = 29 - ((curr_time.minute - 1) % 30)
        await nest_asyncio.sleep(wait_time * 60)
        
        new_time = curr_time.replace(second=0, microsecond=0, minute=curr_time.minute, hour=curr_time.hour) + datetime.timedelta(minutes = wait_time + 5)
        time_str = new_time.strftime("%I:%M")
        curr_emoji = list(key for key, val in clock_map.items() if val == time_str)[0]
        
        reaction_list = self.client.db.get_current_time_reactions(curr_emoji)
        
        msg_dict = defaultdict(list)
        for message_id, user_id in reaction_list:
            msg_dict[message_id].append(user_id)

        for message_id, user_id_list in msg_dict.items():
            self.checkin(message_id, user_id_list)
            
    def get_ordered_emoji_list(self, start_time):
        wait_time   = 29 - ((start_time.minute - 1) % 30)
        first_time  = start_time.replace(second=0, microsecond=0, minute=start_time.minute, hour=start_time.hour) + datetime.timedelta(minutes = wait_time)
        
        emoji_list          = list(clock_map)[1:-1] * 2
        slice_emoji         = list(key for key, val in clock_map.items() if val == first_time.strftime("%I:%M"))[0]
        slice_index         = emoji_list.index(slice_emoji)
        ordered_emoji_list  = emoji_list[slice_index: slice_index+24]
        
        return ordered_emoji_list, first_time
    
    async def checkin(self, message_id, user_id_list):
        flakeList = []
        
        for react_user_id in user_id_list:
            # Continue if reaction is by bot
            if react_user_id == self.client.user.id: continue
        
            guild_id = self.client.db.get_guild_id(message_id)
            guild = await self.client.fetch_guild(guild_id)
            
            for channel in guild.voice_channels:
                for voice_user in channel.members:

                    if voice_user.id == react_user_id:
                        print(f"HAS JOINED: {react_user_id}")
                        flakeList.append(react_user_id)
                        break
     
                else: continue
                break
                
        if flakeList != []:
            flakeStr = ",".join(flakeList)
            message = await self.client.get_channel(self.client.db.get_channel_id(message_id)).fetch_message(message_id)
            await message.reply(f"{flakeStr}, where the fuck are you?")

    async def update_checkin_embed(self, message):
        embed = message.embeds[0]
        embedDic = embed.to_dict()
        newFieldList = [embedDic["fields"][0]]
        newFieldList.append({'inline': False, 'name': "__Coming Now__", 'value': "\u200b"})
        newFieldList.append({'inline': True, 'name': "__Need More Time__", 'value': "\u200b"})
        newFieldList.append({'inline': True, 'name': "__Not Coming__", 'value': "\u200b"})
    
        for react in message.reactions:
            pass
    
    async def update_request_embed(self, message):
        print("Getting Session")

        message_id = message.id
        start_time = self.client.db.get_creation_time(message_id)
        
        ordered_emoji_list, next_time = self.get_ordered_emoji_list(start_time)
        
        author_name     = self.client.db.get_creator_name(message_id)
        base_embed      = message.embeds[0]
        embed_dict      = base_embed.to_dict()
        new_field_list  = [embed_dict["fields"][0]]
        
        new_field_list.append({'inline': False, 'name': "✅ (Now)", 'value': ""})

        for e in ordered_emoji_list:
            time_str = next_time.strftime("%H:%M")

            new_field_list.append({'inline': False, 'name': f"{e} ({time_str})", 'value': ""})
            next_time = next_time + datetime.timedelta(minutes = 30)

        new_field_list.append({'inline': False, 'name': "❌ (Unavailable)", 'value': ""})

        print("Scanning Reactions")

        emoji_display_order = ["✅"] + ordered_emoji_list + ["❌"]
        for reaction in self.client.db.get_reactions(message_id):
            if reaction['emoji'] not in clock_map: continue

            ind = emoji_display_order.index(reaction['emoji']) + 1
            if reaction['user'] != self.client.user.id:
                new_field_list[ind]["value"] += f"\n> <@{reaction['user']}>"

        print("Finishing up")
        final_field_list = [field for field in new_field_list if field["value"]!=""]

        embed_dict["fields"] = final_field_list
        new_embed = discord.Embed.from_dict(embed_dict)

        await message.edit(embed=new_embed)
        print("---FINISHED---")

    @commands.command()
    async def fakecheckin(self, ctx):

        newEmbed = discord.Embed(title="__Check In__", color=0xff8800)
        # newEmbed.add_field(name=s"🕜 (01:30)", value="CUM\n", inline=False)
        newEmbed.add_field(name="The following people reacted to the reqeust, but do not appear to have joined:", value="PLACEHOLDER TEXT", inline=False)

        authorText, authorIcon = authordetails.get_author_pair()
        newEmbed.set_author(name=authorText, icon_url=authorIcon)

        message = await ctx.reply(embed=newEmbed)

        await message.add_reaction("❌")
        await message.add_reaction("✅")


    def is_request(self, message_id):
        return self.client.db.get_message_type(message_id) == 1
    
    def is_checkin(self, message_id):
        return self.client.db.get_message_type(message_id) == 2
    
    def get_blank_request_embed(self, author_name):
        new_embed = discord.Embed(title="__Valorant Request__", color=0xff0000)
        new_embed.add_field(name=f"{author_name} wants to play Valorant", value="React with :white_check_mark: if interested now, :x: if unavailable, or a clock emoji if interested later.", inline=False)
        new_embed.set_thumbnail(url="https://preview.redd.it/buzyn25jzr761.png?width=1000&format=png&auto=webp&s=c8a55973b52a27e003269914ed1a883849ce4bdc")
        
        return new_embed

    def ordered_time_list(self, start_time):
        pass

    @commands.command()
    async def valorant2(self, ctx):
        new_embed = self.get_blank_request_embed(ctx.author.name)
    
        agentsID = discord.utils.get(ctx.guild.roles,name="Agents").mention
    
        message = await ctx.reply(agentsID, embed=new_embed)
    
        self.client.db.add_message(message, ctx.message, 1)
    
        await message.add_reaction("❌")
        await message.add_reaction("✅")
        temp_emoji_list, _ = self.get_ordered_emoji_list(datetime.datetime.now())
        for i in range(0,7):
            await message.add_reaction(temp_emoji_list[i])
    
    @commands.command()
    async def username(self, ctx):
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
    
        if not self.is_request(message_id): return

        message = await self.client.get_channel(channel_id).fetch_message(message_id)
        self.client.db.remove_reaction(message_id, payload.user_id, payload.emoji.name)
        await self.update_request_embed(message)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
    
        this_emoji  = payload.emoji.name
        channel_id  = payload.channel_id
        message_id  = payload.message_id
        guild_id    = self.client.get_channel(channel_id).guild.id
        user_id     = payload.user_id
        bot_id      = self.client.user.id
        

        '''ADD CHECK IF MESSAGE IS IN DATABASE'''
    
        #If reaction was from bot
        if user_id == bot_id:
            return
    
        user = await self.client.fetch_user(user_id)
        message = await self.client.get_channel(channel_id).fetch_message(message_id)
    
        #Removes unwanted reactions
        if this_emoji not in clock_map:
            await message.remove_reaction(this_emoji, user_id)
            return
    
        # Check if there is already a reaction in the database
        if self.client.db.get_user_reaction(message_id, user_id):
            # Remove the new reaction if there is
            await message.remove_reaction(this_emoji, user_id)
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
    