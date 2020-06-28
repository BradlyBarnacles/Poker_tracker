import simplejson as json
import os
from decimal import Decimal
import matplotlib.pyplot as plt
import shutil
import handhistory as HH

in_path = "C:/Users/Calum/AppData/Local/PokerStars.UK/HandHistory/dazzle0"
out_path = "E:/Poker/hand_data"


def profit():
    total = [0]
    for file in os.listdir(path):
        with open(os.path.join(path, file), "r", encoding='utf-8-sig') as f:
            hands = ijson.items(f, 'item')
            chips = Decimal(2.00)
            for hand in hands:
                net = hand["players"]['dazzle0']['winnings'] - hand["players"]['dazzle0']['into_pot']
                if chips != hand["players"]['dazzle0']["chip_stack"]:
                    print(hand["hand_number"], hand["time"])
                total.append(total[-1]+ change)
                chips += change

    plt.plot(total)
    plt.show()

    print(total[-1])
        

    
with open("player_data.txt", "r") as f:
    player_data = json.loads(f.read())
with open("earnings.txt", "r") as f:
    earnings = json.loads(f.read())
    
for file in os.listdir(in_path):
    f1 = os.path.join(in_path, file)
    f2 = os.path.join(out_path, file)
    if not ( os.path.exists(f2) ) or os.path.getmtime(f1) > os.path.getmtime(f2):
        player_data[f2] = {}
        earnings[f2] = [0]
        shutil.copy(f1, f2)
        for hand in HH.Parse_hands(f2):
            for player in hand["players"]:
                if player in player_data[f2].keys():
                    player_data[f2][player]["hands"] += 1
                else:
                    player_data[f2][player] = {"hands": 1, "flops_seen": 0, "winnings": 0}
                    
                net = hand["players"][player]['winnings'] - hand["players"][player]['into_pot']
                if player == "dazzle0":
                    earnings[f2].append(net)
                player_data[f2][player]["winnings"] += net
                    
                for action in hand["pre_flop_action"]:
                    if action["player"] == player and action["action"] == "folds":
                        break
                else:
                    player_data[f2][player]["flops_seen"] += 1

    

with open("player_data.txt", "w") as f:
    f.write(json.dumps(player_data))
with open("earnings.txt", "w") as f:
    f.write(json.dumps(earnings))

totals = {}
for file, session in player_data.items():
    for player, stats in session.items():
        try:
            for statistic, val in stats.items():
                totals[player][statistic] += val
        except:
            totals[player] = stats

cum_earnings = [0]
for session in earnings.values():
    for net in session:
        cum_earnings.append(cum_earnings[-1] + net)
        

plt.plot(cum_earnings)
plt.show()        
                                        

#x,y = zip(*players.values())
#plt.scatter(x, y)
#plt.show()
