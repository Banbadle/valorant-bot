import discord
import datetime
import os
from invertibledict import InvDict
import toml
import random

from discord.ext import commands, tasks

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import asyncio

import nest_asyncio
nest_asyncio.apply()

with open('config.toml', 'r') as f:
    config = toml.loads(f.read())

client = commands.Bot(command_prefix='?', case_insensitive=True, intents=discord.Intents.all())

client.messageToSession = dict()
#client.clockMap = {"✅":"Now","🕛":"12:00","🕧":"12:30","🕐":"1:00","🕜":"1:30","🕑":"2:00","🕝":"2:30","🕒":"3:00","🕞":"3:30","🕓":"4:00","🕟":"4:30","🕔":"5:00","🕠":"5:30","🕕":"6:00","🕡":"6:30","🕖":"7:00","🕢":"7:30","🕗":"8:00","🕣":"8:30","🕘":"9:00","🕤":"9:30","🕙":"10:00","🕥":"10:30","🕚":"11:00","🕦":"11:30"}
client.clockMap = {"✅":"Now","🕛":"12:00","🕧":"12:30","🕐":"01:00","🕜":"01:30","🕑":"02:00","🕝":"02:30","🕒":"03:00","🕞":"03:30","🕓":"04:00","🕟":"04:30","🕔":"05:00","🕠":"05:30","🕕":"06:00","🕡":"06:30","🕖":"07:00","🕢":"07:30","🕗":"08:00","🕣":"08:30","🕘":"09:00","🕤":"09:30","🕙":"10:00","🕥":"10:30","🕚":"11:00","🕦":"11:30","❌": None}


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
        for emoji,time in self.timeDict.items():
            if emoji == "✅" or emoji == "❌":
                continue
            self.scheduler.add_job(checkIn, "date", args=[emoji, self], run_date=time + mins5)
            


async def checkIn(emoji, session):
    print("CHECKING IN")
    message = session.message

    if session.hasStarted == False:
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

                print("HAS JOINED: {}".format(userJoined))
                if userJoined == False:
                    flakeList.append(reactUser.mention)

            if flakeList != []:
                await message.reply("{}, where the fuck are you?".format(",".join(flakeList)))

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

async def updateEmbed(message):
    print("Getting Session")
    currSession = client.getSession(message)
    emojiToTimeDict = currSession.timeDict

    embed = message.embeds[0]
    embedDic = embed.to_dict()
    newFieldList = [embedDic["fields"][0]]

    for e in currSession.orderedEmojiList:
        try:
            timeStr = emojiToTimeDict[e].strftime("%H:%M")
            newFieldList.append({'inline': False, 'name': "{} ({})".format(e, timeStr), 'value': ""})
        except:
            timeStr = "Unavailable"
            newFieldList.append({'inline': False, 'name': "{} ({})".format(e, timeStr), 'value': ""})

    newFieldList[1] = {'inline': False, 'name': "{} (Now)".format("✅", timeStr), 'value': ""}

    print("Scanning Reactions")
    for react in message.reactions:
        emoji = react.emoji
        if emoji not in client.clockMap:
            return

        ind = currSession.orderedEmojiList.index(emoji) + 1
        async for user in react.users():
            if user != client.user:
                field = newFieldList[ind]
                field["value"] = "{}\n{}".format(field["value"], user.mention)

    print("Finishing up")
    cleanNewFieldList = [field for field in newFieldList if field["value"]!=""]

    embedDic["fields"] = cleanNewFieldList
    newEmbed = discord.Embed.from_dict(embedDic)

    await message.edit(embed=newEmbed)
    print("---FINISHED---")

client.updateEmbed = updateEmbed

@client.command()
async def test(ctx):
    await ctx.send("hello")
    
# @client.command()
# async def ecoround(ctx):
#     txt = "The one with the rifle shoots! The one without follows him!\nWhen the one with the rifle gets killed, the one who is following picks up the rifle and shoots!"
#     message = await ctx.reply(txt)

@client.command()
async def randommap(ctx):
    mapList = ["Ascent", "Split", "Fracture", "Bind", "Breeze", "Icebox", "Haven"]
    await ctx.reply(random.choice(mapList))
    
@client.command()
async def ligma(ctx):
    await ctx.reply("Ligma balls, bitch!")

@client.command()
async def valorant(ctx):

    newEmbed = discord.Embed(title="Valorant Request", color=0xff0000)
    # newEmbed.add_field(name=s"🕜 (01:30)", value="CUM\n", inline=False)
    newEmbed.add_field(name="{} wants to play Valorant".format(ctx.author.name), value="React with :white_check_mark: if interested now, :x: if unavailable, or a clock emoji if interested later \n--------------------------", inline=False)
    agentsID = discord.utils.get(ctx.guild.roles,name="Agents").mention

    message = await ctx.send(agentsID, embed=newEmbed)

    newSession = client.makeNewSession(message)
    
    await message.add_reaction("❌")
    tempEmojiList = [emoji for emoji, dt in newSession.timeDict.items()]
    for i in range(0,7):
        await message.add_reaction(tempEmojiList[i])

@client.event
async def on_raw_reaction_remove(payload):

    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    await client.updateEmbed(message)

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

    #Removes unwanted reactions (change if want a yes/no)
    if thisEmoji not in client.clockMap:
        await message.remove_reaction(payload.emoji, user)
        return

    print("Checking Emoji's")
    #Removes this reaction if another reaction has been given
    for react in message.reactions:
        async for nextUser in react.users():
            if user == nextUser:
                if react.emoji != thisEmoji:
                    await message.remove_reaction(thisEmoji, user)
                    return

    await client.updateEmbed(message)

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
        print(joinUser)
        for message in client.messageToSession:
            for react in message.reactions:
                async for user in react.users():
                    print(user.name)
                    if user == joinUser:

                        session = client.messageToSession[message]
                        session.scheduler.add_job(checkIn, "date", args=["✅", session], run_date=datetime.datetime.now() + datetime.timedelta(minutes = 5))
                        session.start()
                        print("STARTING SESSION")
                        print(datetime.datetime.now())

    # Someone Leaves Voice Chat
    if before.channel is not None and after.channel is None:
        guild = before.channel.guild

        count = 0
        for channel in guild.voice_channels:
            for voiceUser in channel.members:
                count +=1

        if count == 0:
            for message in client.messageToSession:
                if message.guild == guild:

                    session = client.messageToSession[message]
                    session.hasStarted = False
                    session.hasEnded = True


client.run(config['discord']['key'])
