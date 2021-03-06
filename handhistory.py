import os
import re
import simplejson as json
from decimal import Decimal


def Parse_bet(line):
    match = re.match(bet_pattern, line)
    if match == None:
        if re.match(return_pattern, line) != None:
            match = re.match(return_pattern, line)
            action = {'player': match.group(2),
                      'action': 'bet_returned',
                      'amount': Decimal(match.group(1))}
        else:
            action = None
            
    elif match.group(2) == 'folds':
        action = {"player": match.group(1),
                  "action": "folds"}
    elif match.group(2) == 'checks':
        action = {"player": match.group(1),
                  "action": 'checks'}
    elif match.group(2) == 'bets':
        sub_match = re.match(' \$(\d*(?:\.\d\d)?)(?: and is all-in)?', match.group(3)) 
        action = {"player": match.group(1),
                  "action": "bets",
                  "amount": Decimal(sub_match.group(1))}
    elif match.group(2) == 'calls':
        sub_match = re.match(' \$(\d*(?:\.\d\d)?)(?: and is all-in)?', match.group(3)) 
        action = {"player": match.group(1),
                  "action": "calls",
                  "amount": Decimal(sub_match.group(1))}
    elif match.group(2) == 'raises':
        sub_match = re.match(' \$(\d*(?:\.\d\d)?) to \$(\d*(?:\.\d\d)?)(?: and is all-in)?', match.group(3)) 
        action = {"player": match.group(1),
                  "action": "raises",
                  "amount": Decimal(sub_match.group(2)),
                  "raised_by": Decimal(sub_match.group(1))}
    return action

def Parse_betting_round(file,contributions, players):
    line = file.readline()
    actions = []
    while re.match(limit_pattern, line) == None:
        action = Parse_bet(line)
        if action:
            actions.append(action)
            if action["action"] in ["bets", "calls"]:
                contributions[action["player"]] += action["amount"]
            elif action["action"] == "raises":
                contributions[action["player"]] = action["amount"]
            elif action["action"] == 'bet_returned':
                contributions[action["player"]] += -action["amount"]
            
        line = file.readline()
        if re.match(collect_pot_pattern, line) != None:
            match = re.match(collect_pot_pattern, line)
            actions.append({'player': match.group(1),
                            'action': 'collects_pot',
                            'amount': Decimal(match.group(2))})
            while '*** SUMMARY ***' not in line:
                line = file.readline()
            return actions, True
    return actions, False

def Parse_hands(path):
    with open(path, "r", encoding='utf-8-sig') as file:
        while True:
            hand = {} ##dictionary for all data about hand


            ##read 2 header lines
            match = re.match(header_pattern1 ,file.readline())
            if match == None:
                break
            hand['hand_number'] = match.group(1)
            hand['blinds'] = match.group(2)
            hand['date'] = match.group(3)
            hand['time'] = match.group(4)
            
            match = re.match(header_pattern2 ,file.readline())
            hand['table_name'] = match.group(1)
            hand['table_max_size'] = match.group(2)
            hand['button_pos'] = match.group(3)
            

            line = file.readline()
            hand["players"] = {}
            contributions = {}
            while re.match(seat_pattern, line) != None:
                match = re.match(seat_pattern, line)
                hand["players"][match.group(2)] = {"seat_num": match.group(1),
                                                   "chip_stack": Decimal(match.group(3)),
                                                   "into_pot": 0,
                                                   "winnings": 0}
                contributions[match.group(2)] = 0

                line = file.readline()
            hand["blinds_posted"] = []
            
            while line != '*** HOLE CARDS ***\n':
                match = re.match(blinds_pattern, line)
                if match != None:
                    hand["blinds_posted"].append({"player": match.group(1),
                                          "blind_type": match.group(2),
                                          "blind_size": Decimal(match.group(3))})
                    contributions[match.group(1)] += Decimal(match.group(3))
                line = file.readline()
            hand["my_cards"] = re.match(delt_pattern, file.readline()).group(1)
            hand["betting_rounds"] = {}
            

            for betting_round in betting_rounds:
                hand["betting_rounds"][betting_round], Done  = Parse_betting_round(file, contributions, hand["players"])
                for player, amount in contributions.items():
                    hand["players"][player]["into_pot"] += amount
                    contributions[player] = 0
                if Done == True:
                    hand["players"][hand["betting_rounds"][betting_round][-1]['player']]["winnings"]+= hand["betting_rounds"][betting_round][-1]['amount']
                    break
            else:
                line = file.readline()
                hand["showdown_action"] = []
                while '*** SUMMARY ***' not in line:
                    if re.match(mucks_pattern, line) != None:
                        hand["showdown_action"].append({'player': re.match(mucks_pattern, line).group(1),
                                                        'action': 'mucks'})
                    elif re.match(shows_pattern, line) != None:
                        hand["showdown_action"].append({'player': re.match(shows_pattern, line).group(1),
                                                        'action': 'shows',
                                                        'cards': re.match(shows_pattern, line).group(2)})
                    elif re.match(collect_pot_pattern, line) != None:
                        match = re.match(collect_pot_pattern, line)
                        hand["showdown_action"].append({'player': match.group(1),
                                                        'action': 'collects_pot',
                                                        'amount': Decimal(match.group(2))})
                        hand["players"][match.group(1)]["winnings"]+= Decimal(match.group(2))
                        
                    elif re.match(cashout_pattern, line) != None:
                        match = re.match(cashout_pattern, line)
                        hand["showdown_action"].append({'player': match.group(1),
                                                        'action': 'collects_pot',
                                                        'amount': Decimal(match.group(2))})
                        hand["players"][match.group(1)]["winnings"]+= Decimal(match.group(2))
                        
                    
                    line = file.readline()

            Parse_summary(hand, file)
            yield hand

def Parse_summary(hand,file):
    line = file.readline()
    match = re.match("Total pot \$(\d*(?:\.\d\d)?)( Main pot \d*. Side pot \d*.)? \| Rake \$(\d*(?:\.\d\d)?)" , line)
    hand["pot"] = match.group(1)
    hand["rake"] = match.group(2)
    
    line = file.readline()
    match = re.match("Board \[([AKQJTschd2-9 ]*)\]" , line)
    while file.readline() != "\n":
        pass
    file.readline()
    file.readline()
    return
    

my_name = ""

money_pattern = '\$\d*(?:\.\d\d)?' ## regex pattern for dollar amounts in the form $x.yz or $x


## regex patterns to parse the 2 header lines for each hand
header_pattern1 = "PokerStars Hand #(\d*):  Hold'em No Limit \((\$\d*(?:\.\d\d)?/\$\d*(?:\.\d\d)? USD)\) - (\d{4}/\d{2}/\d{2}) (\d{2}:\d{2}:\d{2}) WET \[\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} ET\]"
header_pattern2 = "Table '([a-zA-Z\s]*)' (\d)-max Seat #(\d) is the button"

## regex for seat allocations, group 1: seat number, group 2: player name, group 3: chip stack
seat_pattern = "Seat (\d): (.*) \(\$(\d*(?:\.\d\d)?) in chips\) "#


blinds_pattern = "(.*): posts (big|small) blind \$(\d*(?:\.\d\d)?)"
delt_pattern = 'Dealt to ' + my_name + ' \[([AKQJT2-9][schd] [AKQJT2-9][schd])\]'
bet_pattern = '(.*): (folds|bets|calls|raises|checks)(.*)'
shows_pattern = '(.*): shows \[([AKQJT2-9][schd] [AKQJT2-9][schd])\] \(([a-zA-Z\s]*)\)'
mucks_pattern = '(.*): mucks hand'
return_pattern = 'Uncalled bet \(\$(\d*(?:\.\d\d)?)\) returned to (.*)'
collect_pot_pattern = '(.*) collected \$(\d*(?:\.\d\d)?) from pot'
limit_pattern = '\*\*\* (FLOP|TURN|RIVER|SHOW DOWN) \*\*\*'
cashout_pattern = '(.*) cashed out the hand for \$(\d*(?:\.\d\d)?) \| Cash Out Fee \$(\d*(?:\.\d\d)?)'

betting_rounds = ["pre_flop", "flop", "turn", "river"]





             



