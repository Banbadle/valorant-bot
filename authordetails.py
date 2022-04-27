import random

agent_details = {'Astra':       {'image': 'https://static.wikia.nocookie.net/valorant/images/0/08/Astra_icon.png/',     'phrase': '"My people, are you ready?"'},\
                 'Phoenix':     {'image': 'https://static.wikia.nocookie.net/valorant/images/1/14/Phoenix_icon.png/',   'phrase': '"Come on, let\'s go"'},\
                 'Killjoy':     {'image': 'https://static.wikia.nocookie.net/valorant/images/1/15/Killjoy_icon.png/',   'phrase': '"You should run"'},\
                 'Skye':        {'image': 'https://static.wikia.nocookie.net/valorant/images/3/33/Skye_icon.png/',      'phrase': '"Time to hunt"'},
                 'Jett':        {'image': 'https://static.wikia.nocookie.net/valorant/images/3/35/Jett_icon.png/',      'phrase': '"I hate to say it but, probably best to play as a team"'}, 
                 'Sova':        {'image': 'https://static.wikia.nocookie.net/valorant/images/4/49/Sova_icon.png',       'phrase': '"Wherever you run, I will find you"'}, 
                 'Brimstone':   {'image': 'https://static.wikia.nocookie.net/valorant/images/4/4d/Brimstone_icon.png/', 'phrase': '"You know what to do"'}, 
                 'Breach':      {'image': 'https://static.wikia.nocookie.net/valorant/images/5/53/Breach_icon.png/',    'phrase': '"We doing this, or what?"'}, 
                 'Viper':       {'image': 'https://static.wikia.nocookie.net/valorant/images/5/5f/Viper_icon.png',      'phrase': '"Come"'}, 
                 'Sage':        {'image': 'https://static.wikia.nocookie.net/valorant/images/7/74/Sage_icon.png',       'phrase': '"Your duty is not over"'}, 
                 'Cypher':      {'image': 'https://static.wikia.nocookie.net/valorant/images/8/88/Cypher_icon.png',     'phrase': '"I know exactly where you are"'}, 
                 'Raze':        {'image': 'https://static.wikia.nocookie.net/valorant/images/9/9c/Raze_icon.png',       'phrase': '"Too slow"'}, 
                 'Omen':        {'image': 'https://static.wikia.nocookie.net/valorant/images/b/b0/Omen_icon.png',       'phrase': '"Make the right choice, even if it calls for sacrifice"'}, 
                 'Reyna':       {'image': 'https://static.wikia.nocookie.net/valorant/images/b/b0/Reyna_icon.png',      'phrase': '"The hunt begins"'}, 
                 'Yoru':        {'image': 'https://static.wikia.nocookie.net/valorant/images/d/d4/Yoru_icon.png/',      'phrase': '"Anyone else?"'}, 
                 'KAY/O':       {'image': 'https://static.wikia.nocookie.net/valorant/images/f/f0/KAYO_icon.png/',      'phrase': '"Where the fuck are you?"'}, 
                 'Chamber':     {'image': 'https://static.wikia.nocookie.net/valorant/images/0/09/Chamber_icon.png',    'phrase': '"This has gone on long enough I think."'}, 
                 'Neon':        {'image': 'https://static.wikia.nocookie.net/valorant/images/d/d0/Neon_icon.png/',      'phrase': '"Lets go. World\'s not saving itself."'}}

map_list = ("Ascent", "Split", "Fracture", "Bind", "Breeze", "Icebox", "Haven")

def get_author_pair(agent=None):
    if agent==None:
        agent_name = random.choice(list(agent_details))
        
    phrase = agent_details[agent_name]["phrase"]
    image  = agent_details[agent_name]["image"]
    return [phrase, image]