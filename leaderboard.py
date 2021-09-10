from discord.ext import commands
import discord
import exp

cogs = [exp]

client = commands.Bot(command_prefix="nfs", intents=discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

client.run()  # this is def already done

talk_channels = []
