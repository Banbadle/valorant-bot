from discord.ext import commands
from discord import app_commands, Interaction
from checks import is_admin
import discord

def slash_is_admin(interaction: Interaction):
    return interaction.client.db.is_admin(interaction.user.id)

class VoteCommands(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        
        print("votecommands.py loaded")
        
    @commands.command(help = "Shows the social credits of a user")
    async def showcredits(self, ctx, user_mention: str):
        user_id = int(user_mention[2:-1])
        sc = self.client.db.get_social_credit(user_id)
        if sc != None:
            await ctx.channel.send(f"{user_mention} has {sc} social credits")
        else:
            await ctx.channel.send(f"I could not find a user in my database called {user_mention}")
        
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
        embed_dict = base_embed.to_dict()
        embed_dict['fields'].pop()
        embed_dict['fields'].pop()
        new_embed = discord.Embed.from_dict(embed_dict)
        
        await message.edit(embed=new_embed)
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

            field = embed_dict['fields'][-1]
            field['value'] = f"~~{field['value']}~~" + "\n\n" + "__**VOIDED**__"
            
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