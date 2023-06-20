import discord
from discord.ext import commands
from games.creditgame import CreditGame
from discord.ui import Button, View
from discord import ButtonStyle
from random import choice
import re

class Card:    
    suit_list = ['♠️', '♥️', '♦️', '♣️']
    rank_list = {":regional_indicator_a:": 11,
                 ":two:": 2,
                 ":three:": 3,
                 ":four:": 4,
                 ":five:": 5,
                 ":six:": 6,
                 ":seven:": 7,
                 ":eight:": 8,
                 ":nine:": 9,
                 ":keycap_ten:": 10,
                 ":regional_indicator_j:": 10,
                 ":regional_indicator_q:": 10,
                 ":regional_indicator_k:": 10}

    def __init__(self, rank=None, suit=None):
        self.suit = suit if suit != None else choice(self.suit_list)
        self.rank = rank if rank != None else choice(list(self.rank_list.keys()))
        
    def __str__(self):
        return self.rank  # + self.suit

    def __int__(self):
        return self.rank_list[self.rank]

    def __add__(self, other):
        return int(self) + int(other)

class Blackjack(CreditGame):
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.blackjack_view = self.BlackjackView(self)
        self.client.add_view(self.blackjack_view)
        print("blackjack.py loaded")

    def __init__(self, client):
        self.client = client

        hand_string = r"Hand: {}"

        hand_regex = re.escape(hand_string)
        hand_regex = re.sub(r"\\{\\}", r"([0-9]+)", hand_regex)

        self.hand_string = hand_string
        self.hand_regex = hand_regex

    def get_hand_values(self, string):
        regex = self.hand_regex
        match = re.search(regex, string)
        if match:
            value = match.group(2)
            return value
        return None, None

    def get_base_embeds(self, bet):
        # TITLE EMBED
        new_embed = discord.Embed(title="__Welcome to KAsYn/O Blackjack__", color=0xFF0000)
        new_embed.add_field(name=f"Initial Bet: {bet}", value="Current hand: 1", inline=False)
        
        # PLAYER EMBED        
        player_card_1 = Card()
        player_card_2 = Card()
        player_score = player_card_1 + player_card_2
        
        player_value = f"{player_card_1}, {player_card_2}" + "\n" + f"Value: {player_score}"
        new_embed.add_field(name="**Hand 1:**", value=player_value, inline=True)   
        
        # DEALER EMBED
        dealer_card = Card()
        dealer_value = str(dealer_card) + "\n" + f"Value: {int(dealer_card)}"
        new_embed.add_field(name="**Dealer's Hand**", value=dealer_value, inline=True)

        return new_embed
    
    def get_state_from_msg(self, msg):
        pass
        
    class BlackjackView(View):
        def __init__(self, base_cog):
            self.base_cog = base_cog
            super().__init__(timeout=None)
            self._make_buttons()

        def _make_buttons(self):
            base_cog = self.base_cog

            button_funcs = [base_cog.hit, base_cog.stand,
                            base_cog.double, base_cog.split]
            button_labels = ["Hit", "Stand", "Double", "Split"]
            button_styles = [ButtonStyle.green, ButtonStyle.red,
                             ButtonStyle.blurple, ButtonStyle.grey]

            for func, label, style in zip(button_funcs, button_labels, button_styles):
                new_button = base_cog.BlackjackButton(base_cog, func, label, style)
                self.add_item(new_button)

    class BlackjackButton(Button):

        def __init__(self, base_cog, button_func, button_label, button_style):
            self.base_cog = base_cog
            self.button_func = button_func

            super().__init__(label=button_label, style=button_style, custom_id=button_label)

        async def callback(self, interaction):
            msg = interaction.message
            user = interaction.user
            await self.button_func(msg)

    @commands.command(help="Starts a game of blackjack")
    async def blackjack(self, ctx, bet):
        user = ctx.author
        game_embeds = self.get_base_embeds(bet)
        await user.send(embed=game_embeds, view=self.blackjack_view)

    def deal(self, message):
        new_card = Card()


async def setup(client):
    await client.add_cog(Blackjack(client))
