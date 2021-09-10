import discord
from discord.ext import commands
from pymongo import MongoClient

level_name = ["lev1", "lev2", "lev3"]
#  rankings = ["rank1", "rank2", "rank3"]
level = [1, 5, 10]

talk_channels = [885179991028015145]

cluster = MongoClient("")

leveling = cluster["discord"]["leveling"]

class Exp(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("ready!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in talk_channels:
            stats = leveling.find_one({"id" : message.author.id})
            if not message.autor.bot:
                if stats is None:
                    new_user = {"id" : message.author.id, "xp" : 100}
                    leveling.insert_one(new_user)
                else:
                    xp = stats["xp"] + 5
                    leveling.update_one({"id":message.author.id}, {"$set":"xp"})
                    lvl = 0
                    while True:
                        if xp < ((50*(lvl**2))+(50*(lvl-1))):
                            break
                        lvl += 1
                    xp -= (50*((lvl-1)**2)(50*(lvl-1)))
                    if xp == 0:
                        await message.channel.send(f"well done {message.author.mention}!\n you leveled up to **level: {lvl}**!")
                        for i in range(len(level)):
                            if lvl == level[i]:
                                await message.author.add_roles(discord.utils.get(message.author.guild.roles, name=level_name[i]))
                                embed = discord.Embed(description=f"{message.author.mention} you have gotten role **{level_name[i]}**!")
                                embed.set_thumbnail(url=message.author.avatar_url)
                                await message.channel.send(embed=embed)

        @commands.command()
        async def rank(self, ctx):
            if ctx.channel.id == talk_channels:
                stats = leveling.find_one({"id" : ctx.author.id})
                if stats is None:
                    embed = discord.Embed(description="You haven't earned enough XP yet.")
                    await ctx.channel.send(embed=embed)
                else:
                    xp = stats["xp"]
                    lvl = 0
                    rank = 0
                    while True:
                        if xp < ((50*(lvl**2))+(50*(lvl-1))):
                            break
                        lvl += 1
                    xp -= (50 * ((lvl - 1) ** 2)(50 * (lvl - 1)))
                    boxes = int((xp/(200*((1/2) * lvl)))*20)
                    rankings = leveling.find().sort("xp", -1)
                    for x in rankings:
                        rank += 1
                        if stats ["id"] == x["id"]:
                            break
                    embed = discord.Embed(title="{}'s level stats".format(ctx.author.name))
                    embed.add_field(name="Name", value=ctx.author.mention, inline=True)
                    embed.add_field(name="XP", value=f"{xp}/{int(200*((1/2)*lvl))}", inline=True)
                    embed.add_field(name="Rank", value=f"{rank}/{ctx.guild.member_count}", inline=True)
                    embed.add_field(name="Progress Bar [lvl]", value=boxes * ":blue_square:" + (20-boxes) * ":white_large_square:", inline=False)
                    embed.set_thumbnail(url=ctx.author.avatar_url)
                    await ctx.channel.send(embed=embed)

        @commands.command()
        async def leaderboard(self, ctx):
            if ctx.channel.id == talk_channels:
              rankings = leveling.find().sort("xp", -1)
              i = 1
              embed = discord.Embed(title="rankings")
              for x in rankings:
                  try:
                      temp = ctx.guild.get_member(x["id"])
                      tempxp = x["xp"]
                      embed.add_field(name=f"{i}: {temp.name}", value=f"Total XP: {tempxp}", inline=False)
                      i += 1
                  except:
                      pass
                  if i == 11:
                      break
              await ctx.channel.send(embed=embed)

        def setup(client):
    client.add.cog(exp(client))      
    
