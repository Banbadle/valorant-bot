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
        
    @commands.command()
    @commands.check(is_admin)
    async def addevent(self, ctx, event_name, default_value, event_category="Misc", cooldown=10, public="TRUE"):
        self.client.db.add_credit_event_type(event_name, 
                                             default_value,
                                             event_category=event_category,
                                             cooldown=cooldown,
                                             public=public)
        
    @commands.command()
    @commands.check(is_admin)
    async def deleteevent(self, ctx, event_name):
        self.client.db.delete_credit_event_type(event_name)
        
    @commands.command()
    @commands.check(is_admin)
    async def modifyevent(self, ctx, event_name, column_name, new_value):
        self.client.db.modify_event(event_name, column_name, new_value)
        
    @commands.command()
    @commands.check(is_admin)
    async def changecategoryname(self, ctx, category_name_old, category_name_new):
        self.client.db.change_category_name(category_name_old, category_name_new)
        
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
        
    @commands.command()
    @commands.check(is_admin)
    async def voidvote(self, ctx):
        print("RUN:")
        
        db = self.client.db
        result_msg_id = ctx.message.reference.message_id
        details = db.get_credit_change(result_msg_id)
        
        if not details:
            return
        
        user_id = int(details['user_id'])
        user = self.client.get_user(user_id)
        
        if details['processed'] == 1:
            inv_num = -int(details['change_value'])
            
            result_msg = await ctx.channel.fetch_message(result_msg_id)
            base_embed = result_msg.embeds[0]
            embed_dict = base_embed.to_dict()

            field = embed_dict['fields'][-1]
            field['value'] = f"~~{field['value']}~~" + "\n\n" + "__**VOIDED**__"
            
            new_embed = discord.Embed.from_dict(embed_dict)
            
            await result_msg.edit(embed=new_embed)
            
            db.void_credit_change(result_msg_id)
            db.add_social_credit(user, inv_num)   
        
async def setup(client):
    await client.add_cog(VoteCommands(client))