import discord
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp

import logging

logger = logging.getLogger('__main__')


class NFSBot(commands.Bot):
    COGS = [
        'cogs.game',
        'cogs.main',
        'cogs.profile',
        'cogs.leaderboard'
    ]

    def __init__(self, token, prefix):
        self.TOKEN = token
        super().__init__(
            command_prefix=prefix,
            description="Niki for Speed: Text Edition v8.306624..."
        )

        # self.help_command = PrettyHelp(
        #     navigation=DefaultMenu('◀️', '▶️', '❌'),
        #     color=discord.Colour.blue()
        # )

        self.help_command = None

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
    
    @commands.command(name="help")
    async def help(self, ctx, *args):
        """The help command of the bot"""

        help_embed = discord.Embed(
            title="❓ Help - Niki for Speed v8.306624...",
            description="**For more info: nfs help [command]**\nAdd `nfs` before any command"
            )
        
        await ctx.send(embed=help_embed)

    def run(self):
        super().run(self.TOKEN, reconnect=True)
