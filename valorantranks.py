from bs4 import BeautifulSoup
import requests
import random
from itertools import product
import lxml

tiers = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Imortal", "Radiant"]

ranks = ["".join(prod) for prod in product(tiers[0:-1], [" 1", " 2", " 3"])]
ranks.append(tiers[-1])
ranks = tuple(ranks)

def get_player_rank(trackerpage):

    source = requests.get(trackerpage).text
    soup = BeautifulSoup(source, 'html.parser')
    rankSpan = soup.find("span", {"class":"valorant-highlighted-stat__value"})
    rank = rankSpan.text
    
    return rank

def get_rank_num(rankText):
    return ranks.index(rankText)

def get_rank_icon(rankText):
    num = get_rank_num(rankText)+3
    return f"https://trackercdn.com/cdn/tracker.gg/valorant/icons/tiers/{num}.png"


# randRank = random.choice(ranks)

# print(randRank)
# print(get_rank_num(randRank))
# print(get_rank_icon(randRank))

# print(get_player_rank("https://tracker.gg/valorant/profile/riot/Banbadle%23EUW/overview"))

