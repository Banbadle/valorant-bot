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
        
    @commands.command(help = f"Starts a {CREDIT_NAME} vote")
    @commands.guild_only()
    @commands.check(is_admin)
    async def ASCvoting(self, ctx, num):
        
        category_list = self.client.db.get_event_categories()
        option_list = []
        for categ in category_list:   
            
            new_select = SelectOption(label = f"{categ}", value = f"voteoption_category_{categ}")
            option_list.append(new_select)
            
        await ctx.send(content="Select a Category", components = [Select(placeholder= "Categories", options=option_list)])
        #await self.post_vote(ctx, 273795229264642048, "Misc", int(num))
    
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

    async def post_result(self, ctx, user_id, feat, value, v_yes, v_no):
        
        ## TEMP TO ALLOW TESTING IN DISCORD, DELETE BEFORE PUSHING
        user_id = int(user_id)
        v_yes = int(v_yes)
        v_no = int(v_no)
        value = int(value)
        
        pass_condition = (v_yes > v_no) and v_yes > 1
        is_reward = value > 0
        is_good =  (not is_reward ^ pass_condition)

        new_embed = discord.Embed(title=("__Reward Result__" if is_reward else "__Fine Result__"), 
                                  color=(0x00ff00 if is_good else 0xff0000))

        title_text = None
        if pass_condition:
            
            if is_reward:
                title_text = f'''The reward for {feat} has been granted to <@{user_id}>.
                            They have been awarded {value} {CREDIT_NAME}'''
            else:
                title_text = f'''<@{user_id}> has been found guilty of {feat}.
                            They have been fined {value} {CREDIT_NAME}.'''
        else:
            if is_reward:
                title_text = f"The reward for {feat} has been denied to <@{user_id}>."
            else:
                title_text = f"Charges of {feat} have been dropped against <@{user_id}>."
                
        vote_str = f"Denied ({v_no}) v ({v_yes}) Accepted" if is_reward else f"Guilty ({v_yes}) v ({v_no}) Innocent"

        new_embed.add_field(name=f"{feat}",  value=title_text + "\n" + vote_str,  inline=False)

        message = await ctx.send(embed=new_embed)
        return message
        
    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        msg_id = interaction.message.id
        user   = interaction.user

        v_id = interaction.custom_id
    
        if "verdict" in v_id:
            
            is_good = ("accept" in v_id or "deny" in v_id)
            
            vote = self.client.db.get_user_vote(msg_id, user.id)
            if vote != None:
                keywords = [["Innocent", "Guilty"],["Deny", "Accept"]]
                await interaction.send(f"You have already voted '{keywords[is_good][vote]}' in this poll.")
                return
            
            suffix = v_id[len("verdict")+1:].capitalize()
            await interaction.send(f"You have voted: {suffix}")
            
            if v_id == "verdict_deny" or v_id == "verdict_innocent":
                self.client.db.set_user_vote(msg_id, user, 0) 
            elif v_id == "verdict_accept" or v_id == "verdict_guilty":
                self.client.db.set_user_vote(msg_id, user, 1)
                
                
    @commands.Cog.listener()
    async def on_select_option(self, interaction):
        val = interaction.values[0]              
        if "voteoption" in val:
           _, process_type, process_name = val.split("_")
            
           if process_type == "category":
                event_types = self.client.db.get_event_types_from_category(process_name)
                option_list = []
                for event in event_types:   
                    
                    new_select = SelectOption(label = f"{event}", value = f"voteoption_event_{event}")
                    option_list.append(new_select)
                    
                await interaction.send(content="Select an offense", components = [Select(placeholder= "offenses", options=option_list)])
               
           elif process_type == "event":
               details = self.client.db.get_event_details(process_name)
               
               await self.post_vote(interaction, 1, process_name, details['default_value'])
               
                


def setup(client):
    client.add_cog(CreditVoting(client))
