from discord.ext import commands

class CreditGame(commands.Cog):

    def __init__(self, client):
        self.client = client
        
    def can_start(self, user):
        user_credits = self.client.db.get_social_credit(user)
        return user_credits > 0
        
    def start_game(self, user):
        if not self.can_start(user):
            pass
        else:
            pass
        
    def buyin(self, user, value):
        self.make_credit_change(self, user, value, "Bet")
    
    def payout(self, user, value):
        self.make_credit_change(self, user, value, "Payout")
        
    def make_credit_change(self, user, value, event_name):
        game_name = self.__class__.__name__
        payout_str = f"{event_name} ({game_name})"
            
        self.client.db.record_credit_change(user, 
                                            event_name = payout_str, 
                                            change_value = value,
                                            cooldown=0, 
                                            vote_msg_id=None,
                                            cause_user=user, 
                                            processed=1)
        
        self.client.db.add_social_credit(user, value)

