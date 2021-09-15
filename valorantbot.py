import discord
import datetime
import toml
import random
from bs4 import BeautifulSoup
from discord.ext import commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import authordetails
import valorantranks

import asyncio
import nest_asyncio
nest_asyncio.apply()

with open('config.toml', 'r') as f:
    config = toml.loads(f.read())

client = commands.Bot(command_prefix='?', case_insensitive=True, intents=discord.Intents.all())

client.messageToSession = dict()
#client.clockMap = {"✅":"Now","🕛":"12:00","🕧":"12:30","🕐":"1:00","🕜":"1:30","🕑":"2:00","🕝":"2:30","🕒":"3:00","🕞":"3:30","🕓":"4:00","🕟":"4:30","🕔":"5:00","🕠":"5:30","🕕":"6:00","🕡":"6:30","🕖":"7:00","🕢":"7:30","🕗":"8:00","🕣":"8:30","🕘":"9:00","🕤":"9:30","🕙":"10:00","🕥":"10:30","🕚":"11:00","🕦":"11:30"}
client.clockMap = {"✅":"Now","🕛":"12:00","🕧":"12:30","🕐":"01:00","🕜":"01:30","🕑":"02:00","🕝":"02:30","🕒":"03:00","🕞":"03:30","🕓":"04:00","🕟":"04:30","🕔":"05:00","🕠":"05:30","🕕":"06:00","🕡":"06:30","🕖":"07:00","🕢":"07:30","🕗":"08:00","🕣":"08:30","🕘":"09:00","🕤":"09:30","🕙":"10:00","🕥":"10:30","🕚":"11:00","🕦":"11:30","❌": None}
client.scheduler = AsyncIOScheduler()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    

class ValorantSession():

    timeOffset = datetime.timedelta(minutes=60)

    def __init__(self, message=None):
        self.scheduler = AsyncIOScheduler()
        self.message = message
        self.hasStarted = False
        self.hasEnded = False
        self.voiceChannel = None
        self.time = message.created_at

        self.timeDict = self.makeTimeDict()
        self.orderedEmojiList = list([emoji for emoji in self.timeDict])

    def makeTimeDict(self):
        message = self.message
        currTime = message.created_at + ValorantSession.timeOffset

        deltaMin = ((currTime.minute // 30)+1)*30 - currTime.minute
        deltaTime = datetime.timedelta(minutes= deltaMin, seconds = -currTime.second, microseconds=-currTime.microsecond)

        firstTime = currTime + deltaTime
        mins30 = datetime.timedelta(minutes = 30)

        indOffset = 0
        timeStrList = [val for key, val in client.clockMap.items() if key != "✅" and key != "❌"]
        lookupTime = firstTime.strftime("%I:%M")
        
        for ind in range(0, len(timeStrList)):
            if lookupTime == timeStrList[ind]:
                indOffset = ind
                print(indOffset)
                break

        timeEmojiList = [key for key in client.clockMap if key != "✅" and key != "❌"]*2

        self.orderedEmojiList = ["✅"]
        timeDict = {"✅": currTime}

        for num in range(0,24):
            nextTime = firstTime + mins30 * num
            key = timeEmojiList[num + indOffset]
            
            self.orderedEmojiList.append(key)
            timeDict[key] = nextTime
            
            
        self.orderedEmojiList.append("❌")
        timeDict["❌"] = None

        return timeDict

    def start(self):
        try:
            self.scheduler.start()
            print("Started Scheduler")
        except:
            print("Scheduler was already started")
        

        if self.hasStarted == True:
            return
        else:
            self.hasStarted = True

        mins5 = datetime.timedelta(minutes = 5)
        self.scheduler.add_job(checkIn, "date", args=["✅", self], run_date=datetime.datetime.now() + mins5)
        
        for emoji,time in self.timeDict.items():
            if emoji == "✅" or emoji == "❌":
                continue
            self.scheduler.add_job(checkIn, "date", args=[emoji, self], run_date=time + mins5)
            

async def checkIn(emoji, session):
    print("CHECKING IN")
    message = session.message

    if session.hasStarted == False:
        print("Session not started")
        return

    for react in message.reactions:
        if react.emoji == emoji:

            flakeList = []

            async for reactUser in react.users():
                print(reactUser)
                userJoined = False
                if reactUser == client.user:
                    continue
                for channel in message.guild.voice_channels:
                    for voiceUser in channel.members:

                        if voiceUser == reactUser:
                            userJoined = True

                print(f"HAS JOINED: {userJoined}")
                if userJoined == False:
                    flakeList.append(reactUser.mention)

            if flakeList != []:
                flakeStr = ",".join(flakeList)
                await message.reply(f"{flakeStr}, where the fuck are you?")

def makeNewSession(message):
    newSession = ValorantSession(message)
    client.messageToSession[message] = newSession
    return newSession
client.makeNewSession = makeNewSession


def getSession(message):
    try:
        return client.messageToSession[message]
    except:
        newSession = client.makeNewSession(message)
        return newSession
client.getSession = getSession

async def update_checkin_embed(message):
    embed = message.embeds[0]
    embedDic = embed.to_dict()
    newFieldList = [embedDic["fields"][0]]
    newFieldList.append({'inline': False, 'name': "__Coming Now__", 'value': "\u200b"})
    newFieldList.append({'inline': True, 'name': "__Need More Time__", 'value': "\u200b"})
    newFieldList.append({'inline': True, 'name': "__Not Coming__", 'value': "\u200b"})
    
    for react in message.reactions:
        pass
    

async def update_request_embed(message):
    print("Getting Session")
    currSession = client.getSession(message)
    emojiToTimeDict = currSession.timeDict

    embed = message.embeds[0]
    embedDic = embed.to_dict()
    newFieldList = [embedDic["fields"][0]]

    for e in currSession.orderedEmojiList:
        try:
            timeStr = emojiToTimeDict[e].strftime("%H:%M")
            newFieldList.append({'inline': False, 'name': f"{e} ({timeStr})", 'value': ""})
        except:
            if e == "❌":
                timeStr = "Unavailable"
                newFieldList.append({'inline': False, 'name': f"{e} ({timeStr})", 'value': ""})
            else: 
                raise Exception("Error found updating embed using ValorantSession.orderedEmojiList")

    newFieldList[1] = {'inline': False, 'name': "✅ (Now)", 'value': ""}

    print("Scanning Reactions")
    for react in message.reactions:
        emoji = react.emoji
        if emoji not in client.clockMap:
            return

        ind = currSession.orderedEmojiList.index(emoji) + 1
        async for user in react.users():
            if user != client.user:
                field = newFieldList[ind]
                field["value"] = field["value"] + f"\n> {user.mention}"

    print("Finishing up")
    cleanNewFieldList = [field for field in newFieldList if field["value"]!=""]

    embedDic["fields"] = cleanNewFieldList
    newEmbed = discord.Embed.from_dict(embedDic)

    await message.edit(embed=newEmbed)
    print("---FINISHED---")

client.update_request_embed = update_request_embed

@client.command()
async def fakecheckin(ctx):
    
    newEmbed = discord.Embed(title="__Check In__", color=0xff8800)
    # newEmbed.add_field(name=s"🕜 (01:30)", value="CUM\n", inline=False)
    newEmbed.add_field(name="The following people reacted to the reqeust, but do not appear to have joined:", value="PLACEHOLDER TEXT", inline=False)
    
    authorText, authorIcon = authordetails.get_author_pair()
    newEmbed.set_author(name=authorText, icon_url=authorIcon) 
    
    message = await ctx.reply(embed=newEmbed)
    
    await message.add_reaction("❌")
    await message.add_reaction("✅")
    
    
# @client.command()
# async def ecoround(ctx):
#     txt = "The one with the rifle shoots! The one without follows him!\nWhen the one with the rifle gets killed, the one who is following picks up the rifle and shoots!"
#     message = await ctx.reply(txt)

@client.command()
async def randommap(ctx):
    mapList = authordetails.maps
    await ctx.reply(random.choice(mapList))
    
@client.command()
async def randomagent(ctx, num="1"):
    num = int(num)
    try:
        sample = authordetails.random_agents(num)
        if num == 1:
            await ctx.reply(f"> {sample[0]}")
            return
        

        agentStr = "\n".join([f"> {i + 1}: {sample[i]}" for i in range(0,num)])
        await ctx.reply(agentStr)
        
    except:
        await ctx.reply(f"I'm sorry {ctx.author.name}, I can't let you do that")

    
@client.command()
async def ligma(ctx):
    await ctx.reply("Ligma balls, bitch!")
    
def is_request(message):
    return "Valorant Request" in message.embeds[0].title
client.is_request = is_request

@client.command()
async def ranks(ctx):
    memberList = []
    rankList = []
    for member in discord.utils.get(ctx.guild.roles,name="Agents").members:

        memberList.append(f"> {member.name}")
        try:
            memberRank = valorantranks.get_player_rank(member.id)
            
            rankList.append(memberRank)
        except:
            
            rankList.append("Unknown")
            
    rankNumList = [valorantranks.get_rank_num(rank) if rank != "Unknown" else -1 for rank in rankList]
    print(rankNumList)
    
    zip_list = zip(rankNumList, memberList, rankList)
    sorted_zip_list = sorted(zip_list, reverse=True)
    
    orderedMemberList = [m for _,m,_ in sorted_zip_list]
    orderedRankList = [r for _,_,r in sorted_zip_list]
    
    memberStr = "\n".join(orderedMemberList)
    rankStr = "\n".join(orderedRankList)
    
    newEmbed = discord.Embed(title="__Leaderboard__", color=0xff0000)
    
    newEmbed.add_field(name="__Player__", value=memberStr, inline=True)
    newEmbed.add_field(name="__Rank__", value=rankStr, inline=True)
    
    message = await ctx.send(embed=newEmbed)
   
    
''''FUNCTION DOESN'T WORK:
    I think because match history loads in
    after the page loads. If so, would need
    selenium to make this work'''
# @client.command()
# async def recentrecords(ctx):
#     memberList = []
#     winList = []
#     lossList = []
#     for member in discord.utils.get(ctx.guild.roles,name="Agents").members:

#         memberList.append(f"> {member.name}")
#         # try:
#         wins, losses = valorantranks.get_recent_win_loss(member.id)
#         winList.append(wins)
#         lossList.append(losses)

#         # except:
#         #     winList.append("-1")
#         #     lossList.append("?")
        
#     zip_list = zip(winList, memberList, lossList)
#     sorted_zip_list = sorted(zip_list, reverse=True)
    
#     orderedWinList = [w if w != "-1" else "?" for w,_,_ in sorted_zip_list]
#     orderedMemberList = [m for _,m,_ in sorted_zip_list]
#     orderedLossList = [o for _,_,o in sorted_zip_list]

#     winStr = "\n".join(orderedWinList)
#     memberStr = "\n".join(orderedMemberList)
#     lossStr = "\n".join(orderedLossList)
    
#     newEmbed = discord.Embed(title="__Leaderboard__", color=0xff0000)
    
#     newEmbed.add_field(name="__Player__", value=memberStr, inline=True)
#     newEmbed.add_field(name="__Wins__", value=winStr, inline=True)
#     newEmbed.add_field(name="__Losses__", value=lossStr, inline=True)
    
#     message = await ctx.send(embed=newEmbed)
            

@client.command()
async def valorant(ctx):
    
    newEmbed = discord.Embed(title="__Valorant Request__", color=0xff0000)
    #ewEmbed = discord.Embed(color=0xff0000)
    # newEmbed.add_field(name=s"🕜 (01:30)", value="CUM\n", inline=False)
    newEmbed.add_field(name=f"{ctx.author.name} wants to play Valorant", value="React with :white_check_mark: if interested now, :x: if unavailable, or a clock emoji if interested later.", inline=False)
    newEmbed.set_thumbnail(url="https://preview.redd.it/buzyn25jzr761.png?width=1000&format=png&auto=webp&s=c8a55973b52a27e003269914ed1a883849ce4bdc")
    #newEmbed.set_author(name="Valorant Request", icon_url="https://cdn.valorantinfo.gg/img/sprays/VALORANT.png") 

    agentsID = discord.utils.get(ctx.guild.roles,name="Agents").mention

    message = await ctx.reply(agentsID, embed=newEmbed)

    newSession = client.makeNewSession(message)
    
    await message.add_reaction("❌")
    tempEmojiList = [emoji for emoji, dt in newSession.timeDict.items()]
    for i in range(0,7):
        await message.add_reaction(tempEmojiList[i])

@client.event
async def on_raw_reaction_remove(payload):

    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    if client.is_request(message):
        await client.update_request_embed(message)

@client.event
async def on_raw_reaction_add(payload):

    thisEmoji = payload.emoji.name
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    #guild = discord.utils.find(lambda g: g.id == payload.guild_id, client.guilds)
    guild = message.guild
    user = discord.utils.find(lambda m : m.id == payload.user_id, guild.members)
    # user = message.user
    #--------------------------------------------------------------------------

    #Checks for reactions to ignore
    #If message was not posted by bot
    if message.author != client.user:
        return
    #If reaction was from bot
    if user == client.user:
        return

    #Removes unwanted reactions
    if thisEmoji not in client.clockMap:
        await message.remove_reaction(payload.emoji, user)
        return

    print("Checking For Multiple Emoji's")
    #Removes this reaction if another reaction has been given
    for react in message.reactions:
        async for nextUser in react.users():
            if user == nextUser:
                if react.emoji != thisEmoji:
                    await message.remove_reaction(thisEmoji, user)
                    return

    if client.is_request(message):
        print("Message: Request")
        await client.update_request_embed(message)
        
    elif client.is_checkin(message):
        print("Message: Check In")
        if thisEmoji not in ["❌", "✅"]:
            await message.remove_reaction(payload.emoji,user)
            return

        await client.update_checkin_embed(message)
        
# @tasks.loop(minutes=5)
# def checkSchedule(schedule):
#     message = schedule.message
#     guild = message.guild
#     for channel in guild.voice_channels:
#         for user in channel.members:
    


@client.event
async def on_voice_state_update(joinUser, before, after):
    # New Person Joins Voice Chat
    if before.channel is None and after.channel is not None:
        print(f"{joinUser} has joined a voice channel. Checking for session")
        for message, session in client.messageToSession.items():
            print(f"Checking session from {session.time}")
            for react in message.reactions:
                print(f"Checking {react.emoji}")
                async for user in react.users():
                    print(f"Checking {user} == {joinUser}")
                    if user == joinUser:
                        print(f"STARTING SESSION FROM {session.time}")
                        session = client.messageToSession[message]
                        session.start()
                        print(datetime.datetime.now())

    # Someone Leaves Voice Chat
    if before.channel is not None and after.channel is None:
        guild = before.channel.guild

        count = 0
        for channel in guild.voice_channels:
            for voiceUser in channel.members:
                count +=1

        if count == 0:
            for message,session in client.messageToSession.items():
                if message.guild == guild:
                    
                    print(f"Channel is now empty, ending session from {session.time}")
                    session = client.messageToSession[message]
                    session.hasStarted = False
                    session.hasEnded = True


client.run(config['discord']['key'])
