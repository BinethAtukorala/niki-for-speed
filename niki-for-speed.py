#!/usr/bin/env python

"""
Niki for Speed: Text Edition
- A text based racing game

By: Bineth Atukorala, Nikita Ünver
Development started: 7th September 2021
"""

# Imports =====================

import random
import time
import math
import json

# Variables =====================

maps_data = []
with open('maps.json') as f:
    maps_data = json.load(f)["maps"]

# Functions =====================

def print_map(map: list):
    print("+" + "-" * len(map[0]) + "+")
    for line in map:
        print("|" + line + "|")
    print("+" + "-" * len(map[0]) + "+")

def print_time(time_taken_milis):
    mins = math.floor(time_taken_milis / 60 / 1000)
    time_taken_milis = time_taken_milis - mins * 60 * 1000
    secs = math.floor(time_taken_milis / 1000)
    time_taken_milis = time_taken_milis - secs * 1000
    milis = time_taken_milis

    print()
    print("Time taken :", mins, "min", secs, "sec", milis, "ms")

# Main Program =====================

# Welcome message
print()
print("Welcome Niki for Speed: Text Edition")
print("- A text based racing game")
print()
print("Instructions")
print("* Enter the correct order of steps to go to the finish line.")
print("* The steps are w - forward, a - left, s - down, d - right.")
print("* An example path might look like this :- wwasdwdasasssdw")
print("* You only have 3 tries to complete the race.")
print()

# Wait for input to start
start_game = "start"
command = input("Type Start to begin the race: ")
if command.lower() == start_game:
    # Record start time
    print()
    print("!!!Time Started!!!")
    print()
    start_time_milis = round(time.time() * 1000)

    # Pick a random map and record start time
    current_map = maps_data[random.randint(0, len(maps_data)-1)]
    
    # Logic for printing out the map
    print_map(current_map["map"])
    print()

    # Check for correct path - the key is `current_map["path"]`
    guess_count = 0
    guess_limit = 3
    limit_reached = False
    guess = ""
    current_map["path"]

    while guess != current_map["path"] and not limit_reached:
        if guess_count < guess_limit:
            print("You have", guess_limit - guess_count, "tries left.")
            guess = input("Enter the right path: ")
            print()
            guess_count += 1
        else:
            limit_reached = True

    if limit_reached:
        print("!!!You ran out of tries. You lost!!!")
    else:
        print("!!!You took the right path. You win!!!")

        # Record finishing time
        finish_time_milis = round(time.time() * 1000)
        
        # Output time taken
        print_time(finish_time_milis - start_time_milis)