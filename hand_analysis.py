import simplejson as json
import os
from decimal import Decimal
import matplotlib.pyplot as plt
import shutil
import handhistory as HH
import pandas as pd
import numpy as np


in_path = "" ## directory for hand history, eg C:/Users/user/AppData/Local/PokerStars.UK/HandHistory/user_name
out_path = "E:/Poker/hand_data"
my_name = ""

betting_rounds = ["pre_flop", "flop", "turn", "river"]

def player_winnings(hand, player):
    net = hand["players"][player]['winnings'] - hand["players"][player]['into_pot']
    return {"winnings": net}

def round_seen(hand, player):
    stat_names = ["total_hands",
             "flops_seen",
             "turns_seen",
             "rivers_seen",
             "showdowns_seen"]
    round_reached = 0
    for betting_round in hand["betting_rounds"].values():
        for action in betting_round:
            if action["player"] == player and action["action"] in ["folds",'collects_pot']:
                break
        else:
            round_reached += 1
            continue
        break

    stats = {stat_names[i]: (round_reached >= i) for i in range(0,5)}
    
    return stats

def _3bets(hand, player):
    stats = {"3bet_opertunitys": 0,
             "3bets_made": 0}
    for betting_round in hand["betting_rounds"].values():
        for idx, action in enumerate(betting_round):
            if action["action"] == "raises":
                betting_round = betting_round[idx+1:]
                break
        for action in betting_round:
            if action["player"] == player and action["action"] not in ['collects_pot', 'bet_returned']:
                stats["3bet_opertunitys"] += 1
                if action["action"] == "raises":
                    stats["3bets_made"] += 1
    return stats

##list of functions, each of return 1 or more statistics about a given player
analytics = [round_seen, player_winnings, _3bets]


##updates the player data dictionary accoring to the stats returned by and analytic
def update(player_data, new_stats):
    for stat_name, val in new_stats.items():
        try:
            player_data[stat_name] += val
        except:
            player_data[stat_name] = val
    return


update_only = False                 ##if true, script will only read new and updated files.


if update_only:
    try:
        player_data = pd.read_csv("player_data.csv")
    except:
        player_data = pd.DataFrame(columns = ["session", "player"])
else:
    player_data = pd.DataFrame(columns = ["session", "player"])

try:
    with open("earnings.txt", "r") as f:
        earnings = json.loads(f.read())
except:
    earnings = {}
    

for file in os.listdir(in_path):
    
    f1 = os.path.join(in_path, file)
    f2 = os.path.join(out_path, file)
    
    if not update_only or (not ( os.path.exists(f2) ) or os.path.getmtime(f1) > os.path.getmtime(f2)):           ##if file is new or updated
        
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
                        
                    net = hand["players"][my_name]['winnings'] - hand["players"][my_name]['into_pot']
                    earnings[f2].append(net)

        player_data = player_data.append(pd.DataFrame(new_data.values()), ignore_index = True, sort = False)



player_data.to_csv("player_data.csv")
with open("earnings.txt", "w") as f:
    f.write(json.dumps(earnings))



cum_earnings = [0]
for session in earnings.values():
    for net in session:
        cum_earnings.append(cum_earnings[-1] + net)
        

plt.plot(cum_earnings)
plt.show()        
                                        
