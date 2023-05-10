import discord
from discord.ext import commands
import sys
import requests

ranks = ('Unrated', 'Unrated', 'Unrated', 'Iron 1', 'Iron 2', 'Iron 3', 'Bronze 1', 'Bronze 2', 'Bronze 3', 'Silver 1', 'Silver 2', 'Silver 3', 'Gold 1', 'Gold 2', 'Gold 3', 'Platinum 1', 'Platinum 2', 'Platinum 3', 'Diamond 1', 'Diamond 2', 'Diamond 3', 'Ascendant 1', 'Ascendant 2', 'Ascendant 3', 'Imortal 1', 'Imortal 2', 'Imortal 3', 'Radiant')
rank_brackets = ((1,2,3,4,5,6,7,8,9), (7,8,9,10,11,12), (10,11,12,13,14,15), (13,14,15,16), (14,15,16,17), (15,16,17,18), (16,17,18,19,20,21), (21,22))
rank_ranges = ((1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 13), (1, 13), (1, 13), (7, 16), (7, 16), (7, 16), (10, 17), (10, 18), (10, 19), (13, 22), (14, 22), (15, 22), (16, 22), (16, 22), (16, 23), (21, 23))

class Valranks(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(sys.argv[0])

    def num_to_rank(self, num):
        return ranks[num]

    def get_rank_icon(self, rankText):
        num = self.get_rank_num(rankText)+3
        return f"https://trackercdn.com/cdn/tracker.gg/valorant/icons/tiers/{num}.png"

    def get_tracker_from_ids(self, username, tag):
        return f"https://tracker.gg/valorant/profile/riot/{username}%23{tag}/overview?playlist=competitive"

    def get_rank_range(self, num):
        return rank_ranges[num]

    def get_player_rank(self, user_id):
        user = self.client.db.get_valorant_username(user_id)
        url = f"https://api.henrikdev.xyz/valorant/v1/mmr-history/eu/{user['val_username']}/{user['val_tag']}"

        response = requests.get(url).json()
        lastGame = response['data'][0]

        return (lastGame['currenttier'], lastGame['ranking_in_tier'])

    @commands.command(help = "Lists the ranks of everyone with the 'Agents' role.")
    @commands.guild_only()
    @commands.cooldown(1, 1*60)
    async def ranks(self, ctx):
        '''Lists the ranks of everyone with the 'Agents' role.'''
        rankList = []
        agents = discord.utils.get(ctx.guild.roles, name="Agents").members
        for member in agents:
            valorant = self.client.db.get_valorant_username(member.id)
            if not valorant:
                continue

            if None in valorant.values():
                continue

            try:
                rank = self.get_player_rank(member.id)
            except:
                rank = "Unknown"

            rankList.append((rank, member.name))

        rankList.sort(reverse=True)

        memberStr = '\n'.join([u for (_, u) in rankList])
        rankStr = '\n'.join([f"{self.num_to_rank(t)} ({rr} RR)" for ((t, rr), _) in rankList])

        newEmbed = discord.Embed(title="__Leaderboard__", color=0xff0000)

        newEmbed.add_field(name="__Player__", value=memberStr, inline=True)
        newEmbed.add_field(name="__Rank__", value=rankStr, inline=True)

        await ctx.send(embed=newEmbed)

async def setup(client):
    await client.add_cog(Valranks(client))
