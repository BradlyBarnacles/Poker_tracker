# Poker_tracker
This is my personal attempt to write a poker tracker, reading the hand history files produced by PokerStars to create player statistics. At present these statistics are put into a pandas DataFrame, and then saved to a csv.

handhistory.py - this contains generator function Parse_hands(file), which creates a dictionary to describe the events of each hand in a file.

hand_analysis.py - Updates the csv file of player statistics.

example_hand.txt – example hand data which poker tracker takes as input.

example_data.txt – corresponding dictionary produced by Parse_hands.

If you wish to run this on your own computer, you will want to change the variables "my_name", "in_path" and "out_path" in handhistory.py and hand_analysis.py.
