import discord
from discord.ext import commands
from pymongo import MongoClient

import utils

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def calculate_level(self, xp):
        inc = 0
        level = 0
        level_xp = 0
        while(level_xp <= xp):
            if(level%5 == 0):
                inc += 2500
            level_xp += inc
            level += 1
        return level

    @commands.command(name="level")
    async def level(self, ctx):
        current_profile = utils.get_profile_by_discord_id(ctx.author.id)
        level = self.calculate_level(current_profile["xp"])

        level_embed = discord.Embed(
            title="Level {}".format(level),
            description="You have `{}xp`".format(current_profile["xp"])
        )

        await ctx.send(embed=level_embed)

    @commands.command(name="profile")
    async def profile(self, ctx):
        current_profile = utils.get_profile_by_discord_id(ctx.author.id)
        
        profile_embed = discord.Embed(
            title="{}'s Profile".format(ctx.author.display_name),
            description=" Multiplayer Wins: {}\n Races Completed: {}\n Current Level: {}\n XP Earned: {}xp".format(current_profile['multiplayer_wins'], current_profile["race_count"], self.calculate_level(current_profile["xp"]), current_profile["xp"])
        )

        await ctx.send(embed=profile_embed)

def setup(bot):
    bot.add_cog(Profile(bot))