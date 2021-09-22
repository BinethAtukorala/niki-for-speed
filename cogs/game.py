from discord.ext import commands
import discord
import asyncio

import utils

# Game Imports =====================

import time
import math
import random
import re

# Constants ========================

XP_VALUES = {
    "easy": 100,
    "medium": 200,
    "hard": 400
}

class GameCog(commands.Cog):
    """
    The fun stuff lol.
    """

    def __init__(self, bot):
        self.bot = bot
        self.currently_running_races = {}
    
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

    @commands.command(name="sp")
    async def sp(self, ctx):
        """Start a new singleplayer race"""

        if ctx.channel.id in self.currently_running_races:
            already_running_embed = discord.Embed(
                title=f"There is already a race active on this channel."
            )
            await ctx.send(embed=already_running_embed)
            return

        welcome_embed = discord.Embed(
            title=f"Niki for Speed: Text Edition v8.306624...",
            description="**Singleplayer Race** 🏎️\nThe race will start in 5 seconds..."
        ).add_field(
            name="Instructions",
            value=":white_small_square: Enter the correct order of steps to go to the finish line.\n:white_small_square: The steps are w - forward, a - left, s - down, d - right.\n:white_small_square: An example path might look like this :- wwasdwdasasssdw\n:white_small_square: You only have 3 tries to complete the race.\n:white_small_square: You only have 90 seconds between each try."
        )

        self.currently_running_races[ctx.channel.id] = {
            'mode': 'sp',
            'user_id': ctx.author.id
        }

        await ctx.send(embed=welcome_embed)
        
        # Pick a random map and record start time
        current_map = next(utils.get_random_map())

        # Wait for 5 seconds for the race to start
        await asyncio.sleep(5)

        map_embed = discord.Embed(
            title=f"Racetrack - {current_map['name']}",
            description=self.format_map(current_map["map"])
        )
        await ctx.send(embed=map_embed)

        start_time_milis = round(time.time() * 1000  - self.bot.latency * 100)

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
                        self.currently_running_races.pop(ctx.channel.id)
                        await ctx.send(embed=discord.Embed(title="You took too long to finish the race. You lost slowpoke!"))
                        return
                    # Record finishing time
                    finish_time_milis = round(time.time() * 1000  - self.bot.latency * 100)
                    guess = msg.content.lower().strip()
                guess_count += 1
            else:
                limit_reached = True
        if limit_reached:
            final_embed = discord.Embed(title="You ran out of tries. You lost!")
        else:

            # Get user's profile or create a new profile if they dont have one
            current_profile = utils.get_profile_by_discord_id(ctx.author.id)
            # If no profile exists
            if current_profile == None:
                current_profile = utils.new_profile(ctx.author.id)

            # Check for faster lap

            fastest_laps = current_profile["fastest_laps"]
            fastest_lap_achieved = False

            if str(current_map["_id"]) in fastest_laps:
                if finish_time_milis - start_time_milis < fastest_laps[str(current_map["_id"])]:
                    fastest_laps[str(current_map["_id"])] = finish_time_milis - start_time_milis
                    utils.set_high_score(current_profile["_id"], fastest_laps)
                    fastest_lap_achieved = True
            else:
                fastest_laps[str(current_map["_id"])] = finish_time_milis - start_time_milis
                utils.set_high_score(current_profile["_id"], fastest_laps)
                fastest_lap_achieved = True
            
            # Update XP and race count
            if "difficulty" in current_map:
                xp_earned = XP_VALUES[current_map["difficulty"]]
            # give the default xp amount if no difficulty is set
            else:
                xp_earned = XP_VALUES["easy"]
            
            utils.sp_won(current_profile["_id"], xp_earned)

            # Output time taken
            time_taken = self.format_time(finish_time_milis - start_time_milis)
            final_embed = discord.Embed(
                title="You won!",
                description="Time taken: {}\n\n{}".format(
                    time_taken, 
                    "**New fastest lap achieved!** 🎉" if fastest_lap_achieved else ""
                    )
            )

        self.currently_running_races.pop(ctx.channel.id)
        await ctx.send(embed=final_embed)
# are you ruining my code that i worked SO hard on
# lmfao yeah, get rekt
# stupid bitch <--- no you niki yes imdelete ng lmfaooooo  -.- that looks weird. already took a ss :D mf okay okay add the instructions now you cant run more than one race in one channel
# :D
# :'(

    @commands.command(name="mp")
    async def mp(self, ctx):
        """Start a new multiplayer race"""

        if ctx.channel.id in self.currently_running_races:
            already_running_embed = discord.Embed(
                title=f"There is already a race active on this channel."
            )
            await ctx.send(embed=already_running_embed)
            return
        
        self.currently_running_races[ctx.channel.id] = {
                'message_id': None,
                'map_message_id': None,
                'mode': 'mp',
                'map': None,
                'ongoing': True,
                'guess_limit': 3,
                'winner': None,
                'players': {
                    ctx.author.id: {
                        'finish_time_milis': 0,
                        'guess_count': 0
                    }
                }
            }

        welcome_embed = discord.Embed(
            title=f"Niki for Speed: Text Edition v8.306624...",
            description="**Multiplayer Race** 🏎️\nThe race will start after players have signed up..."
        ).add_field(
            name="Instructions",
            value=":white_small_square: React to the message below to join the race.\n:white_small_square: Enter the correct order of steps to go to the finish line.\n:white_small_square: The steps are w - forward, a - left, s - down, d - right.\n:white_small_square: An example path might look like this :- wwasdwdasasssdw\n:white_small_square: You only have 3 tries to complete the race.\n:white_small_square: You only have 90 seconds between each try."
        )

        await ctx.send(embed=welcome_embed)

        race_join_embed = discord.Embed(
            title="React to this message to join.",
            description=f"Click on the reaction below to join the multiplayer race started by {ctx.author.mention}\n(10 seconds left)"
        ).add_field(
            name="Racers joined",
            value=f":white_small_square: <@{ctx.author.id}>"
        )

        race_join_message = await ctx.send(embed=race_join_embed)
        await race_join_message.add_reaction('✅')

        self.currently_running_races[ctx.channel.id] = {
                'message_id': race_join_message.id,
                'map_message_id': None,
                'mode': 'mp',
                'map': None,
                'ongoing': True,
                'guess_limit': 3,
                'winner': None,
                'players': {
                    ctx.author.id: {
                        'finish_time_milis': 0,
                        'guess_count': 0
                    }
                }
            }

        await asyncio.sleep(10)

        # Check if there are 2 or more races
        if(len(self.currently_running_races[ctx.channel.id]['players']) > 1):

            # Pick a random map and record start time
            current_map = next(utils.get_random_map())

            # Wait for 5 seconds for the race to start
            await asyncio.sleep(5)

            racers_status_str = ""

            for player in self.currently_running_races[ctx.channel.id]['players']:
                racers_status_str += f"<@{player}> - :white_square_button::white_square_button::white_square_button:\n"

            map_embed = discord.Embed(
                title=f"Racetrack - {current_map['name']}",
                description=self.format_map(current_map["map"])
            ).add_field(
                name="Status",
                value=racers_status_str
            )
            map_message = await ctx.send(embed=map_embed)

            self.currently_running_races[ctx.channel.id]['map'] = current_map['map']
            self.currently_running_races[ctx.channel.id]['map_message_id'] = map_message.id

            start_time_milis = round(time.time() * 1000  - self.bot.latency * 100)

            countdown = 90
            while(self.currently_running_races[ctx.channel.id]['ongoing']):
                await asyncio.sleep(1)
                countdown -= 1

                if(countdown == 0):
                    self.currently_running_races[ctx.channel.id]['ongoing'] = False
                else:
                    ongoing = False
                    for player in self.currently_running_races[ctx.channel.id]['players']:
                        print(player, self.currently_running_races[ctx.channel.id]['players'][player]['guess_count'])
                        if self.currently_running_races[ctx.channel.id]['players'][player]['finish_time_milis'] == 0 and self.currently_running_races[ctx.channel.id]['players'][player]['guess_count'] < self.currently_running_races[ctx.channel.id]['guess_limit']:
                            ongoing = True
                    self.currently_running_races[ctx.channel.id]['ongoing'] = ongoing
            
            # Update user profiles
            players = self.currently_running_races[ctx.channel.id]['players']

            sorted_players = sorted(players.items(), key=lambda k_v: k_v[1]['finish_time_milis'])
            for idd, x in enumerate(sorted_players):
                if x[1]['finish_time_milis'] == 0:
                    sorted_players.append(sorted_players.pop(sorted_players.index(x)))

            results_string = ""
            
            counter = 1
            for player in sorted_players:
                player_id = player[0]

                # Check if racer finished the race
                if players[player_id]['finish_time_milis'] != 0:
                    
                    finish_time_milis = players[player_id]['finish_time_milis']

                    # Get user's profile or create a new profile if they dont have one
                    current_profile = utils.get_profile_by_discord_id(player_id)
                    # If no profile exists
                    if current_profile == None:
                        current_profile = utils.new_profile(player_id)
                    
                    # Check for faster lap

                    fastest_laps = current_profile["fastest_laps"]
                    fastest_lap_achieved = False

                    if str(current_map["_id"]) in fastest_laps:
                        if finish_time_milis - start_time_milis < fastest_laps[str(current_map["_id"])]:
                            fastest_laps[str(current_map["_id"])] = finish_time_milis - start_time_milis
                            utils.set_high_score(current_profile["_id"], fastest_laps)
                            fastest_lap_achieved = True
                    
                    else:
                        fastest_laps[str(current_map["_id"])] = finish_time_milis - start_time_milis
                        utils.set_high_score(current_profile["_id"], fastest_laps)
                        fastest_lap_achieved = True

                    # Update XP and race count
                    if "difficulty" in current_map:
                        xp_earned = XP_VALUES[current_map["difficulty"]]
                    # give the default xp amount if no difficulty is set
                    else:
                        xp_earned = XP_VALUES["easy"]
                    
                    # If the player is the winner
                    if player_id == self.currently_running_races[ctx.channel.id]['winner']:
                        utils.mp_won(current_profile["_id"])
                        xp_earned += int(xp_earned/2)
                    
                    utils.sp_won(current_profile["_id"], xp_earned)

                    # Output time taken
                    time_taken = self.format_time(finish_time_milis - start_time_milis)

                    results_string += f":white_small_square: #{counter} <@{player_id}> - {time_taken}\n"
                
                # Racer hasn't finished the race
                else:
                    results_string += f":white_small_square: #{counter} <@{player_id}> - DNF\n"
                
                counter += 1
            
            final_embed = discord.Embed(
                title="Race results!",
                description=f"**Winner** - <@{self.currently_running_races[ctx.channel.id]['winner']}>"
            ).add_field(
                name="Leaderboard",
                value=results_string
            )

            await ctx.send(embed=final_embed)

        else:

            not_enough_racers_embed = discord.Embed(
                title="Not enough racers...",
                description="Need 2 or more racers to start."
            )

            await ctx.send(embed=not_enough_racers_embed)
        self.currently_running_races.pop(ctx.channel.id)

    
    @commands.Cog.listener()
    async def on_message(self, message):

        finish_time_milis = round(time.time() * 1000  - self.bot.latency * 100)

        # Check that the message is not from the bot
        if message.author.id != self.bot.user.id:

            # Check whether a race exists in the channel
            if message.channel.id in self.currently_running_races:

                # Get current race details to a variable
                current_race = self.currently_running_races[message.channel.id]

                # Check if it's a multiplayer
                if current_race['mode'] == 'mp': 

                    # Check if the user has signed up for the race && that the sign-up phase is over (whether a map is set or not) && whether the race has stopped looking for guesses (ongoing)
                    if message.author.id in current_race['players'] and current_race['map'] != None and current_race['ongoing']:
                        # Get the guess
                        guess = message.content.lower().strip()
                        # Get the current racer details from current_race
                        current_racer = current_race['players'][message.author.id]

                        # Check whether the guess is a valid path
                        if re.search(r'^[wasd]+$', guess):

                            # Check whether this racer has passed the guess limit
                            if current_racer['guess_count'] < current_race['guess_limit']:

                                # Check whether the racer hasn't finished the race
                                if current_racer['finish_time_milis'] == 0:
                                
                                    # Check whether it's the correct path
                                    if self.correct_path(current_race['map'], guess):

                                        # Check whether a winner doesn't exist
                                        if(current_race['winner'] == None):
                                            self.currently_running_races[message.channel.id]['winner'] = message.author.id

                                        self.currently_running_races[message.channel.id]['players'][message.author.id]['finish_time_milis'] = finish_time_milis
                                        asyncio.run_coroutine_threadsafe(message.add_reaction('✅'), asyncio.get_event_loop())
                                    
                                    # Not the correct path -> increase guess counter
                                    else:
                                        self.currently_running_races[message.channel.id]['players'][message.author.id]['guess_count']+=1
                                        asyncio.run_coroutine_threadsafe(message.add_reaction('❌'), asyncio.get_event_loop())

                                    async def edit_map_message():
                                        racers_status_str = ""
                                        current_race = self.currently_running_races[message.channel.id]
                                        for player in current_race['players']:
                                            racers_status_str += f"<@{player}> - " + "".join(":x:" for x in range(current_race['players'][player]['guess_count']))
                                            if (current_race['players'][player]['finish_time_milis'] != 0):
                                                racers_status_str += ":white_check_mark:"
                                                racers_status_str  += "".join(":white_square_button:" for x in range(current_race['guess_limit'] - 1 - current_race['players'][player]['guess_count']))
                                            else:
                                                racers_status_str  += "".join(":white_square_button:" for x in range(current_race['guess_limit'] - current_race['players'][player]['guess_count']))
                                            racers_status_str += "\n"

                                        map_message = await message.channel.fetch_message(current_race['map_message_id'])
                                        map_message.embeds[0].clear_fields()
                                        await map_message.edit(
                                            embed=map_message.embeds[0].add_field(
                                                name="Status",
                                                value=racers_status_str
                                            )
                                        )
                                    
                                    asyncio.run_coroutine_threadsafe(edit_map_message(), asyncio.get_event_loop())
                                
                                # If racer has finished the race -> ignore

                            # Passed the guess limit -> ignore
                        
                        # Not a valid path -> ignore
                    
                    # Hasn't signed up -> ignore



    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.bot.user.id:
            if payload.channel_id in self.currently_running_races:
                if self.currently_running_races[payload.channel_id]['map'] == None:
                    if payload.user_id not in self.currently_running_races[payload.channel_id]['players']:
                        self.currently_running_races[payload.channel_id]['players'][payload.user_id] = {
                                                                                                        'finish_time_milis': 0,
                                                                                                        'guess_count': 0
                                                                                                    }
                        channel = await self.bot.fetch_channel(payload.channel_id)
                        message = await channel.fetch_message(self.currently_running_races[payload.channel_id]['message_id'])
                        message.embeds[0].clear_fields()
                        await message.edit(
                            embed=message.embeds[0].add_field(
                                name="Racers joined",
                                value=":white_small_square: " + "\n:white_small_square: ".join([f"<@{player}>" for player in self.currently_running_races[payload.channel_id]['players']])
                            )
                        )

def setup(bot):
    bot.add_cog(GameCog(bot))