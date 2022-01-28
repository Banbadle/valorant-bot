import random

images = {"Astra": "https://static.wikia.nocookie.net/valorant/images/0/08/Astra_icon.png/",\
          "Pheonix": "https://static.wikia.nocookie.net/valorant/images/1/14/Phoenix_icon.png/",\
          "Killjoy": "https://static.wikia.nocookie.net/valorant/images/1/15/Killjoy_icon.png/",\
          "Skye": "https://static.wikia.nocookie.net/valorant/images/3/33/Skye_icon.png/",\
          "Jett": "https://static.wikia.nocookie.net/valorant/images/3/35/Jett_icon.png/",\
          "Sova": "https://static.wikia.nocookie.net/valorant/images/4/49/Sova_icon.png",\
          "Brimstone": "https://static.wikia.nocookie.net/valorant/images/4/4d/Brimstone_icon.png/",\
          "Breach": "https://static.wikia.nocookie.net/valorant/images/5/53/Breach_icon.png/",\
          "Viper": "https://static.wikia.nocookie.net/valorant/images/5/5f/Viper_icon.png",\
          "Sage": "https://static.wikia.nocookie.net/valorant/images/7/74/Sage_icon.png",\
          "Cypher": "https://static.wikia.nocookie.net/valorant/images/8/88/Cypher_icon.png",\
          "Raze": "https://static.wikia.nocookie.net/valorant/images/9/9c/Raze_icon.png",\
          "Omen": "https://static.wikia.nocookie.net/valorant/images/b/b0/Omen_icon.png",\
          "Reyna": "https://static.wikia.nocookie.net/valorant/images/b/b0/Reyna_icon.png",\
          "Yoru": "https://static.wikia.nocookie.net/valorant/images/d/d4/Yoru_icon.png/",\
          "KAYO": "https://static.wikia.nocookie.net/valorant/images/f/f0/KAYO_icon.png/",\
          "Chamber": "https://static.wikia.nocookie.net/valorant/images/0/09/Chamber_icon.png",\
          "Neon": "https://static.wikia.nocookie.net/valorant/images/d/d0/Neon_icon.png/"}
    
    
phrases = {"Astra": '"My people, are you ready?"',\
           "Pheonix": '"Come on, let\'s go"',\
           "Killjoy": '"You should run"',\
           "Skye": '"Time to hunt"',\
           "Jett": '"I hate to say it but, probably best to play as a team"',\
           "Sova": '"Wherever you run, I will find you"',\
           "Brimstone": '"You know what to do"',\
           "Breach": '"We doing this, or what?"',\
           "Viper": '"Come"',\
           "Sage": '"Your duty is not over"',\
           "Cypher": '"I know exactly where you are"',\
           "Raze": '"Too slow"',\
           "Omen": '"Make the right choice, even if it calls for sacrifice"',\
           "Reyna": '"The hunt begins"',\
           "Yoru": '"Anyone else?"',\
           "Chamber": '"This has gone on long enough I think."',\
           "Neon": '"Lets go. Worlds not saving itself."'}
    
agent_list = tuple(images)

map_list = ["Ascent", "Split", "Fracture", "Bind", "Breeze", "Icebox", "Haven"]
    
pair_list = tuple(name for name in images if name in phrases)

def get_author_pair(agentName=None):
    if agentName==None:
        agentName = random.choice(pair_list)
        
    text = phrases[agentName]
    icon = images[agentName]
    return [text, icon]
