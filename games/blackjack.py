import discord
from discord.ext import commands
from games.creditgame import CreditGame
from discord.ui import Button, View
from discord import ButtonStyle
from random import choice
import re

class Card:    
    suit_list = ['♠️', '♥️', '♦️', '♣️']
    rank_list = {":regional_indicator_a:": 1,
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
        if isinstance(other, Card):
            return int(self) + int(other)
        return NotImplemented
    
class Hand:
    def __init__(self, cards):
        self.cards = []
        self.value = 0
        self.is_soft = False
        for c in cards:
            self + c
        
    def __add__(self, card):
        if not isinstance(card, Card):
            return NotImplemented
        
        self.cards.append(card)
        self.value += int(card)
        
        if self.value <= 11 and int(card) == 1:
            self.value += 10
            self.is_soft = True
            
        elif self.value > 21 and self.is_soft:
            self.value -= 10
            self.is_soft = False 
            
    def __radd__(self, card):
        return self.__add__(card)

    def __str__(self):
        cards = ", ".join([str(c) for c in self.cards])
        value = f"Value: " + "Soft "*self.is_soft + f"{self.value}"
        hand_string = cards + "\n" + value
        return hand_string
    
    def __int__(self):
        return self.value
    
    def from_field(self, field):
        cards_string = field.value.split("\n")[0]
        card_str_list = cards_string.split(", ")
        card_list = list([Card(rank=c) for c in card_str_list])
        return Hand(card_list)
        
class BlackjackState:
    def __init__(self, bet, hand_num, player_hands, dealer_hand):
        self.bet = bet
        self.hand_num = hand_num
        self.player_hands = player_hands
        self.dealer_hand = dealer_hand
    
    def current_hand(self):
        return self.player_hands[self.hand_num-1]
    
    def to_embed(self):
        new_embed = discord.Embed(
            title="__Welcome to KAsYn/O Blackjack__", 
            color=0xFF0000)
        
        # SUMMARY FIELD
        new_embed.add_field(
            name=f"Initial Bet: {self.bet}", 
            value=f"Current hand: {self.hand_num}", 
            inline=False)

        # PLAYER FIELDS
        for i in range(0, len(self.player_hands)):
            player_hand = self.player_hands[i]
            new_embed.add_field(
                name=f"**Hand {i+1}:**", 
                value=str(player_hand), 
                inline=(True if i == 0 else False))

        # DEALER FIELD
        dealer_hand = self.dealer_hand
        new_embed.insert_field_at(
            index=2, 
            name="**Dealer's Hand**", 
            value=str(dealer_hand), 
            inline=True)

        return new_embed
    
    def from_embed(self, embed):
        fields = embed.fields
        bet = re.search(r"Initial Bet: (\d+)", fields[0].name)
        bet = bet.group(1)
        hand_num = re.search(r"Current hand: (\d+)", fields[0].value)
        hand_num = hand_num.group(1)
        
        hand_num = hand_num
        player_hands = []
        for i in range(1, len(fields)):
            field = fields[i]
            new_hand = Hand.from_field(field)
            
            if i == 2:
                dealer_hand = new_hand
                continue
            player_hands.append(new_hand)
            
        return BlackjackState(bet, hand_num, player_hands, dealer_hand)
            
class Blackjack(CreditGame):

    @commands.Cog.listener()
    async def on_ready(self):
        self.blackjack_view = self.BlackjackView(self)
        self.client.add_view(self.blackjack_view)
        print("blackjack.py loaded")

    def __init__(self, client):
        self.client = client

    async def hit(self, message):
        new_card = Card()
        pass

    async def stand(self, message):
        self.get_state_from_msg(message)

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
    async def double(self, message):
        self.hit(message)
        self.stand(message)
        pass  # DOUBLE BET

        return new_embed
    
    async def split(self, message):
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
