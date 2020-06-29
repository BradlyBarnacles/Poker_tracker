# Poker_tracker
This is my personal attempt to write a poker tracker, reading the hand history files produced by PokerStars to create player statistics. At present these statistics are put into a pandas DataFrame, and then saved to a csv.

handhistory.py - this contains generator function Parse_hands(file), which creates a dictionary to describe the events of each hand in a file.
hand_analysis.py - Updates the csv file of player statistics.
