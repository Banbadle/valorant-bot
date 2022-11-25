import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import datetime
import pytz
import asyncio
from checks import is_admin

class Groupscrape(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("groupscrape.py loaded")
        
        tz = pytz.timezone('Asia/Qatar')
        game_list = self.get_game_list()
        upcoming_game_list = [game for game in game_list if game["Score"] == None]
        
        for next_game in upcoming_game_list:
            self.next_game = next_game
            wait_time = next_game["Timestamp"] - datetime.datetime.now(tz) + datetime.timedelta(hours=2)
            await asyncio.sleep(wait_time.total_seconds())
            
            score = None
            while score == None:
                new_game_list = self.get_game_list()
                played_games_list = [game for game in new_game_list if game["Score"] != None]
                
                for played_game in played_games_list:
                    if played_game["Home"] == next_game["Home"] and played_game["Away"] == next_game["Away"] and played_game["Date"] == next_game["Date"]:
                        score = played_game["Score"]
                        
                if score != None:
                    await asyncio.sleep(15*60)
            
            await 
            
    @commands.command()
    @commands.check(is_admin)        
    async def timeuntil(self, ctx):
        game = self.next_game
        tz = pytz.timezone('Asia/Qatar')
        wait_time = game["Timestamp"] - datetime.datetime.now(tz)
        print(game["Timestamp"])
        print(datetime.datetime.now(tz))
        await ctx.reply(wait_time)
        
    @commands.command()
    @commands.check(is_admin)        
    async def nextmatch(self, ctx): 
        game = self.next_game
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
    
