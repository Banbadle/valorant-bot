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
        self.result_channel_id = 1045462897507172393
        self.team_channel_id   = 1029595534299766826 #949464302526545941
        
    @commands.Cog.listener()
    async def on_ready(self):

        result_channel      = self.client.get_channel(self.result_channel_id)
        
        tz = pytz.timezone('Asia/Qatar')
        soup = self.get_page()
        game_list = self.get_game_list(soup)
        self.game_list = game_list
        
        num_matches = len(game_list)
        for i in range(num_matches):
            
            # Update game_list after match 48
            if i == 48:
                soup = self.get_page()
                game_list = self.get_game_list(soup)
                self.game_list = game_list
            
            next_game = game_list[i]
            self.game_index = i
            if next_game["Score"] != None:
                continue

            wait_time = next_game["Timestamp"] - datetime.datetime.now(tz) + datetime.timedelta(hours=2, minutes=15)
            if wait_time > datetime.timedelta(0):
                await asyncio.sleep(wait_time.total_seconds())
            
            score = None
            soup  = None
            while score == None:
                new_soup = self.get_page()
                new_game_list = self.get_game_list(new_soup)
                updated_game = new_game_list[i]
            
                score = updated_game["Score"]
                        
                if score == None:
                    await asyncio.sleep(15*60)
            
            next_game["Score"]      = score
            next_game["Home"]       = updated_game["Home"]
            next_game["Away"]       = updated_game["Away"]
            next_game["Penalties"]  = updated_game["Penalties"]
            
            result_msg = self.get_game_result(next_game, result_channel)
            await result_channel.send(result_msg)
            
            # Group Stage Result
            if i <= 47:
                await self.postgroupresults(None, next_game["Home"])
            # Do not change roles on match 63 (bronze medal match)
            elif i == 62:
                await result_channel.send("(This is the third place play-off match and has no impact on the sweepstake)")
            # Knockout Stage Result
            else:
                await self.postknockoutresult(None, i)
    
    @commands.command()
    @commands.check(is_admin)
    async def postgroupresults(self, ctx, team_name):
            
        # CODE FOR END OF GROUP STAGE
        opp_list = self.get_played_opponents(team_name)
        
        if len(opp_list) >= 3:
            
            for opp in opp_list:
                new_opp_list = self.get_played_opponents(opp)
                if len(new_opp_list) < 3:
                    break
            else:
                # Find group standings
                opp_list.append(team_name)
                group_order, g_num = self.get_group_order(opp_list[:3])
                group_order = [team.replace(" ", "-") for team in group_order]
                
                # Adjust roles
                team_channel = self.client.get_channel(self.team_channel_id)
                sw = self.client.get_cog("Sweepstake")
                role1, role3 = await sw.addresult(team_channel, group_order[0], group_order[2])
                role2, role4 = await sw.addresult(team_channel, group_order[1], group_order[3])
                
                # Announce Adjustments
                member_third  = role3.members[0]
                member_fourth = role4.members[0]
                msg0 = f"Group {'ABCDEFGH'[g_num]} has concluded"
                msg1 = f"{role4.mention} came 4th and has been eliminated.\n{member_fourth.mention} has been reassigned the 2nd Place team: {role2.mention}"
                msg2 = f"{role3.mention} came 3rd and has been eliminated.\n{member_third.mention} has been reassigned the 1st Place team: {role1.mention}"
                
                await team_channel.send(msg0)
                await asyncio.sleep(5)
                await team_channel.send(msg1)
                await asyncio.sleep(5)
                await team_channel.send(msg2)     

    def get_result_from_score(self, home, away, score):
        g_home, g_away = score.split("–")
        g_home, g_away = int(g_home), int(g_away)
        
        winner, loser = None, None
        if g_home > g_away:
            winner = home
            loser  = away
        elif g_home < g_away:
            winner = away
            loser  = home
            
        return winner, loser
                
    @commands.command()
    @commands.check(is_admin)
    async def postknockoutresult(self, ctx, match_index):
        
        i = int(match_index)
        
        if i > 47 and i != 62:
        
            team_channel = self.client.get_channel(self.team_channel_id)
            game = self.game_list[i]
            
            winner, loser = None, None

            # Find match winner
            while winner == None:
                # Should avoid loop if game has not finished
                if game["Score"] == None:
                    return
                
                # Find FT match winner
                winner, loser = self.get_result_from_score(game["Home"], game["Away"], game["Score"])
                
                # Find winner if tied (and has penalties)
                if winner == None:
                    if game["Penalties"] != None:
                        winner, loser = self.get_result_from_score(game["Home"], game["Away"], game["Penalties"])
                    
                    if winner == None:
                        asyncio.sleep(15*60)
                        new_soup = self.get_page()
                        new_game_list = self.get_game_list(new_soup)
                        updated_game = new_game_list[i]
                        
                        game["Score"]     = updated_game["Score"]
                        game["Penalties"] = updated_game["Penalties"]
                
            # Adjust roles
            opp_list = self.get_played_opponents(loser)
            teams_played = len(opp_list)
            
            winner_role_name = winner.replace(" ", "-")
            loser_role_name  = loser.replace(" ", "-")
            sw = self.client.get_cog("Sweepstake")
            winner_role, loser_role = await sw.addresult(team_channel, winner_role_name, loser_role_name, teams_played)
            
            # Announce Adjustments
            members = loser_role.members
            members_str = "> " + "\n> ".join(member.mention for member in members)
            msg = f"{loser_role.mention} has been eliminated.\nThe following people have been reassigned {winner_role.mention}:\n{members_str}"
            await team_channel.send(msg)
            
            # Update self.game_list with winner
            new_soup = self.get_page()
            new_game_list = self.get_game_list(new_soup)
            for k in range(64):
                game         = self.game_list[k]
                updated_game = new_game_list[k]
                game["Home"] = updated_game["Home"]
                game["Away"] = updated_game["Away"]
                        
    def get_next_game(self):
        return self.game_list[self.game_index]
                
    def get_game_result(self, game, channel):
        home = game["Home"].replace(" ", "-")
        away = game["Away"].replace(" ", "-")
        home_flag = country_flag_map[home]
        away_flag = country_flag_map[away]
        home_mention = discord.utils.get(channel.guild.roles,name=home).mention
        away_mention = discord.utils.get(channel.guild.roles,name=away).mention

        extra_str = (f"\nPenalties: {home_flag} ({game['Penalties']}) {away_flag}") * (game["Penalties"] != None)

        return f"{home_mention} {home_flag} {game['Score']} {away_flag} {away_mention}" + (extra_str)
    
    def get_played_opponents(self, team_name): 
        opponent_list = []
        for game in self.game_list:
            if game["Score"] != None:
                if game["Home"] == team_name:
                    opponent_list.append(game["Away"])
                elif game["Away"] == team_name:
                    opponent_list.append(game["Home"])
                
        return opponent_list
    
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
        
    def get_page(self):
        group_url = "https://en.wikipedia.org/wiki/2022_FIFA_World_Cup#Group_stage"
        result = requests.get(group_url)
        soup = BeautifulSoup(result.text, "html.parser")
        
        return soup
        
    def get_game_list(self, soup):
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
            full_score = game.find("th", {"class": "fscore"})
            score = full_score.findAll("a")[0]
            score = score.get_text()
            game_dict["Score"] = score if score[0] != "M" else None
            
            # Penalties
            fgoals_list = game.findAll("tr", {"class": "fgoals"})
            if len(fgoals_list) == 2:
                pens = fgoals_list[1].find("th")
                game_dict["Penalties"] = pens.get_text()
            else:
                game_dict["Penalties"] = None
            
            game_list.append(game_dict)
        
        ordered_game_list = sorted(game_list, key=lambda d: d["Timestamp"])
        
        return ordered_game_list
    
    # Output: (table_team_list, i)
    #     table_team_list: ordered list of the tables teams
    #     i: the index corresponding to their group (0=A, 1=B, etc)
    def get_group_order(self, team_list):
        soup = self.get_page()
        headers = soup.findAll("abbr", {"title": "Points"}, string="Pts")
        for g_num in range(len(headers)):
            hd = headers[g_num]
            table = hd.parent.parent.parent
            entry_list = [ref.get_text() for ref in table.findAll("a")]
            
            table_team_list = []
            for entry in entry_list:
                if entry in team_list:
                    table_team_list.append(entry)
                    
            if len(table_team_list)==4:
                return table_team_list, g_num
                
    
def setup(client):
    client.add_cog(Groupscrape(client))
    
