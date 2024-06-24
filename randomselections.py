from discord.ext import commands
import authordetails as ad 
import random
import sys
import discord

class Selects(commands.Cog):
    
    primary_guns    = {"Stinger": 1100, "Spectre": 1600, "Bulldog": 2050, "Guardian": 2250, "Marshal": 950, "Outlaw": 2400, "Operator": 4700,\
                            "Bucky": 850, "Judge": 1850, "Phantom": 2900, "Vandal": 2900, "Ares": 1600, "Odin": 3200,\
                                None: 0}
        
    second_guns     = {"Classic": 0, "Shorty": 150, "Frenzy": 450, "Ghost": 500, "Sheriff": 800}
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("randomselections.py loaded")
        
    @commands.command(help = "Returns a random map.")
    async def randommap(self, ctx):
        '''Returns a random map.'''
        await ctx.reply(random.choice(ad.map_list))
        
    @commands.command(help = "Returns a number of random agents (not bound by embed limit).\n" +\
                      "parameters:\n    num: the number of agents to select (default is 1)")
    async def randomagents_simple(self, ctx, num="1"):
        '''Returns a number of random agents.'''
        num = int(num)
        
        if num < 1 or num > len(ad.agent_details):
           await ctx.reply(f"Please use a number from 1-{len(ad.agent_details)}")
           return
        
        sample = random.sample(list(ad.agent_details), num)
        agentStr = "\n".join([f"> {i + 1}: " * (num!=1) + f"{sample[i]}" for i in range(0,num)])
        await ctx.reply(agentStr)
        
    @commands.command(help = "Returns a random agent")
    async def randomagent(self, ctx):
        await self.randomagents(ctx)
    
    @commands.command(help = "Returns a number of random agents.\n" +\
                      "parameters:\n    num: the number of agents to select from 1-5 (default is 1)")
    async def randomagents(self, ctx, num="1"):
        '''Returns a number of random agents.'''
        num = int(num)
        
        if num > 5 or num < 1:
            await ctx.reply("You can only use numbers from 1-5")
            return

        sample = random.sample(list(ad.agent_details), num)
        embed_list = []
        
        
        for i in range(num):
            agent       = sample[i]
            role        = ad.agent_details[agent]['role']
            agent_icon  = ad.agent_details[agent]['image']
            color       = ad.agent_roles[role]['colour']
            role_icon   = ad.agent_roles[role]['image']
            
            new_embed = discord.Embed(title=agent, color=color)
            new_embed.add_field(name=" ", value=f"  -{role}")
            new_embed.set_author(name="⠀", icon_url=role_icon)
            new_embed.set_thumbnail(url=agent_icon)
            embed_list.append(new_embed)
            
        print(embed_list)
        await ctx.reply(embeds=embed_list)
            
    @commands.command(help = "Returns a random primary and secondary weapon.\n" +\
                      "parameters:\n    creds: the number of credits to use (default is 9000)")
    async def randomguns(self, ctx, creds="9000"):
        '''Returns a random primary and secondary weapon.'''
        creds = int(creds)
        primary_list    = list([gun for gun, val in self.primary_guns.items() if val<= creds])
        primary         = random.choice(primary_list)
        spent           = self.primary_guns[primary]
        
        second_list     = list([gun for gun, val in self.second_guns.items() if val <= creds-spent])
        secondary       = random.choice(second_list)
        
        await ctx.reply(f"Primary:       {primary}\nSecondary:  {secondary}")
        
async def setup(client):
    await client.add_cog(Selects(client))
    