import discord
from discord.ext import commands
from games.creditgame import CreditGame
from random import choice
import re

class Card:    
    suit_list = ['♠️', '♥️', '♦️', '♣️']
    rank_list = {"A": 11, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10}
    
    def __init__(self, suit=None, rank=None):
        self.suit = suit if suit != None else choice(self.suit_list)
        self.rank = rank if rank != None else choice(self.rank_list)
        
    def __str__(self):
        return self.rank + self.suit
    
    def __int__(self):
        return self.rank_list[self.rank]
    
    def __add__(self, other):
        return int(self) + int(other)

class Blackjack(CreditGame):
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("blackjack.py loaded")

    def __init__(self, client):
        self.client = client
        
        hand_string = r"Hand {}: (bet {}) value: {}"
        
        hand_regex = re.escape(hand_string)
        hand_regex = re.sub(r"\\{\\}", r"([0-9]+)", hand_regex)
        
        self.hand_string = hand_string
        self.hand_regex  = hand_regex
        
    def get_hand_values(self, string):
        regex = self.hand_regex
        match = re.search(regex, string)
        if match:
            bet = match.group(2)
            value = match.group(3)
            return bet, value
        return None, None
            
    def get_base_embeds(self, bet):
        # TITLE EMBED
        embed_color = 0xFF0000
        embed_top = discord.Embed(title="__Welcome to KAsYn/O Blackjack__", color=embed_color)
        embed_top.addfield(name="Initial Bet: {bet}", value=str(bet))
        
        # DEALER EMBED
        embed_dealer = discord.Embed(title="Dealer", color=embed_color)
        dealer_card = Card()
        embed_dealer.addfield(name="Hand:", value=str(dealer_card))
        
        # PLAYER EMBED
        embed_player = discord.Embed(title="You", color=embed_color)  
        
        player_card_1 = Card()
        player_card_2 = Card()
        
        title = self.hand_string
        value = player_card_1 + player_card_2
        title = title.format("1", bet, value)
        
        embed_dealer.addfield(name=title, value=f"{player_card_1}, {player_card_2}")

        return [embed_top, embed_dealer, embed_player]
    
    def get_state_from_msg(self, msg):
        pass
        
    @commands.command(help = "Starts a game of blackjack")
    def blackjack(self, ctx, bet):
        user = ctx.author
        game_embeds = self.get_base_embeds(5)
        user.send(embeds=game_embeds)
        
    def deal(self, message):
        new_card = Card()
        
async def setup(client):
    await client.add_cog(Blackjack(client))
