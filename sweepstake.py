import discord
from discord.ext import commands
import random
from checks import is_admin
import asyncio

country_flag_map = {"Netherlands": ":flag_nl:",\
"Ecuador": ":flag_ec:" ,\
"Senegal": ":flag_sn:",\
"Qatar": ":flag_qa:",\
"England": ":england:",\
"United-States": ":flag_us:",\
"Iran": ":flag_ir:",\
"Wales": ":wales:" ,\
"Poland": ":flag_pl:",\
"Argentina": ":flag_ar:",\
"Mexico": ":flag_mx:",\
"Saudi-Arabia": ":flag_sa:",\
"France": ":flag_fr:",\
"Denmark": ":flag_dk:",\
"Tunisia": ":flag_tn:",\
"Australia": ":flag_au:",\
"Germany": ":flag_de:",\
"Spain": ":flag_es:",\
"Costa-Rica": ":flag_cr:",\
"Japan": ":flag_jp:",\
"Croatia": ":flag_hr:",\
"Belgium": ":flag_be:",\
"Canada": ":flag_ca:",\
"Morocco": ":flag_ma:" ,\
"Switzerland": ":flag_ch:",\
"Serbia": ":flag_rs:",\
"Brazil": ":flag_br:",\
"Cameroon": ":flag_cm:",\
"Portugal": ":flag_pt:",\
"Uruguay": ":flag_uy:",\
"Ghana": ":flag_gh:",\
"South-Korea": ":flag_kr:"}
    
class Sweepstake(commands.Cog):
        
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("sweepstake.py loaded")
        
    def get_flag(self, country):
        return country_flag_map[country]
        
    @commands.command()
    @commands.check(is_admin)
    async def checkroles(self, ctx):
        for country in country_flag_map:
            role = discord.utils.get(ctx.guild.roles,name=country)
            if role == None:
                await ctx.reply(f"Could not find role: {country}")
                return
            
        await ctx.reply("All country roles have been created")
        
    @commands.command()
    @commands.check(is_admin)  
    async def startsweepstake(self, ctx):
        role_list = ctx.guild.roles
        role_list = list(role for role in role_list if role.name in country_flag_map)
        if len(role_list) != 32:
            await ctx.reply(f"{len(role_list)} country ranks found. Expected 32")
            return
        
        paid_role  = discord.utils.get(ctx.guild.roles,name="Paid")
        if paid_role == None:
            await ctx.reply("No 'Paid' rank found")
        paid_users = paid_role.members
        if len(paid_users) != 32:
            await ctx.reply(f"{len(paid_users)} users found with 'Paid' rank. Expected 32")
            return
        
        random.shuffle(paid_users)
        random.shuffle(role_list)
        
        for i in range(0,len(paid_users)):
            user = paid_users[i]
            role = role_list[i]
            await user.add_roles(role)
            await ctx.channel.send(f"{user.mention} has been given: {self.get_flag(role.name)} {role.name}")
            await asyncio.sleep(2*60)

        new_embed = discord.Embed(title="__Initial Teams__", color=0x30cc74)

        user_str = '\n'.join([user.mention for user in paid_users])
        role_str = '\n'.join([f"{self.get_flag(role.name)} {role.name}" for role in role_list])

        new_embed.add_field(name="__User__", value=user_str, inline=True)
        new_embed.add_field(name="__Team__", value=role_str, inline=True)
            
        await ctx.channel.send("", embed=new_embed)
            
    @commands.command()
    @commands.check(is_admin)
    async def addrole(self, ctx, role_name):
        role = discord.utils.get(ctx.guild.roles,name=role_name)
        user = ctx.author
        await user.add_roles(role)

    @commands.command()
    @commands.check(is_admin)  
    async def addresult(self, ctx, team1, team2):
        role1 = discord.utils.get(ctx.guild.roles,name=team1)
        role2 = discord.utils.get(ctx.guild.roles,name=team2)
        
        for user in role2.members:
            await user.add_roles(role1)
            
        await role2.edit(colour=discord.Colour(0xec1c68))

    @commands.command()
    @commands.check(is_admin) 
    async def resetcolors(self, ctx):
        role_list = ctx.guild.roles
        role_list = list(role for role in role_list if role.name in country_flag_map)
        if len(role_list) != 32:
            await ctx.reply(f"{len(role_list)} country ranks found. Expected 32")
            return

        for role in role_list:
            await role.edit(colour=discord.Colour(0x30cc74))

    @commands.command()
    @commands.check(is_admin) 
    async def createroles(self, ctx):
        role_list = ctx.guild.roles
        role_list = list(role for role in role_list if role.name in country_flag_map)
        if len(role_list) != 0:
            await ctx.reply(f"some country ranks were already found: {list(role.name for role in role_list)}.")
            return

        guild = ctx.guild
        for country in country_flag_map:
            await guild.create_role(name=country, colour=discord.Colour(0x30cc74))

    @commands.command()
    @commands.check(is_admin)      
    async def deleteroles(self, ctx):
        role_list = ctx.guild.roles
        role_list = list(role for role in role_list if role.name in country_flag_map)
        for role in role_list:
            await role.delete()

def setup(client):
    client.add_cog(Sweepstake(client))
