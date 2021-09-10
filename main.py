# Imports ==========

import traceback
import logging
from datetime import datetime

import utils
from bot import NFSBot


# Main Program ==========
def run(logger):
    discord_config = utils.get_discord_config()

    logger.info("Starting discord bot...")

    bot = NFSBot(discord_config["token"], discord_config["prefix"])
    bot.run()


if __name__ == '__main__':

    try:
        # Setup Logging

        timeNow = str(datetime.now()).replace(" ", "_").replace(":", "-")

        config = utils.get_config()

        if config["app"]["logging"]:
            logging.basicConfig(
                handlers=[logging.FileHandler(filename=f"logs/{timeNow}.txt",
                                              encoding='utf-8', mode='a+'),
                          logging.StreamHandler()],
                level=logging.INFO,
                format='[%(asctime)s] %(levelname)s:%(name)s - %(message)s'
            )
        else:
            logging.basicConfig(
                handlers=[logging.StreamHandler()],
                level=logging.INFO,
                format='[%(asctime)s] %(levelname)s:%(name)s - %(message)s'
            )
        logging.info(f"Niki for Speed bot logs - {timeNow}")

        run(logging.getLogger(__name__))

    except Exception as e:
        logging.error(str(e) + "\n\n" + traceback.format_exc())
