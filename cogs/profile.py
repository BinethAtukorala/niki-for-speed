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
            title="{}'s Profile".format(ctx.author.id["display_name"]),
            description="Races Completed: {}".format(current_profile["race_count"])
        )

        await ctx.send(embed=profile_embed)



    # @commands.command(name="leaderboard")
    # async def leaderboard(self, ctx):
    #     if ctx.channel.id == talk_channels:
    #         rankings = leveling.find().sort("xp", -1)
    #         i = 1
    #         embed = discord.Embed(title="rankings")
    #         for x in rankings:
    #             try:
    #                 temp = ctx.guild.get_member(x["id"])
    #                 tempxp = x["xp"]
    #                 embed.add_field(name=f"{i}: {temp.name}", value=f"Total XP: {tempxp}", inline=False)
    #                 i += 1
    #             except:
    #                 pass
    #             if i == 11:
    #                 break
    #         await ctx.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(bot(bot))
    