import discord
from discord.ext import commands
import sys
from bs4 import BeautifulSoup
import requests

ranks = ('Unrated', 'Iron 1', 'Iron 2', 'Iron 3', 'Bronze 1', 'Bronze 2', 'Bronze 3', 'Silver 1', 'Silver 2', 'Silver 3', 'Gold 1', 'Gold 2', 'Gold 3', 'Platinum 1', 'Platinum 2', 'Platinum 3', 'Diamond 1', 'Diamond 2', 'Diamond 3', 'Imortal 1', 'Imortal 2', 'Imortal 3', 'Radiant')
rank_brackets = ((1,2,3,4,5,6,7,8,9), (7,8,9,10,11,12), (10,11,12,13,14,15), (13,14,15,16), (14,15,16,17), (15,16,17,18), (16,17,18,19,20,21), (21,22))
rank_ranges = ((1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 10), (1, 13), (1, 13), (1, 13), (7, 16), (7, 16), (7, 16), (10, 17), (10, 18), (10, 19), (13, 22), (14, 22), (15, 22), (16, 22), (16, 22), (16, 23), (21, 23))

class Valranks(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(sys.argv[0])

    def get_rank_num(self, rankText):
        return (None if rankText not in ranks else ranks.index(rankText))
    
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
        tracker = f"https://tracker.gg/valorant/profile/riot/{user['val_username']}%23{user['val_tag']}/overview?playlist=competitive"
    
        source = requests.get(tracker).text
        soup = BeautifulSoup(source, 'html.parser')
        rankSpan = soup.find("span", {"class":"valorant-highlighted-stat__value"})
        rank = rankSpan.text
    
        return rank
  
    @commands.command()
    async def ranks(self, ctx):
        memberList = []
        rankList = []
        for member in discord.utils.get(ctx.guild.roles,name="Agents").members:
            if not self.client.db.get_valorant_username(member.id): continue
            username, tag = self.client.db.get_valorant_username(member.id)
            if not username or not tag: continue
            memberList.append(f"> {member.name}")
            try:
                memberRank = self.get_player_rank(member.id)
                rankList.append(memberRank)
            except:
                rankList.append("Unknown")

        rank_num_list = [self.get_rank_num(rank) if rank != "Unknown" else -1 for rank in rankList]
        print(rank_num_list)

        zip_list = zip(rank_num_list, memberList, rankList)
        sorted_zip_list = sorted(zip_list, reverse=True)

        orderedMemberList = [m for _,m,_ in sorted_zip_list]
        orderedRankList = [r for _,_,r in sorted_zip_list]

        memberStr = "\n".join(orderedMemberList)
        rankStr = "\n".join(orderedRankList)

        newEmbed = discord.Embed(title="__Leaderboard__", color=0xff0000)

        newEmbed.add_field(name="__Player__", value=memberStr, inline=True)
        newEmbed.add_field(name="__Rank__", value=rankStr, inline=True)

        await ctx.send(embed=newEmbed)

def setup(client):
    client.add_cog(Valranks(client))
    