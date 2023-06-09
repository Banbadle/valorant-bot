import discord
from random import choice
from discord.ext import commands

class StratRoulette(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    
    key_list    = ["W", "S", "A", "D", "Space", "Crouch", "Walk", "Aim"]
    side_list   = ["attack", "defend"]
    stat_list   = ["kills", "assists", "deaths", "money"]
    player_list = ["the player (or players) with the most {stat}", "the player (or players) with the least {stat}"]
    gun_list    = ["classic", "shorty", "frenzy", "ghost", "sheriff", "stinger", "spectre", "bulldog", "guardian", "marshal", "operator", "bucky", "judge", "phantom", "vandal", "ares", "odin"]
    
    basic_strats = [["Ult point farm",          "All ult points on the map must be captured (by either team) before you can kill any opponents."],
                    ["New York Reload",         "Once you have emptied your magazine, you must drop your gun. You may pick up any other gun so long as you were not the last person to shoot it."],
                    ["Powerless",               "No one is allowed to use abilities."],
                    ["Gungame",                 "Every kill this round must be performed with a different weapon."],
                    ["Shoutcasters",            "Every player that is alive must narrate every action that they make."],
                    ["Trickshot",               "Everytime you encounter an enemy, you must 360 before you are allowed to shoot them."],
                    ["High Roller",             "Everyone must buy the most expensive gun that they can afford."],
                    ["Cheapskates",             "No one may spend more than 2000 credits this round"],
                    ["Noob Callouts",           "You may not use any regular callout locations. Any location you callout should be confusing to a random (eg. greg and gleg)."],
                    ["Sound of Silence",        "Everyone on your team must set their game's master volume to 0."],
                    ["Knives Out",              "You may only move while holding your knife."],
                    ["One by One",              "Only one player can leave spawn at a time, the rest of the team must do their best to hide in spawn."],
                    ["Hide and Seek",           "You have until the start of the round to hide somewhere. You may not move until you spot an enemy player."],
                    ["Burst Fire",              "Everyone must use a stinger or bulldog, and must be scoped in when shooting. If you cannot afford either, you may only right click with the classic."],
                    ["Sam Special",             "You may only use shotguns this round."],
                    ["Is For Me?",              "Whenever you see a smoke, you must stay inside of it as long as possible."],
                    ["Toxic Team",              "Everyone must be incredibly toxic. If a player gives any form of complimentt they may not shoot for the rest of the round."],
                    ["Konami Code",             "You may only say the following words this round: up, down, left, right, b, a, start"],
                    ["Trickle Down",            "Everyone's gun is chosen and bought by the person above them on the leaderboard. The top frag must use whatever gun they currently have."],
                    ["Now or Later",            "If you shoot before the spike is planted, you may not do so after it has been planted. The same goes for abilities."],
                    ["Full Rush",               "Everyone must hold W for the entire round."],
                    ["Jumpy Aim",               "Everyone must bind the 'jump' and 'shoot' buttons to the same key."],
                    ["Bunny Hops",              "You must bunny hop any time you are moving."],
                    ["Eagle Eyed",              "You must stay aimed down sights for the entire round."],
                    ["Radio Silence",           "All living players must deafen their discord until the end of the round. Players may not communicate in-game other than pinging"],
                    ["Equality of Outcome",     "Everyone must equip the same guns and armor this round."],
                    ["Social Distancing",       "Players must stay at least 10 meters apart at all times."],
                    ["I AM THE LAW",            "You may only buy the Judge, Sheriff, or Marshal."],
                    ["Doppelgänger",            "If there is an enemy on the other team with the same agent as you, you must ignore all other enemies until you have killed your doppelgänger."],
                    ["X-Ray Vision",            "You are only allowed to kill enemeies through walls."]]
                    
    player_strats = [["Clear Comms",            "Only {player} may speak."],
                     ["Blood Sacrifice",        "{player} must die (from your team's abilities, if possible) before anyone gets a kill."],
                     ["Shot Caller",            "You may only do things explicitly instructed to you by {player}."],
                     ["Permission Slip",        "Everyone must get {player}'s permission before reloading, swapping weapons, or using abilities."],
                     ["Protect the President",  "{player} may only use a classic. The team must stay near, and protect them. If they die, you cannot move."],
                     ["Gun Vendor",             "Only {player} may spend money on weapons for the team."],
                     ["(Almost) Powerless",     "Only {player} may use abilities."],
                     ["Dictatorship",           "The team must follow any order given by {player}."]]
    
    key_strats    = [["Sticky Keys",            "You must hold down the {key} key for the entire round."],
                     ["Broken Keys",            "You cannot use the {key} key."]]
        
    strat_list = []
    for name, desc in basic_strats:
        strat_list.append([name, desc, 0])
    for name, desc in player_strats:
        strat_list.append([name, desc, 1])
    for name, desc in key_strats:
        strat_list.append([name, desc, 2])
        
    def get_player(self):
        stat = self.get_stat()
        return choice(self.player_list).format(stat=stat)
    
    def get_stat(self):
        return choice(self.stat_list)
    
    def get_key(self):
        return choice(self.key_list)
    
    def choose(self):
        name, desc, typ = choice(self.strat_list)
        cap_bool = bool(desc[0] == "{")
        
        if typ == 0:
            return [name, desc]
        
        if typ == 1:
            player = self.get_player()
            if cap_bool:
                player = player.capitalize()
            return [name, desc.format(player=player)]
        
        if typ == 2:
            key = self.get_key()
            if cap_bool:
                key = key.capitalize()
            return [name, desc.format(key=key)]

    @commands.Cog.listener()
    async def on_ready(self):
        print("stratroulette.py loaded")
        
    @commands.command(help = 'Gives a random "Strat Roulette"')
    async def strat(self, ctx):
        '''Gives a random "Strat Roulette"'''
        name, desc = self.choose()
        await ctx.send(f"{name}: {desc}", tts=True)
        
async def setup(client):
    await client.add_cog(StratRoulette(client))
        