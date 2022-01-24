from discord.ext import commands
import authordetails.py as ad 
import random
import sys

def get_author_pair(agentName=None):
    if agentName==None:
        agentName = random.choice(ad.pair_list)
        
    text = ad.phrases[agentName]
    icon = ad.images[agentName]
    return [text, icon]

class Selects(commands.Cog):

    @commands.Cog.listener()
    async def on_ready(self):
        print(sys.argv[0])
        
    @commands.command()
    async def randommap(ctx):
        await ctx.reply(random.choice(ad.map_list))
    
    @commands.command()
    async def randomagents(self, ctx, num="1"):
        num = int(num)
        try:
            sample = random.sample(ad.agent_list, num)
            agentStr = "\n".join([f"> {i + 1}: " * (num!=1) + f"{sample[i]}" for i in range(0,num)])
            await ctx.reply(agentStr)
    
        except:
            await ctx.reply(f"I'm sorry {ctx.author.name}, I can't let you do that")
            
def setup(client):
    client.add_cog(Selects(client))
    