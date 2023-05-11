import discord
from discord.ext import commands
import sys
from checks import is_admin
from discord.ui import Button, Select, View
from discord import SelectOption, ButtonStyle, ActionRow

CREDIT_NAME = "social credits"

class CreditVoting(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.view_penalty = self.CreditVoteView(self.client, 0)
        self.view_reward  = self.CreditVoteView(self.client, 1)
        print("creditvoting.py loaded")
        
    def get_view(self, is_reward):
        return self.view_reward if is_reward else self.view_penalty

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

    class CreditVoteView(View):
        def __init__(self, client, is_reward):           
            self.client = client
            self.is_reward = is_reward
            super().__init__(timeout=None)
            
            self.make_buttons()
            
        def get_bad_button(self):
            return self.children[0]
        
        def get_good_button(self):
            return self.children[1]
        
        def get_yes_button(self):
            return self.children[not self.is_reward]
        
        def get_no_button(self):
            return self.children[self.is_reward]
            
        def make_buttons(self):
            
            button_bad  = self.CreditVoteButton(self.is_reward, not self.is_reward)
            button_good = self.CreditVoteButton(self.is_reward, self.is_reward)
            
            self.add_item(button_bad)
            self.add_item(button_good)
            
        class CreditVoteButton(Button):
            keywords = [["Innocent", "Guilty"],["Deny", "Accept"]]
            
            def __init__(self, is_reward: bool, verdict: bool):
                self.is_reward = is_reward
                self.verdict = verdict
                
                is_good = (is_reward ^ (not verdict))
                button_label = self.keywords[is_reward][verdict]
                button_style = ButtonStyle.green if is_good else ButtonStyle.red
                
                super().__init__(style=button_style, label=button_label, custom_id=f"creditvote_{button_label}")
                
            async def callback(self, interaction):
                msg     = interaction.message
                user    = interaction.user
                verdict = self.verdict
                vote    = self.view.client.db.get_user_vote(msg.id, user.id)
                
                if vote != None:
                    await interaction.response.send_message(f"You have already voted '{self.keywords[self.is_reward][vote]}' in this poll.")
                    return
                
                self.view.client.db.set_user_vote(msg.id, user, verdict) 
                
                await interaction.response.send_message(f"You have voted: {self.label}")
                
            
    @commands.command(help = f"Starts {CREDIT_NAME} votes")
    async def test1(self, ctx):
        await self.post_vote(ctx, ctx.author.id, "Good", 50)
        await self.post_vote(ctx, ctx.author.id, "Bad", -50)
    
    async def post_vote(self, ctx, user_id, feat, value):
        
        is_reward = value > 0
        
        new_embed = discord.Embed(title=("__Reward Vote__" if is_reward else "__Penalty Vote__"), 
                                  color=(0x00ff00 if is_reward else 0xff0000))
        
        
        title_text = "nominated for" if is_reward else "accused of"
        inner_text = f"If supported, <@{user_id}> would receive" if is_reward else f"If found guilty, <@{user_id}> would be fined"

        new_embed.add_field(name=f"{feat}", 
                            value=f'''<@{user_id}> has been {title_text}: {feat} 
                                        {inner_text} {abs(value)} {CREDIT_NAME}.
                                        Please note that your vote cannot be changed once selected.''',
                            inline=False)
            
        view = self.get_view(is_reward)
        
        new_embed.add_field(name=f"__{view.get_bad_button().label}__",  value="0")
        new_embed.add_field(name=f"__{view.get_good_button().label}__",  value="0")
        
        
        message = await ctx.send(embed=new_embed, view=view)
        
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


async def setup(client):
    await client.add_cog(CreditVoting(client))
