import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import datetime
import pytz
import asyncio
from checks import is_admin
from sweepstake import country_flag_map

class Groupscrape(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):

        channel_id = 1045462897507172393
        channel = self.client.get_channel(channel_id)
        tz = pytz.timezone('Asia/Qatar')
        game_list = self.get_game_list()
        self.game_list = game_list
        #upcoming_game_list = [game for game in game_list if game["Score"] == None]
        
        num_matches = len(game_list)
        for i in range(num_matches):
            next_game = game_list[i]
            self.game_index = i
            if next_game["Score"] != None:
                continue

            wait_time = next_game["Timestamp"] - datetime.datetime.now(tz) + datetime.timedelta(hours=2)
            if wait_time > datetime.timedelta(0):
                await asyncio.sleep(wait_time.total_seconds())
            
            score = None
            while score == None:
                new_game_list = self.get_game_list()
                updated_game = new_game_list[i]
            
                score = updated_game["Score"]
                        
                if score == None:
                    await asyncio.sleep(5*60)
            
            next_game["Score"] = score
            
            msg = self.get_game_result(next_game, channel)
            await channel.send(msg)
                
    def get_next_game(self):
        return self.game_list[self.game_index]
                
    def get_game_result(self, game, channel):
        home = game["Home"].replace(" ", "-")
        away = game["Away"].replace(" ", "-")
        home_flag = country_flag_map[home]
        away_flag = country_flag_map[away]
        home_mention = discord.utils.get(channel.guild.roles,name=home).mention
        away_mention = discord.utils.get(channel.guild.roles,name=away).mention
        return f"{home_mention} {home_flag} {game['Score']} {away_flag} {away_mention}"
    
    @commands.command()
    @commands.check(is_admin)
    async def postprevresults(self, ctx):
        for game in self.game_list:
            if game["Score"] == None:
                break
            await ctx.send(self.get_game_result(game, ctx.channel))
            
    @commands.command()
    @commands.check(is_admin)        
    async def timeuntil(self, ctx):
        game = self.get_next_game()
        tz = pytz.timezone('Asia/Qatar')
        wait_time = game["Timestamp"] - datetime.datetime.now(tz)
        await ctx.reply(wait_time)
        
    @commands.command()
    @commands.check(is_admin)        
    async def nextmatch(self, ctx): 
        game = self.get_next_game()
        home = game["Home"]
        away = game["Away"]
        await ctx.reply(f"Next match is: {home} vs {away}")
        
    def get_game_list(self):
    
        group_url = "https://en.wikipedia.org/wiki/2022_FIFA_World_Cup#Group_stage"
        result = requests.get(group_url)
        soup = BeautifulSoup(result.text, "html.parser")
        games = soup.find_all("div", {"class": "footballbox"})
        
        game_list = []
        
        for game in games:
            game_dict = {}
            
            # Date of match
            date = game.find("span", {"class": "bday dtstart published updated"})
            date_text = date.get_text()
            game_dict["Date"] = date_text
            
            # Time of match
            time = game.find("div", {"class": "ftime"})
            time_text = time.get_text()
            game_dict["Time"] = time_text
            
            # Unix timestamp of match
            tz = pytz.timezone('Asia/Qatar')
            unix_num_list = list([*date_text.split("-"), *time_text.split(":")])
            unix_num_list = list(int(num) for num in unix_num_list)
            unix_time = datetime.datetime(*unix_num_list)
            timestamp = tz.localize(unix_time)
            game_dict["Timestamp"] = timestamp
            
            # Home team
            home_team = game.find("th", {"itemprop": "homeTeam"})
            game_dict["Home"] = home_team.get_text(strip=True)
            
            # Away team
            away_team = game.find("th", {"itemprop": "awayTeam"})
            game_dict["Away"] = away_team.get_text(strip=True)
            
            # Score
            score = game.find("th", {"class": "fscore"})
            score = score.get_text()
            game_dict["Score"] = score if score[0] != "M" else None
            
            game_list.append(game_dict)
        
        ordered_game_list = sorted(game_list, key=lambda d: d["Timestamp"])
        
        return ordered_game_list
            
    def update_group(char):
        group_template_url = f"https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_Group_{char}"
        result = requests.get(group_template_url)
    
def setup(client):
    client.add_cog(Groupscrape(client))
    
