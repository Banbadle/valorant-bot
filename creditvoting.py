import discord
from discord_components import Button, ActionRow, ButtonStyle, SelectOption, Select
from discord.ext import commands
import sys
from checks import is_admin

CREDIT_NAME = "social credits"

class CreditVoting(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(sys.argv[0])
    async def post_vote(self, ctx, user_id, feat, value):
        
        is_reward = value > 0
        
        new_embed = discord.Embed(title=("__Reward Vote__" if is_reward else "__Fine Vote__"), 
                                  color=(0x00ff00 if is_reward else 0xff0000))
        
        title_text = "nominated for" if is_reward else "accused of"
        inner_text = f"If supported, <@{user_id}> would receive" if is_reward else f"If found guilty, <@{user_id}> would be fined"

        new_embed.add_field(name=f"{feat}", 
                            value=f'''<@{user_id}> has been {title_text}: {feat} 
                                        {inner_text} {abs(value)} {CREDIT_NAME}.
                                        Please note that your vote cannot be changed once selected.''',
                            inline=False)
        
        new_embed.add_field(name="__Deny__",  value="0")
        new_embed.add_field(name="__Accept__",  value="0")
        
        button_bad, button_good = None, None
        if is_reward:
            button_bad  = Button(label="Deny",      style=ButtonStyle(4), custom_id="verdict_deny")
            button_good = Button(label="Accept",    style=ButtonStyle(3), custom_id="verdict_accept")
        else:
            button_good = Button(label="Innocent",  style=ButtonStyle(3), custom_id="verdict_innocent")
            button_bad  = Button(label="Guilty",    style=ButtonStyle(4), custom_id="verdict_guilty")
            
        button_row = ActionRow(button_bad, button_good)
    
        message = await ctx.send(embed=new_embed, components=[button_row])
        
        return message


def setup(client):
    client.add_cog(CreditVoting(client))
