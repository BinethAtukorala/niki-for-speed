from discord.ext import commands
import discord
import asyncio

import utils

# Game Imports =====================

import time
import math
import random
import re

class GameCog(commands.Cog):
    """
    The fun stuff lol.
    """

    def __init__(self, bot):
        self.bot = bot
        self.currently_running_channels = []
    
    def format_time(self, time_taken_milis):
        mins = math.floor(time_taken_milis / 60 / 1000)
        time_taken_milis = time_taken_milis - mins * 60 * 1000
        secs = math.floor(time_taken_milis / 1000)
        time_taken_milis = time_taken_milis - secs * 1000
        milis = time_taken_milis
        return "{} mins {} secs {} ms".format(mins, secs, milis)
    
    def find_start_pos(self, current_map:list):
        print(current_map)
        for x in range(len(current_map)):
            print(current_map[x])
            if "S" in current_map[x]:
                return {"line": x, "char": current_map[x].find("S")}
    
    def correct_path(self, current_map:list, path: str):
        print("Path given", path)
        current_pos = self.find_start_pos(current_map)
        print(current_pos)
        for step in path:
            if step == "w":
                next_pos = {"line": current_pos["line"]-1, "char": current_pos["char"]}
            elif step == "a":
                next_pos = {"line": current_pos["line"], "char": current_pos["char"]-1}
            elif step == "s":
                next_pos = {"line": current_pos["line"]+1, "char": current_pos["char"]}
            else:
                next_pos = {"line": current_pos["line"], "char": current_pos["char"]+1}

            if next_pos["line"] < 0 or next_pos["line"] >= len(current_map) or next_pos["char"] < 0 or next_pos["char"] >= len(current_map[0]):
                return False
            
            if current_map[next_pos["line"]][next_pos["char"]] == " ":
                return False
            
            if current_map[next_pos["line"]][next_pos["char"]] == "E":
                return True
            current_pos = next_pos
        return False

    def format_map(self, current_map: list):
        map_str = ""
        for line in current_map:
            line_str = ""
            for char in line:
                if(char == "X"):
                    line_str += ":black_square_button:"
                elif(char == "S"):
                    line_str += ":red_square:"
                elif(char == "E"):
                    line_str += ":checkered_flag:"
                else:
                    line_str += ":black_large_square:"
            map_str += line_str + "\n"
        return map_str

    @commands.command(name="race")
    async def race(self, ctx):
        """Start a new race"""

        if ctx.channel.id in self.currently_running_channels:
            already_running_embed = discord.Embed(
                title=f"There is already a race active on this channel."
            )
            await ctx.send(embed=already_running_embed)
            return

        maps_data = utils.get_maps_data()

        welcome_embed = discord.Embed(
            title=f"Niki for Speed: Text Edition v8.306624...",
            description="The race will start in 5 seconds..."
        ).add_field(
            name="Instructions",
            value=":white_small_square: Enter the correct order of steps to go to the finish line.\n:white_small_square: The steps are w - forward, a - left, s - down, d - right.\n:white_small_square: An example path might look like this :- wwasdwdasasssdw\n:white_small_square: You only have 3 tries to complete the race.\n:white_small_square: You only have 90 seconds between each try."
        )

        self.currently_running_channels.append(ctx.channel.id)

        await ctx.send(embed=welcome_embed)
        
        # Wait for 5 seconds for the race to start
        await asyncio.sleep(5)

        # Pick a random map and record start time
        current_map = maps_data[random.randint(0, len(maps_data)-1)]

        map_embed = discord.Embed(
            title=f"Racetrack",
            description=self.format_map(current_map["map"])
        )
        await ctx.send(embed=map_embed)

        start_time_milis = round(time.time() * 1000)

        guess_count = 0
        guess_limit = 3
        limit_reached = False
        guess = ""

        while (not self.correct_path(current_map["map"], guess)) and not limit_reached:
            if(guess_count > 0):
                tries_left_embed = discord.Embed(
                    title="You have {} tries left.".format(guess_limit - guess_count)
                    )
                await ctx.send(embed=tries_left_embed)
            if guess_count < guess_limit:
                guess = ""
                def check(channel):
                    def inner_check(message):
                        return message.channel == channel
                    return inner_check
                while(not(re.search(r'^[wasd]+$', guess))):
                    try:
                        msg = await self.bot.wait_for('message', check=check(ctx.channel), timeout=90)
                    # Timeout if they take too much time to reply
                    except asyncio.TimeoutError:
                        print("Time out")
                        self.currently_running_channels.pop(self.currently_running_channels.index(ctx.channel.id))
                        await ctx.send(embed=discord.Embed(title="You took too long to finish the race."))
                        return
                    # Record finishing time
                    finish_time_milis = round(time.time() * 1000)
                    guess = msg.content.lower().strip()
                guess_count += 1
            else:
                limit_reached = True
        if limit_reached:
            final_embed = discord.Embed(title="You ran out of tries. You lost!")
        else:            
            # Output time taken
            time_taken = self.format_time(finish_time_milis - start_time_milis)
            final_embed = discord.Embed(
                title="You took the right path. You won!",
                description="Time taken: {}".format(time_taken)
                )
        self.currently_running_channels.pop(self.currently_running_channels.index(ctx.channel.id))
        await ctx.send(embed=final_embed)
# are you ruining my code that i worked SO hard on
# lmfao yeah, get rekt
# stupid bitch <--- no you niki yes imdelete ng lmfaooooo  -.- that looks weird. already took a ss :D mf okay okay add the instructions now you cant run more than one race in one channel
# :D
# :'(
def setup(bot):
    bot.add_cog(GameCog(bot))