from discord.ext import commands
import discord

import utils

class MainCog(commands.Cog):
    """
    Handles main aspects of the bot such as bot settings.
    """

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check whether the bot is online"""

        await ctx.send("Pong! `{}ms` 🏓".format(int(self.bot.latency * 100)))

def setup(bot):
    bot.add_cog(MainCog(bot))