from discord.ext import commands
import authordetails as ad 
import random
import sys

class Selects(commands.Cog):
    
    primary_guns    = {"Stinger": 950, "Spectre": 1600, "Bulldog": 2050, "Guardian": 2250, "Marshal": 950, "Operator": 4700,\
                            "Bucky": 850, "Judge": 1850, "Phantom": 2900, "Vandal": 2900, "Ares": 1600, "Odin": 3200,\
                                None: 0}
        
    second_guns     = {"Classic": 0, "Shorty": 150, "Frenzy": 450, "Ghost": 500, "Sheriff": 800}
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(sys.argv[0])
        
    @commands.command(help = "Returns a random map.")
    async def randommap(self, ctx):
        '''Returns a random map.'''
        await ctx.reply(random.choice(ad.map_list))
    
    @commands.command(help = "Returns a number of random agents.\n" +\
                      "parameters:\n    num: the number of agents to select (default is 1)")
    async def randomagents(self, ctx, num="1"):
        '''Returns a number of random agents.'''
        num = int(num)
        try:
            sample = random.sample(list(ad.agent_details), num)
            agentStr = "\n".join([f"> {i + 1}: " * (num!=1) + f"{sample[i]}" for i in range(0,num)])
            await ctx.reply(agentStr)
    
        except:
            await ctx.reply(f"I'm sorry {ctx.author.name}, I can't let you do that")
            
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
        
def setup(client):
    client.add_cog(Selects(client))
    