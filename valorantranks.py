from bs4 import BeautifulSoup
import requests
from itertools import product

tiers = ("Unrated", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Imortal", "Radiant")

ranks = [tiers[0]] + ["".join(prod) for prod in product(tiers[1:-1], [" 1", " 2", " 3"])]
ranks.append(tiers[-1])
ranks = tuple(ranks)

def get_rank_num(rankText):
    try:
        return ranks.index(rankText)
    except:
        return None

def num_to_rank(num):
    return ranks[num]

rank_brackets = ((1,2,3,4,5,6,7,8,9), (7,8,9,10,11,12), (10,11,12,13,14,15), (13,14,15,16), (14,15,16,17), (15,16,17,18), (16,17,18,19,20,21), (21,22))  

rank_ranges = []
for rank_num in range(1, len(ranks)):
    mini = min(bracket[0] for bracket in rank_brackets if rank_num in bracket)
    maxi = max(bracket[-1] for bracket in rank_brackets if rank_num in bracket)+1
    rank_ranges.append((mini, maxi))

rank_ranges = tuple(rank_ranges)

def get_rank_range(num):
    return rank_ranges[num]

def get_player_rank(user_id):

    username, tag = usernametags[user_id]
    tracker = f"https://tracker.gg/valorant/profile/riot/{username}%23{tag}/overview?playlist=competitive"

    source = requests.get(tracker).text
    soup = BeautifulSoup(source, 'html.parser')
    rankSpan = soup.find("span", {"class":"valorant-highlighted-stat__value"})
    rank = rankSpan.text

    return rank

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

playertracker = {key: get_tracker_from_ids(*val) for key, val in usernametags.items()}
