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
    async def postcurrentroles(self, ctx):
        first_role = ctx.guild.roles[0]
        print(first_role)
        print(first_role.colour)
        for role in ctx.guild.roles:
            print(role.colour)
        role_list = [role for role in ctx.guild.roles if role.colour == discord.Colour(0x30cc74)]
        print(role_list)
        
        role_str_list = []
        for role in role_list:
            member_mentions = [member.mention for member in role.members]
            flag = country_flag_map[role.name]
            role_str = f"{role.mention} {flag}:\n> " + "\n> ".join(member_mentions)
            role_str_list.append(role_str)
            
        msg = "Current Teams:\n" + "\n".join(role_str_list)
        await ctx.send(msg)

    @commands.command()
    @commands.check(is_admin)  
    async def addresult(self, ctx, team1, team2, games_played=3):
        games_played = int(games_played)
        i = games_played - 3
        colour_list = [0xec1c68, 0xff5018, 0xfcad00, 0xf2fd0e, 0x9affa4]
        loss_colour = discord.Colour(colour_list[i])
        
        role1 = discord.utils.get(ctx.guild.roles,name=team1)
        role2 = discord.utils.get(ctx.guild.roles,name=team2)
        
        if i != 4:     # Do not reassign roles on final match
            for user in role2.members:
                await user.add_roles(role1)
            
        await role2.edit(colour=loss_colour)
        await role1.edit(position=32)
        
        return [role1, role2]
    
    @commands.command()
    @commands.check(is_admin)  
    async def postpotwins(self, ctx):
        colour_list = [0x30cc74, 0xec1c68, 0xff5018, 0xfcad00, 0xf2fd0e, 0x9affa4]
        prize_list  = [30,       20,       15,       10,       5,        0       ]
        colour_dict = {}
        for k in range(len(colour_list)):
            colour = discord.Colour(colour_list[k])
            colour_dict[colour] = prize_list[k]

        paid_role  = discord.utils.get(ctx.guild.roles,name="Paid")
        paid_users = paid_role.members
        
        user_dict = {user.mention: [None,None] for user in paid_users}
        for user in paid_users:
            for role in user.roles:
                if role.colour == discord.Colour(0x30cc74):
                    user_dict[user.mention][0] = role

                if role.colour in colour_dict:
                    new_prize = colour_dict[role.colour]
                    old_prize = user_dict[user.mention][1]
                    if old_prize == None or new_prize < old_prize:
                        user_dict[user.mention][1] = new_prize
                    
        team_dict = {team: [] for user_mention, (team, prize) in user_dict.items()}
        print(user_dict)
        for user_mention, (team, prize) in user_dict.items():
            team_dict[team].append((prize, user_mention))

        prize_str_list = []
        for team in team_dict:
            
            # Skip if no potential prize 
            if team == None:
                print("SKIP")
                continue
            
            sorted_prizes = sorted(team_dict[team], reverse=True)
            team_dict[team] = sorted_prizes
            flag = country_flag_map[team.name]
            
            user_prize_str_list = [f"{user_mention}: £{prize}" for prize, user_mention in sorted_prizes]
            
            prize_str = f"{team.mention} {flag}:\n> " + "\n> ".join(user_prize_str_list)
            prize_str_list.append(prize_str)
            
        header = "Potential Prizes" if len(prize_str_list) != 1 else "Prizes"
        msg = f"{header}:\n" + "\n".join(prize_str_list)
        await ctx.send(msg)

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

async def setup(client):
    await client.add_cog(Sweepstake(client))
