from bs4 import BeautifulSoup
import requests
import random
from itertools import product
import lxml

tiers = ["Unrated", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Imortal", "Radiant"]

ranks = [tiers[0]] + ["".join(prod) for prod in product(tiers[1:-1], [" 1", " 2", " 3"])]
ranks.append(tiers[-1])
ranks = tuple(ranks)

def get_player_rank(user_id):
    
    username, tag = usernametags[user_id]
    tracker = f"https://tracker.gg/valorant/profile/riot/{username}%23{tag}/overview?playlist=competitive" 

    source = requests.get(tracker).text
    soup = BeautifulSoup(source, 'html.parser')
    rankSpan = soup.find("span", {"class":"valorant-highlighted-stat__value"})
    rank = rankSpan.text
    
    return rank

def get_rank_num(rankText):
    try:
        return ranks.index(rankText)
    except:
        return None

def num_to_rank(num):
    return ranks[num]

def get_rank_icon(rankText):
    num = get_rank_num(rankText)+3
    return f"https://trackercdn.com/cdn/tracker.gg/valorant/icons/tiers/{num}.png"


usernametags = {188315898698924033: ["McSalterson","EUW"],\
                273795229264642048: ["Banbadle","EUW"],\
                202046790114082816: ["TheImperialGuard","EUW"],\
                358330529675739187: ["TicTacNicNac","EUW"],\
                122818014189060096: ["ThePiMan","ligma"],\
                115392592832757761: ["TorchyTwo","ligma"],\
                552247766659760141: ["seethelanes","MBB"],\
                295114226467340289: ["Lusington", "1234"],\
                201437325257998336: ["uWuWu", "uWuWu"],\
                231898748316286976: ["calpicco", "EUW"],\
                140172943396306944: ["motornaik", "EUW"]}
                                     

def get_tracker_from_ids(username, tag):
    return f"https://tracker.gg/valorant/profile/riot/{username}%23{tag}/overview?playlist=competitive" 


# def get_recent_win_loss(user_id):
#     def get_wins_losses_int(soup, winorloss):
#         text = soup.find("span", {"class": winorloss}).text
#         numstr = text[0:-1]
#         return numstr

#     username, tag = usernametags[user_id]
#     tracker = f"https://tracker.gg/valorant/profile/riot/{username}%23{tag}/matches?playlist=competitive" 

#     source = requests.get(tracker).text
#     soup = BeautifulSoup(source, 'html.parser')
#     wins = get_wins_losses_int(soup, "wins")
#     losses = get_wins_losses_int(soup, "losses")
    
#     return [wins, losses]


playertracker = {key: get_tracker_from_ids(*val) for key, val in usernametags.items()}
