import discord
from discord.ext import commands
from checks import is_admin
from discord.ui import Button, Select, View
from discord import SelectOption, ButtonStyle

CREDIT_NAME = "social credits"

class CreditVoting(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.view_penalty = self.CreditVoteView(self, 0)
        self.client.add_view(self.view_penalty)
        self.view_reward  = self.CreditVoteView(self, 1)
        self.client.add_view(self.view_reward)
        print("creditvoting.py loaded")
        
    def get_vote_view(self, is_reward):
        return self.view_reward if is_reward else self.view_penalty

    @commands.command(help = f"Starts a {CREDIT_NAME} vote")
    @commands.guild_only()
    @commands.check(is_admin)
    async def ASCvote(self, ctx):
        
        select_categ = self.SelectCategory(self, 817415777442857020)
        select_view = View()
        select_view.add_item(select_categ)
            
        await ctx.send(content="Select a Category", view=select_view)

    class CreditVoteView(View):
        def __init__(self, base_cog, is_reward):           
            self.base_cog = base_cog
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
        
        async def update_vote_embed(self, message):
            votes   = self.base_cog.client.db.get_votes(message.id)
            num_yes = sum(votes)
            num_no  = len(votes)-num_yes
            
            yes_i   = (self.is_reward)      + 1
            no_i    = (not self.is_reward)  + 1
            
            old_embed   = message.embeds[0]
            embed_dict  = old_embed.to_dict()
            fields      = embed_dict['fields']
            
            fields[yes_i]['value'] = num_yes
            fields[no_i]['value']  = num_no
            
            new_embed = discord.Embed.from_dict(embed_dict)
            
            await message.edit(embed=new_embed)
            
        def make_buttons(self):
            
            button_bad  = self.base_cog.CreditVoteButton(self.is_reward, not self.is_reward)
            button_good = self.base_cog.CreditVoteButton(self.is_reward, self.is_reward)
            
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
                await interaction.response.send_message(f"You have already voted '{self.keywords[self.is_reward][vote]}' in this poll.", ephemeral=True)
                return
            
            self.view.client.db.set_user_vote(msg.id, user, verdict) 
            
            await self.view.update_vote_embed(msg)
            
            await interaction.response.send_message(f"You have voted: {self.label}", ephemeral=True)

    
    async def post_vote(self, interaction, user_id, feat, value):
        
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
            
        view = self.get_vote_view(is_reward)
        
        new_embed.add_field(name=f"__{view.get_bad_button().label}__",  value="0")
        new_embed.add_field(name=f"__{view.get_good_button().label}__",  value="0")
        
        
        message = await interaction.response.send_message(embed=new_embed, view=view)
        
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

        new_embed = discord.Embed(title=("__Reward Result__" if is_reward else "__Penalty Result__"), 
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

    class SelectCategory(Select):

        def __init__(self, base_cog, user_id):
            self.base_cog   = base_cog
            self.user_id    = user_id
            
            category_list = self.base_cog.client.db.get_event_categories()
            
            option_list = list(
                SelectOption(label=categ, value=categ) 
                for categ in category_list)  
                
            super().__init__(placeholder="Select a category", 
                             min_values=1, 
                             max_values=1, 
                             options=option_list)
                
        async def callback(self, interaction):
            category        = self.values[0]
            select_event    = self.base_cog.SelectEventType(self.base_cog, self.user_id, category)
            select_view     = View()
            
            select_view.add_item(select_event)
            await interaction.response.send_message(view=select_view, ephemeral=True)
            
    class SelectEventType(Select):
        
        def __init__(self, base_cog, user_id, category):
            self.base_cog   = base_cog
            self.user_id    = user_id
            self.category   = category
            
            event_types = self.base_cog.client.db.get_event_types_from_category(category)
            
            option_list = list(
                SelectOption(label=event, value=event) 
                for event in event_types)  
                
            super().__init__(placeholder="Select an offense", 
                             min_values=1, 
                             max_values=1, 
                             options=option_list)
        
        async def callback(self, interaction):
            event_name = self.values[0]
            details = self.base_cog.client.db.get_event_details(event_name)
            num_credits = details['default_value']
            await self.base_cog.post_vote(interaction, self.user_id, event_name, num_credits)

async def setup(client):
    await client.add_cog(CreditVoting(client))
