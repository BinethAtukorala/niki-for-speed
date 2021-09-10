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

def get_random_map():
    """
    Get a random map from MongoDB
    """

    return maps_col.aggregate([{"$sample": {"size": 1}}])
    