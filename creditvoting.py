import discord
from discord.ext import commands
from discord.ui import Button, Select, View, Modal, TextInput
from discord import SelectOption, ButtonStyle, TextStyle
from discord import Interaction, Member, app_commands
import asyncio

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
        
        self.report_menu = app_commands.ContextMenu(
            name = "Report",
            callback=self.ASCvote_bad)
        
        self.commend_menu = app_commands.ContextMenu(
            name = "Reward",
            callback=self.ASCvote_good)
            
        self.client.tree.add_command(self.report_menu)
        self.client.tree.add_command(self.commend_menu)
        print("creditvoting.py loaded")
        
        
    def get_vote_view(self, is_reward):
        return self.view_reward if is_reward else self.view_penalty
    
    def ASCvote_good(self, interaction: Interaction, user: Member):
        return self.ASCvote(interaction, user, 1)
    
    def ASCvote_bad(self, interaction: Interaction, user: Member):
        return self.ASCvote(interaction, user, 0)

    async def ASCvote(self, interaction: Interaction, user: Member, is_reward: int):
        
        select_categ = self.SelectCategory(self, user, is_reward)
        select_view = View()
        select_view.add_item(select_categ)
        
        channel = interaction.channel
        if channel.name != "credit-votes":
            await interaction.response.send_message(
                content="You must be in a channel called 'credit-votes' to report or reward someone.",
                ephemeral=True) 
        else:    
            await interaction.response.send_message(content="Select a Category", view=select_view, ephemeral=True)
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
           
            no_i    = (not self.is_reward)  - 2
            yes_i   = (self.is_reward)      - 2
            
            old_embed   = message.embeds[0]
            embed_dict  = old_embed.to_dict()
            fields      = embed_dict['fields']
            
            fields[yes_i]['value'] = num_yes
            fields[no_i]['value']  = num_no
            
            new_embed = discord.Embed.from_dict(embed_dict)
            
            await message.edit(embed=new_embed)
            
        def make_buttons(self):
            
            button_bad  = self.base_cog.CreditVoteButton(self.base_cog, 
                                                         self.is_reward, 
                                                         not self.is_reward)
            button_good = self.base_cog.CreditVoteButton(self.base_cog, 
                                                         self.is_reward, 
                                                         self.is_reward)
            
            self.add_item(button_bad)
            self.add_item(button_good)
            
    class CreditVoteButton(Button):
        keywords = [["Innocent", "Guilty"],["Deny", "Accept"]]
        
        def __init__(self, base_cog, is_reward: bool, verdict: bool):
            self.is_reward = is_reward
            self.verdict = verdict
            self.base_cog = base_cog
            
            is_good = (is_reward ^ (not verdict))
            button_label = self.keywords[is_reward][verdict]
            button_style = ButtonStyle.green if is_good else ButtonStyle.red
            
            super().__init__(style=button_style, label=button_label, custom_id=f"creditvote_{button_label}")
            
        async def callback(self, interaction):
            msg     = interaction.message
            user    = interaction.user
            verdict = self.verdict
            vote    = self.base_cog.client.db.get_user_vote(msg.id, user.id)
            
            if vote != None:
                await interaction.response.send_message(f"You have already voted '{self.keywords[self.is_reward][vote]}' in this poll.", ephemeral=True)
                return
            
            self.base_cog.client.db.set_user_vote(msg.id, user, verdict) 
            
            await self.view.update_vote_embed(msg)
            
            await interaction.response.send_message(f"You have voted: {self.label}", ephemeral=True)

    
    async def post_vote(self, interaction, user, feat, value, cooldown, explanation):
        await interaction.response.defer()
        
        if self.client.db.get_user_active_event(user.id, feat):
            await interaction.followup.send("This has been attempted by someone too recently. Try again later",
                                            ephemeral=True)
            return
        
        is_reward = value > 0
        
        new_embed = discord.Embed(title=("__Reward Vote__" if is_reward else "__Penalty Vote__"), 
                                  color=(0x00ff00 if is_reward else 0xff0000))
        
        
        title_text = "nominated for" if is_reward else "accused of"
        inner_text = f"If supported, <@{user.id}> would receive" if is_reward else f"If found guilty, <@{user.id}> would be fined"

        new_embed.add_field(name=f"{feat}", 
                            value=f'''<@{user.id}> has been {title_text}: {feat} 
                                        {inner_text} {abs(value)} {CREDIT_NAME}.
                                        Please note that your vote cannot be changed once selected.''',
                            inline=False)
        
        if explanation:
            new_embed.add_field(name="Explanation:",
                                value= explanation,
                                inline=False)
            
        new_embed.set_thumbnail(url=user.avatar)
            
        view = self.get_vote_view(is_reward)
        
        new_embed.add_field(name=f"__{view.get_bad_button().label}__",  value="0")
        new_embed.add_field(name=f"__{view.get_good_button().label}__",  value="0")
        
        msg = await interaction.followup.send(embed=new_embed, view=view)
        msg_id = msg.id
        
        self.client.db.record_credit_change(user, 
                                            feat, 
                                            value,
                                            cooldown=cooldown, 
                                            vote_msg_id=msg_id,
                                            cause_user=interaction.user)
        await asyncio.sleep(cooldown * 60)
        
        results = self.client.db.get_votes(msg_id)
        v_yes = sum(results)
        v_no  = len(results) - v_yes
        
        await msg.delete()
        
        result_msg, verdict = await self.post_result(interaction, user, feat, value, v_yes, v_no) 
        
        await self.process_vote_result(interaction, user, feat, value, msg_id, verdict, result_msg.id)
        
        result_embed = result_msg.embeds[0]
        sc = self.client.db.get_social_credit(user)
        sc_str = f"<@{user.id}> has {sc} {CREDIT_NAME}"
        
        result_embed.add_field(name="", value=sc_str, inline=False)
        await result_msg.edit(embed=result_embed)
        
    async def process_vote_result(self, interaction, user, feat, value, msg_id, verdict, result_msg_id):

        self.client.db.process_credit_change(msg_id, verdict, result_msg_id)
        if verdict == 1:
            self.client.db.add_social_credit(user, value)
        
    async def post_result(self, interaction, user, feat, value, v_yes, v_no):
        
        pass_condition = (v_yes > v_no) and v_yes > 1
        is_reward = value > 0
        is_good =  (not is_reward ^ pass_condition)

        new_embed = discord.Embed(title=("__Reward Result__" if is_reward else "__Penalty Result__"), 
                                  color=(0x00ff00 if is_good else 0xff0000))

        title_text = None
        if pass_condition:
            
            if is_reward:
                title_text = f'''The reward for {feat} has been **GRANTED** to <@{user.id}>.
                            They have been awarded {value} {CREDIT_NAME}.'''
            else:
                title_text = f'''<@{user.id}> has been found **GUILTY** of {feat}.
                            They have been fined {abs(value)} {CREDIT_NAME}.'''
        else:
            if is_reward:
                title_text = f"The reward for {feat} has been **DENIED** to <@{user.id}>."
            else:
                title_text = f"<@{user.id}> has been found **INNOCENT** of {feat}."

        new_embed.add_field(name=f"{feat}",  value=title_text ,  inline=False)
        
        name_l, name_r = ("__Denied__", "__Accepted__") if is_reward else ("__Guilty__", "__Innocent__")
        vote_l, vote_r = (v_no, v_yes)          if is_reward else (v_yes, v_no)
        
        new_embed.add_field(name=name_l, value=vote_l, inline=True)
        new_embed.add_field(name=name_r, value=vote_r, inline=True)
        
        new_embed.set_thumbnail(url=user.avatar)

        message = await interaction.followup.send(embed=new_embed)
        
        return message, pass_condition

    class SelectCategory(Select):

        def __init__(self, base_cog, user, is_reward=None):
            self.base_cog   = base_cog
            self.user       = user
            
            category_list = self.base_cog.client.db.get_event_categories(is_reward)
            
            option_list = []
            for categ in category_list:
                option_list.append(SelectOption(label=categ, value=categ))
                
            super().__init__(placeholder="Select a category", 
                             min_values=1, 
                             max_values=1, 
                             options=option_list)
                
        async def callback(self, interaction):
            category        = self.values[0]
            select_event    = self.base_cog.SelectEventType(self.base_cog, self.user, category)
            select_view     = View()
            
            select_view.add_item(select_event)
            await interaction.response.send_message(view=select_view, ephemeral=True)
            
    class SelectEventType(Select):
        
        def __init__(self, base_cog, user, category):
            self.base_cog   = base_cog
            self.user       = user
            self.category   = category
            
            event_types = self.base_cog.client.db.get_event_types_from_category(category)
            
            option_list = []
            for event in event_types:
                name = event['event_name']
                value = event['default_value']
                new_button = SelectOption(label=name, description=f"credits: {value}", value=name) 
                option_list.append(new_button)
                
            super().__init__(placeholder="Select an event", 
                             min_values=1, 
                             max_values=1, 
                             options=option_list)
        
        async def callback(self, interaction):
            event_name = self.values[0]
            new_modal = self.base_cog.ReasonModal(self.base_cog, self.user, event_name)
            await interaction.response.send_modal(new_modal)

    class ReasonModal(Modal):
        def __init__(self, base_cog, user, event_name):
            self.title = event_name
            self.base_cog = base_cog
            self.user = user
            self.event_name = event_name
            
            super().__init__()
            
        answer = TextInput(label= "Give a short explanation:",
                           style= TextStyle.short,
                           required= False,
                           max_length= 256)
            
        async def on_submit(self, interaction: Interaction):
            explanation = self.answer.value
            details = self.base_cog.client.db.get_event_details(self.event_name)
            num_credits = details['default_value']
            cooldown = details['cooldown']
            await self.base_cog.post_vote(interaction, self.user, self.event_name, num_credits, cooldown, explanation)
    
async def setup(client):
    await client.add_cog(CreditVoting(client))
