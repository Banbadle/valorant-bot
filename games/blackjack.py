import discord
from discord.ext import commands
from games.creditgame import CreditGame
from discord.ui import Button, View
from discord import ButtonStyle, Interaction
from random import choice
import re

class Card:    
    #suit_list = ['♠️', '♥️', '♦️', '♣️']
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
        #self.suit = suit if suit != None else choice(self.suit_list)
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
    def __init__(self, cards, bet=None):
        self.cards = []
        self.value = 0
        self.is_soft = False
        self.bet = bet
        for c in cards:
            self.add(c)
            
    def dealer_play(self):
        while self.value < 17:
            self.hit()
            
    def hit(self):
        new_card = Card()
        self.add(new_card)
        
    def add(self, card):
        if not isinstance(card, Card):
            raise TypeError(f"object of type 'Card' expected, {type(card)} was given")
        
        self.cards.append(card)
        self.value += int(card)
        
        if self.value <= 11 and int(card) == 1:
            self.value += 10
            self.is_soft = True
            
        elif self.value > 21 and self.is_soft:
            self.value -= 10
            self.is_soft = False 
            
    def is_blackjack(self):
        return len(self) == 2 and int(self) == 21
    
    def is_bust(self):
        return int(self) > 21

    def __str__(self):
        cards = ", ".join([str(c) for c in self.cards])
        value = "Value: " + "Soft "*self.is_soft + f"{self.value}"
        if self.is_blackjack():
            value = "Value: Blackjack"
        hand_string = cards + "\n" + value
        return hand_string
    
    def __int__(self):
        return self.value
    
    def __len__(self):
        return len(self.cards)
    
    def __getitem__(self, index):
        return self.cards[index]
    
    def pop(self):
        popped_card = self.cards.pop()
        self.value -= int(popped_card)
        return popped_card
    
    @staticmethod
    def from_field(field):
        bet = re.search(r"\(Bet (\d+)\)", field.name)
        if bet:
            bet = int(bet.group(1))
        cards_string = field.value.split("\n")[0]
        card_str_list = cards_string.split(", ")
        card_list = list([Card(rank=c) for c in card_str_list])
        return Hand(card_list, bet=bet)
        
class BlackjackState:
    def __init__(self, player_hands, dealer_hand, hand_num=1):
        self.hand_num = int(hand_num)
        self.player_hands = player_hands
        self.dealer_hand = dealer_hand
    
    def current_hand(self):
        if len(self.player_hands) < self.hand_num:
            return None
        return self.player_hands[self.hand_num-1]

    def is_finished(self):
        return self.current_hand() == None
    
    def to_embed(self):
        new_embed = discord.Embed(
            title="__Welcome to KAsYn/O Blackjack__", 
            color=0xFF0000)
        
        # SUMMARY FIELD
        total_bet = sum(h.bet for h in self.player_hands)
        new_embed.add_field(
            name=f"Total Bet: {total_bet}", 
            value=f"Current hand: {self.hand_num}" * (not self.is_finished()), 
            inline=False)

        # PLAYER FIELDS
        for i in range(0, len(self.player_hands)):
            player_hand = self.player_hands[i]
            bet = player_hand.bet
            
            base_str = f"**Hand {i+1}:**"
            bet_str = f" (Bet {bet})" * (bet != None)
            curr_str = " :point_left:" * (i == self.hand_num-1)
            
            win_str = ""
            if self.is_finished():
                if self.payouts[i] == player_hand.bet:
                    win_str = f":yellow_square: (Push {self.payouts[i]})"   # Push
                elif self.payouts[i] > 0:
                    win_str = f":white_check_mark: (Win {self.payouts[i]})" # Win
                else:
                    win_str = ":x: (Lose)"                                  # Lose
            
            new_embed.add_field(
                name= base_str + bet_str + curr_str, 
                value=str(player_hand) + "\n" + win_str,
                inline=(True if i == 0 else False))

        # DEALER FIELD
        dealer_hand = self.dealer_hand
        new_embed.insert_field_at(
            index=2, 
            name="**Dealer's Hand**", 
            value=str(dealer_hand), 
            inline=True)

        return new_embed
    
    @staticmethod
    def from_embed(embed):
        fields = embed.fields
        bet = re.search(r"Total Bet: (\d+)", fields[0].name)
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
            
        return BlackjackState(player_hands, dealer_hand, hand_num)
    
    def add(self, card):
        if not isinstance(card, Card):
            raise TypeError(f"object of type 'Card' expected, {type(card)} was given")
        
        self.current_hand().add(card)
    
    def hit(self):
        self.current_hand().hit()
        
    def stand(self):
        self.hand_num += 1
        
    def double(self):
        hand = self.current_hand()
        has_cards = len(hand) == 2
        if not has_cards:
            return "You may only double a hand when it has exactly 2 cards"
        self.hit()
        hand.bet *= 2
        self.stand()
    
    def split(self):
        hand = self.current_hand()
        has_cards = len(hand) == 2 and (int(hand[0]) == int(hand[1]))
        if not has_cards:
            return "You may only split when you have 2 cards of the same value"
        
        # CREDIT CHECK
        
        card2 = hand.pop()
        hand.hit()
        
        new_hand = Hand([card2], bet=hand.bet)
        new_hand.hit()
        self.player_hands.append(new_hand)
    
    def update(self):
        while self.current_hand() and self.current_hand().value >= 21:
            self.hand_num += 1
        
        if self.current_hand() == None:
            self.finish()
            
    def finish(self):
        self.dealer_hand.dealer_play()
    
    def action(self, string):
        out = None
        if   string == "Hit": out = self.hit()
        elif string == "Stand": out = self.stand()
        elif string == "Double": out = self.double()
        elif string == "Split": out = self.split()
        
        if out: 
            return out
        
        self.update()
            
class Blackjack(CreditGame):

    @commands.Cog.listener()
    async def on_ready(self):
        self.blackjack_view = self.BlackjackView(self)
        self.client.add_view(self.blackjack_view)
        print("blackjack.py loaded")

    def __init__(self, client):
        self.client = client
        
    def make_credit_change(self, user, num, reason, msg_id):
        event_name = f"{reason} (Blackjack)"
        self.client.db.record_credit_change(
            user, 
            event_name, 
            change_value=num,
            cooldown=0, 
            vote_msg_id=msg_id,
            cause_user=user, 
            processed=1)

        self.client.db.add_social_credit(user, num)

    class BlackjackView(View):
        def __init__(self, base_cog):
            self.base_cog = base_cog
            super().__init__(timeout=None)
            self._make_buttons()

        def _make_buttons(self):
            base_cog = self.base_cog

            button_labels = ["Hit", 
                             "Stand", 
                             "Double", 
                             "Split"]
            button_styles = [ButtonStyle.green, 
                             ButtonStyle.red, 
                             ButtonStyle.blurple, 
                             ButtonStyle.grey]

            for label, style in zip(button_labels, button_styles):
                new_button = base_cog.BlackjackButton(base_cog, label, style)
                self.add_item(new_button)

    class BlackjackButton(Button):

        def __init__(self, base_cog, button_label, button_style):
            self.base_cog = base_cog

            super().__init__(label=button_label, style=button_style, custom_id=button_label)

        async def callback(self, interaction: Interaction):
            msg = interaction.message
            embed = msg.embeds[0]
                
            gamestate = BlackjackState.from_embed(embed)
            
            user = interaction.user
            error_msg = None
            bet = gamestate.current_hand().bet
            if self.costs:
                error_msg = self.base_cog.check_credits(user, bet)
            
            if error_msg == None:
                error_msg = gamestate.action(self.label)

            embed_list = [gamestate.to_embed()]
            if error_msg != None:
                error_embed = discord.Embed(title=error_msg, color=0xFF0000)
                embed_list.append(error_embed)
                
            if gamestate.is_finished():
                await interaction.response.edit_message(embeds=embed_list, view=None)
    def check_credits(self, user, cost):
        creds = self.client.db.get_social_credit(user)
        if creds < cost:
            return "You do not have enough Social Credit to do this"
        
            else:
                await interaction.response.edit_message(embeds=embed_list)

    @commands.command(help="Starts a game of blackjack")
    async def blackjack(self, ctx, bet):
        user = ctx.author
        try:
            bet = int(bet)
        except:
            await user.send("The bet amount must be a number")
            return
        if bet <= 0:
            await user.send("You must bet a positive amount")
            return
        if bet > 10:
            await user.send("Your bet must be 10 or less")
            return
        creds_msg = self.check_credits(user, bet)
        if creds_msg:
            await user.send(creds_msg)
            return
            
        player_hand = Hand([Card(), Card()], bet=int(bet))
        dealer_hand = Hand([Card()])
        
        gamestate = BlackjackState([player_hand], dealer_hand)
        gamestate.update()
        game_embed = gamestate.to_embed()
        if gamestate.is_finished():
            await user.send(embed=game_embed)
        else:
            await user.send(embed=game_embed, view=self.blackjack_view)

async def setup(client):
    await client.add_cog(Blackjack(client))
