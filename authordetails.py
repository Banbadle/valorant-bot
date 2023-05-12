import random

agent_details = {'Astra':       {'image': 'https://static.wikia.nocookie.net/valorant/images/0/08/Astra_icon.png/',
                                 'phrase': '"My people, are you ready?"',
                                 'role': "Controller"},\
                 'Phoenix':     {'image': 'https://static.wikia.nocookie.net/valorant/images/1/14/Phoenix_icon.png/',   
                                 'phrase': '"Come on, let\'s go"',
                                 'role': "Duelist"},\
                 'Killjoy':     {'image': 'https://static.wikia.nocookie.net/valorant/images/1/15/Killjoy_icon.png/',   
                                 'phrase': '"You should run"',
                                 'role': "Sentinel"},\
                 'Skye':        {'image': 'https://static.wikia.nocookie.net/valorant/images/3/33/Skye_icon.png/',      
                                 'phrase': '"Time to hunt"',
                                 'role': "Initiator"},\
                 'Jett':        {'image': 'https://static.wikia.nocookie.net/valorant/images/3/35/Jett_icon.png/',      
                                 'phrase': '"I hate to say it but, probably best to play as a team"', 
                                 'role': "Duelist"},\
                 'Sova':        {'image': 'https://static.wikia.nocookie.net/valorant/images/4/49/Sova_icon.png',       
                                 'phrase': '"Wherever you run, I will find you"', 
                                 'role': "Initiator"},\
                 'Brimstone':   {'image': 'https://static.wikia.nocookie.net/valorant/images/4/4d/Brimstone_icon.png/', 
                                 'phrase': '"You know what to do"', 
                                 'role': "Controller"},\
                 'Breach':      {'image': 'https://static.wikia.nocookie.net/valorant/images/5/53/Breach_icon.png/',    
                                 'phrase': '"We doing this, or what?"',
                                 'role': "Initiator"},\
                 'Viper':       {'image': 'https://static.wikia.nocookie.net/valorant/images/5/5f/Viper_icon.png',      
                                 'phrase': '"Come"', 
                                 'role': "Controller"},\
                 'Sage':        {'image': 'https://static.wikia.nocookie.net/valorant/images/7/74/Sage_icon.png',       
                                 'phrase': '"Your duty is not over"', 
                                 'role': "Sentinel"},\
                 'Cypher':      {'image': 'https://static.wikia.nocookie.net/valorant/images/8/88/Cypher_icon.png',     
                                 'phrase': '"I know exactly where you are"', 
                                 'role': "Sentinel"},\
                 'Raze':        {'image': 'https://static.wikia.nocookie.net/valorant/images/9/9c/Raze_icon.png',       
                                 'phrase': '"Too slow"', 
                                 'role': "Duelist"},\
                 'Omen':        {'image': 'https://static.wikia.nocookie.net/valorant/images/b/b0/Omen_icon.png',       
                                 'phrase': '"Make the right choice, even if it calls for sacrifice"', 
                                 'role': "Controller"},\
                 'Reyna':       {'image': 'https://static.wikia.nocookie.net/valorant/images/b/b0/Reyna_icon.png',      
                                 'phrase': '"The hunt begins"', 
                                 'role': "Duelist"},\
                 'Yoru':        {'image': 'https://static.wikia.nocookie.net/valorant/images/d/d4/Yoru_icon.png/',      
                                 'phrase': '"Anyone else?"', 
                                 'role': "Duelist"},\
                 'KAY/O':       {'image': 'https://static.wikia.nocookie.net/valorant/images/f/f0/KAYO_icon.png/',      
                                 'phrase': '"Where the fuck are you?"',
                                 'role': "Initiator"},\
                 'Chamber':     {'image': 'https://static.wikia.nocookie.net/valorant/images/0/09/Chamber_icon.png',    
                                 'phrase': '"This has gone on long enough I think."', 
                                 'role': "Sentinel"},\
                 'Neon':        {'image': 'https://static.wikia.nocookie.net/valorant/images/d/d0/Neon_icon.png/',      
                                 'phrase': '"Lets go. World\'s not saving itself."',
                                 'role': "Duelist"},\
                 'Fade':        {'image': 'https://static.wikia.nocookie.net/valorant/images/a/a6/Fade_icon.png/',      
                                 'phrase': '"Another mission? Good. Anything to keep me awake."',
                                 'role': "Initiator"},\
                 'Harbor':      {'image': 'https://static.wikia.nocookie.net/valorant/images/f/f3/Harbor_icon.png/',    
                                 'phrase': '"I suggest you move."',
                                 'role': "Controller"},\
                 'Gekko':       {'image': 'https://static.wikia.nocookie.net/valorant/images/6/66/Gekko_icon.png/',     
                                 'phrase': '"Run, little man."',
                                 'role': "Controller"}}
    
agent_roles = {"Controller":    {'image': 'https://static.wikia.nocookie.net/valorant/images/0/04/ControllerClassSymbol.png/',
                                 'colour': 0x00bc00},
               "Duelist":       {'image': 'https://static.wikia.nocookie.net/valorant/images/f/fd/DuelistClassSymbol.png/',
                                 'colour': 0xf00000},
               "Initiator":     {'image': 'https://static.wikia.nocookie.net/valorant/images/7/77/InitiatorClassSymbol.png/',
                                 'colour': 0xffff00},
               "Sentinel":      {'image': 'https://static.wikia.nocookie.net/valorant/images/4/43/SentinelClassSymbol.png/',
                                 'colour': 0x00ffff}}

map_list = ("Ascent", "Split", "Fracture", "Bind", "Breeze", "Icebox", "Haven", "Pearl", "Lotus")

def get_author_pair(agent=None):
    if agent==None:
        agent_name = random.choice(list(agent_details))
        
    phrase = agent_details[agent_name]["phrase"]
    image  = agent_details[agent_name]["image"]
    return [phrase, image]