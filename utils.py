# Imports ==========

import json
import logging
from datetime import datetime

import discord

# Reading config.json

def get_config():
    """
    READ /config.json and return it's content as a dict
    """
    try:
        with open("config.json", "r") as f:
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

def get_maps_data():
    """
    READ /maps.json and return a list of maps.
    """
    with open("maps.json", "r") as f:
        data = f.read()
    return json.loads(data)["maps"]