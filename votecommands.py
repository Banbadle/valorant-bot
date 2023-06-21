from discord.ext import commands
from discord import app_commands, Interaction
from checks import slash_is_admin
import discord

class VoteCommands(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        
        print("votecommands.py loaded")
        
    @commands.command(help = "Shows the social credits of a user")
    async def showcredits(self, ctx, user_mention: str):
        user_id = int(user_mention[2:-1])
        user = await self.client.fetch_user(user_id)
        sc = self.client.db.get_social_credit(user)
        if sc != None:
            await ctx.channel.send(f"{user_mention} has {sc} social credits")
        else:
            await ctx.channel.send(f"I could not find a user in my database called {user_mention}")
            
    @commands.command(help = "Shows a snippet of the social credit standings")
    async def leaderboard(self, ctx):
        user_list = self.client.db.get_all_social_credits()
        
        new_embed = discord.Embed(title="__Social Credits__", color=0xFFFFFF)
        values = {'Rank': [], 'User': [], 'Social Credit': []}
        
        n = 13 # Number to show
        size = len(user_list)
        top_bound = min(size, n)
        for i in range(0,top_bound):
            values['Rank'].append(f"#{i+1}")
            values['User'].append(f"<@{user_list[i]['id']}>")
            values['Social Credit'].append(str(user_list[i]['social_credit']))
        
        bottom_bound = max(size-n, top_bound)
        if bottom_bound != top_bound:
            for index in values:
                values[index].append("⋮\n⋮")
            
        for j in range(bottom_bound, size):
            values['Rank'].append(f"#{j+1}")
            values['User'].append(f"<@{user_list[j]['id']}>")
            values['Social Credit'].append(str(user_list[j]['social_credit']))
            
        value_strings = {key: "\n".join(vals) for key, vals in values.items()}
        
        new_embed.add_field(name="Rank", value=value_strings["Rank"], inline=True)
        new_embed.add_field(name="User", value=value_strings["User"], inline=True)
        new_embed.add_field(name="Social Credit", value=value_strings["Social Credit"], inline=True)
    
        await ctx.reply(embed=new_embed)
        
    @app_commands.command(name="addevent")
    @app_commands.check(slash_is_admin)
    async def addevent(self, 
                       interaction: Interaction, 
                       event_name: str, 
                       default_value: int, 
                       event_category: str, 
                       cooldown: int=10, 
                       public: str="TRUE"):
        
        self.client.db.add_credit_event_type(event_name, 
                                             default_value,
                                             event_category=event_category,
                                             cooldown=cooldown,
                                             public=public)
        await interaction.response.send_message(f"Added {event_category} - {event_name}", 
                                                ephemeral=True)
        
    @app_commands.command(name="deleteevent")
    @app_commands.check(slash_is_admin)
    async def deleteevent(self, interaction: Interaction, event_name: str):
        self.client.db.delete_credit_event_type(event_name)
        await interaction.response.send_message(f"{event_name} has been deleted", 
                                                ephemeral=True)
        
    @app_commands.command(name="modifyevent")
    @app_commands.check(slash_is_admin)
    async def modifyevent(self, interaction: Interaction, event_name: str, column_name: str, new_value: str):
        self.client.db.modify_event(event_name, column_name, new_value)
        await interaction.response.send_message(f"{event_name}'s {column_name} has been changed to {new_value}", 
                                                ephemeral=True)
        
    @app_commands.command(name="changecategoryname")
    @app_commands.check(slash_is_admin)
    async def changecategoryname(self, interaction: Interaction, old_category_name: str, new_category_name: str):
        self.client.db.change_category_name(old_category_name, new_category_name)
        await interaction.response.send_message(f"{old_category_name} has been changed to {new_category_name}", 
                                                ephemeral=True)
        
    @app_commands.command(name="forceresult")
    @app_commands.check(slash_is_admin)
    async def forceresult(self, interaction: Interaction, user_mention: str, feat: str, value: int):
        user_id = int(user_mention[2:-1])
        user = self.client.get_user(user_id)
        
        cv = self.client.get_cog("CreditVoting")
        
        await interaction.response.defer()
        
        message, _ = await cv.post_result(interaction, user, feat, value, 99, 0)
        base_embed = message.embeds[0]

        await message.edit(embed=base_embed)
        msg_id = message.id
        
        self.client.db.record_credit_change(user,
                                            event_name=feat, 
                                            change_value=value,
                                            cooldown=0,
                                            vote_msg_id=msg_id,
                                            cause_user=None, 
                                            processed=None)
        
        await cv.process_vote_result(interaction, user, feat, value, msg_id, 1, msg_id)
        
    @app_commands.command(name="voidvote")
    @app_commands.check(slash_is_admin)
    async def voidvote(self, interaction: Interaction, result_msg_id: str):
        
        db = self.client.db
        result_msg_id = int(result_msg_id)
        details = db.get_credit_change(result_msg_id)
        
        if not details:
            await interaction.response.send_message("This id does not correspond to a vote message in the database", 
                                                    ephemeral=True)
            return
        
        user_id = int(details['user_id'])
        user = self.client.get_user(user_id)
        
        if details['processed'] == 1:
            inv_num = -int(details['change_value'])
            
            result_msg = await interaction.channel.fetch_message(result_msg_id)

            base_embed = result_msg.embeds[0]
            embed_dict = base_embed.to_dict()
            
            for field in embed_dict['fields']:
                field['value'] = f"~~{field['value']}~~"
                
            embed_dict['title'] = "__**VOIDED**__"
            
            new_embed = discord.Embed.from_dict(embed_dict)
            
            await result_msg.edit(embed=new_embed)
            
            db.void_credit_change(result_msg_id)
            db.add_social_credit(user, inv_num)   
            
            await interaction.response.send_message("This vote has been voided", 
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("This vote has not passed, or is already void", 
                                                    ephemeral=True)
            
            
        
async def setup(client):
    await client.add_cog(VoteCommands(client))