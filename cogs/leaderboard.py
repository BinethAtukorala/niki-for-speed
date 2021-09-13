import discord
from discord.ext import commands
from pymongo import MongoClient

import utils

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="top")
    async def top_racess(self, ctx, *args):
        leaderboard_string = ""
        leaderbooard_title = ""

        if(len(args) > 0):
            if(args[0] == "races"):
                top_five = utils.get_top_five_race_count()
            if(args[0] == "levels"):
                top_five = utils.get_top_five_calculate_level()
                
                print(top_five)

                leaderbooard_title = "Race Count"

                for x in range(1, len(top_five) + 1):
                    profile = top_five[x-1]
                    profile_string = "**" if profile["discord_id"] == ctx.author.id else ""
                    profile_string += "#" + str(x) + " | "
                    profile_string += "<@" + str(profile["discord_id"]) + "> - "
                    profile_string += str(profile["race_count"])
                    profile_string += str(utils.calculate_level(profile["xp"]))
                    profile_string += "**" if profile["discord_id"] == ctx.author.id else ""
                    leaderboard_string += profile_string if leaderboard_string == "" else "\n" + profile_string


        leaderboard_embed = discord.Embed(
            title=f"Leaderboard - {leaderbooard_title}",
            description=leaderboard_string
        )

        await ctx.send(embed=leaderboard_embed)

    

def setup(bot):
    bot.add_cog(LeaderboardCog(bot))