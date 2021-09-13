# Imports ==========

import json
import logging
from datetime import datetime

import discord

from pymongo import MongoClient
import pymongo

# Reading config.json

def get_config():
    """
    READ /data/config.json and return it's content as a dict
    """
    try:
        with open("data/config.json", "r") as f:
            data = f.read()
        return json.loads(data)
    except IOError:
        raise Exception("File not accessible")

def get_discord_config():
    """
    Returns discord configs in /config.json as a dict
    """
    config = get_config()

    try:
        discord_configs = config["discord"]
        return {"token": discord_configs["token"], "prefix": discord_configs["prefix"]}
    except:
        raise Exception("Couldn't find discord configs in /config.json")

def get_commands_help():
    """
    READ /data/help.json and return a dictionary of it's data
    """
    with open("data/help.json", "r") as f:
        data = f.read()
    return json.loads(data)["commands"]

# MongoDB

mongo_config = get_config()["mongo"]
CONNECTION_STRING = mongo_config["connection_string"]
database = mongo_config["database"]

client = MongoClient(CONNECTION_STRING)

db = client[database]

maps_col = db["maps"]
profiles_col = db["profiles"]

def get_random_map():
    """
    Get a random map from MongoDB
    """

    return maps_col.aggregate([{"$sample": {"size": 1}}])

def get_profile_by_discord_id(discord_id):
    """
    Get the user's profile with their Discord ID
    """

    profile = profiles_col.find_one({"discord_id": discord_id})

    return profile

def new_profile(discord_id):
    """
    Create a new profile and return it
    """

    profile = {
        "discord_id": discord_id,
        "xp": 0,
        "race_count": 0,
        "multiplayer_wins": 0,
        "badges": [],
        "multiplayer_streak": 0,
        "fastest_laps": {}
    }

    result = profiles_col.insert_one(profile)

    return profiles_col.find_one({"_id": result.inserted_id})

def sp_won(id, xp_earned):

    result = profiles_col.update_one({"_id": id}, {"$inc": {"xp": xp_earned, "race_count": 1}})

    return result

def set_high_score(id, fastest_laps):

    result = profiles_col.update_one({"_id": id}, {"$set": {"fastest_laps": fastest_laps}})

def get_top_five_race_count():

    aggregate_pipeline = [
        {
            "$sort": {"race_count": -1}
        },
        {
            "$limit": 5
        }
    ]

    result = profiles_col.aggregate(aggregate_pipeline)

    return list(result)