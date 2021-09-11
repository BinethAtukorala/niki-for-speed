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

        pong_embed = discord.Embed(title="Pong! `{}ms` 🏓".format(int(self.bot.latency * 100)))

        await ctx.send(embed=pong_embed)

    @commands.command(name="help")
    async def help(self, ctx, *args):
        """The help command of the bot"""

        if(len(args) > 0):

            commands_help = utils.get_commands_help()

            for category in commands_help.keys():
                for x in commands_help[category]:
                    if(x["name"] == args[0]):
                        help_embed = discord.Embed(
                            title=f"❓ Help - {x['name']}",
                            description=x["description"]
                        ).add_field(
                            name="Usage",
                            value=f"`{x['usage']}`"
                        )

                        await ctx.send(embed=help_embed)
                        return

            help_embed = discord.Embed(
                title="❓ Help - Niki for Speed v8.306624..",
                description="**No command found**"
            )
            await ctx.send(embed=help_embed)

        else:

            help_embed = discord.Embed(
                title="❓ Help - Niki for Speed v8.306624...",
                description="**For more info: nfs help [command]**\nAdd `nfs` before any command"
                )

            commands_help = utils.get_commands_help()

            game_commands_str = ""

            for x in commands_help["game"]:
                game_commands_str += "`" + x["name"] + "`, "

            help_embed = help_embed.add_field(
                name="🎮 Game commands",
                value=game_commands_str[:-2]
            )
            
            await ctx.send(embed=help_embed)

def setup(bot):
    bot.add_cog(MainCog(bot))