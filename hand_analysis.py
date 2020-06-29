import simplejson as json
import os
from decimal import Decimal
import matplotlib.pyplot as plt
import shutil
import handhistory as HH
import pandas as pd
import numpy as np


in_path = "C:/Users/Calum/AppData/Local/PokerStars.UK/HandHistory/dazzle0"
out_path = "E:/Poker/hand_data"
my_user = "dazzle0"



def player_winnings(hand, player):
    net = hand["players"][player]['winnings'] - hand["players"][player]['into_pot']
    return {"winnings": net}

def round_seen(hand, player):
    stats = {"total_hands": 1,
             "flops_seen": 0}
    for action in hand["pre_flop_action"]:
        if action["player"] == player and action["action"] == "folds":
            break
    else:
        stats["flops_seen"] = 1
    return stats


##list of functions, each of return 1 or more statistics about a given player
analytics = [round_seen, player_winnings]


##updates the player data dictionary accoring to the stats returned by and analytic
def update(player_data, new_stats):
    for stat_name, val in new_stats.items():
        try:
            player_data[stat_name] += val
        except:
            player_data[stat_name] = val
    return


update_only = False                 ##if true, script will only read new and updated files.



try:
    player_data = pd.read_csv("player_data.csv")
except:
    player_data = pd.DataFrame(columns = ["session", "player", "total_hands", "flops_seen", "winnings"])
    player_data.set_index('player')


try:
    with open("earnings.txt", "r") as f:
        earnings = json.loads(f.read())
except:
    earnings = {}
    

for file in os.listdir(in_path):
    
    f1 = os.path.join(in_path, file)
    f2 = os.path.join(out_path, file)
    
    if update_only and (not ( os.path.exists(f2) ) or os.path.getmtime(f1) > os.path.getmtime(f2)):           ##if file is new or updated
        
        player_data = player_data[player_data.session != f2] ## remove pre-existing entries relating to this session
        new_data = {}
        earnings[f2] = [0]
        shutil.copy(f1, f2)
        for hand in HH.Parse_hands(f2):
            for player in hand["players"]:

                if player not in new_data.keys():
                        new_data[player] = {"session": f2, "player": player}
                        
                for analytic in analytics:
                    update(new_data[player], analytic(hand,player))
                        
                    net = hand["players"][my_user]['winnings'] - hand["players"][my_user]['into_pot']
                    earnings[f2].append(net)

        player_data = player_data.append(pd.DataFrame(new_data.values()), ignore_index = True)



player_data.to_csv("player_data.csv")
with open("earnings.txt", "w") as f:
    f.write(json.dumps(earnings))



cum_earnings = [0]
for session in earnings.values():
    for net in session:
        cum_earnings.append(cum_earnings[-1] + net)
        

plt.plot(cum_earnings)
plt.show()        
                                        
