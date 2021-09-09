import discord
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp

import utils

import logging
logger = logging.getLogger('__main__')

class NFSBot(commands.Bot):

    COGS = [
        'cogs.game',
        'cogs.main'
    ]

    def __init__(self, token, prefix):
        self.TOKEN = token
        super().__init__(
            command_prefix=prefix,
            description="Niki for Speed: Text Edition v8.306624..."
        )

        self.help_command = PrettyHelp(
            navigation=DefaultMenu('◀️', '▶️', '❌'), 
            color=discord.Colour.blue()
        )

        for cog in self.COGS:
            try:
                self.load_extension(cog)
            except Exception as e:
                raise Exception("Failed to load cog {}".format(cog))
    
    async def on_ready(self):
        printString = "\nLogged in as:" + "\n"
        printString += "Username: " + self.user.name + "#" + self.user.discriminator + "\n"
        printString += "ID: " + str(self.user.id) + "\n\n"
        printString += "Connected to servers: " + "\n"
        guilds = await self.fetch_guilds(limit=100).flatten()
        for guild in guilds:
            printString += "*" + guild.name + "\n"
        
        logger.info(printString)

        await self.change_presence(status=discord.Status.online, activity=discord.Game("Niki and Furious"))

    def run(self):
        super().run(self.TOKEN, reconnect=True)