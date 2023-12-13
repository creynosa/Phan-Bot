# import logging
# import random
# from pathlib import Path
# from typing import Optional
#
# import discord
# import num2words
# import yaml
# from discord.ext import commands, tasks
#
# logger = logging.getLogger("main.ButtonGame")
# logger.handlers.clear()


# ACCESS_KEY = os.environ["s3-access-key"]
# SECRET_KEY = os.environ["s3-secret-access-key"]
# s3 = boto3.client("s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)


# class ButtonGame(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.embedLogoURL = "https://i.imgur.com/CkAoqD2.png"
#         self.config = None
#         self.isCurrentlyProcessing = {}
#
#     @staticmethod
#     def configDownload() -> None:
#         """Downloads the game configuration file from AWS."""
#         configPath = Path.cwd() / "resources" / "buttongame.yaml"
#
#         # s3.download_file("phanbot", "buttongame.yaml", str(configPath))
#
#     @staticmethod
#     def configUpload() -> None:
#         """Uploads the game configuration file to AWS."""
#         configPath = Path.cwd() / "resources" / "buttongame.yaml"
#
#         # s3.upload_file(str(configPath), "phanbot", "buttongame.yaml")
#
#     def saveConfig(self) -> None:
#         """Writes the current game configuration and data to a file."""
#         with open("resources/buttongame.yaml", "w") as f:
#             yaml.dump(self.config, f)
#         return
#
#     def getActiveGuilds(self) -> list:
#         """Retrieve the guild IDs for all guilds currently playing the button game."""
#         guilds = self.config["guilds"]
#         activeGuilds = [
#             int(guildID)
#             for guildID, guildConfig in guilds.items()
#             if guildConfig["active"] is True
#         ]
#         return activeGuilds
#
#     def clearButtonGame(self, guildID: int) -> None:
#         """Resets a guild's game data to base values in preparation for a new game."""
#         guildConfig = self.config["guilds"][guildID]
#
#         # Reset general game values.
#         guildConfig["currentPoints"] = 0
#         guildConfig["currentWinnerID"] = 0
#         guildConfig["currentWinnerPoints"] = 0
#         guildConfig["timer"] = 0
#
#         # Set a new random game duration.
#         minDuration = guildConfig["minDuration"]
#         maxDuration = guildConfig["maxDuration"]
#         newDuration = random.randint(minDuration, maxDuration)
#
#         guildConfig["gameDuration"] = newDuration
#         guildConfig["timeRemaining"] = newDuration
#
#         # Reset the points and active status for every individual player.
#         players = guildConfig["players"]
#         for playerID, playerConfig in players.items():
#             playerConfig["currentPoints"] = 0
#             playerConfig["active"] = False
#
#         # Committing the changes to the main configuration.
#         guildConfig["players"] = players
#         self.config["guilds"][guildID] = guildConfig
#
#     def updatePlayerTimesPlayed(self, guildID: int) -> None:
#         """Increments the times-played counter for all participating players."""
#         players = self.config["guilds"][guildID]["players"]
#
#         for playerID, playerConfig in players.items():
#             timesPlayed = playerConfig["timesPlayed"]
#             timesPlayed += 1
#             playerConfig["timesPlayed"] = timesPlayed
#
#         self.config["guilds"][guildID]["players"] = players
#
#     def getGameMsgIDs(self) -> list[int]:
#         """Retrieves a list of Discord message IDs containing the button game itself."""
#         guildConfigs = self.config["guilds"]
#         gameMsgIDs = [
#             guildConfig["gameMsgID"] for guildID, guildConfig in guildConfigs.items()
#         ]
#         return gameMsgIDs
#
#     def getPlayerIDs(self, guildID: int) -> Optional[list]:
#         """Retrieves a sorted list of all active player IDs for a specific guild."""
#         playersConfig = self.config["guilds"][guildID]["players"]
#         activePlayers = [
#             playerID
#             for playerID, playerConfig in playersConfig.items()
#             if playerConfig["active"]
#         ]
#
#         if not activePlayers:
#             return None
#
#         return self.sortPlayerIDs(activePlayers, playersConfig)
#
#     @staticmethod
#     def sortPlayerIDs(playerIDs: list, playersConfig: dict) -> list:
#         """Sorts a player ID list first by last time played and then by current points."""
#         sortedPlayerIDs = sorted(
#             playerIDs, key=lambda x: playersConfig[x]["lastTimePlayed"]
#         )
#
#         sortedPlayerIDs = sorted(
#             sortedPlayerIDs,
#             key=lambda x: (playersConfig[x]["currentPoints"]),
#             reverse=True,
#         )
#
#         return sortedPlayerIDs
#
#     def checkPlayer(self, guildID: int, memberID: int) -> None:
#         """Checks whether a player has played the game before. If not, it adds them to the game."""
#         guildConfig = self.config["guilds"][guildID]
#         players = guildConfig["players"]
#
#         if memberID not in players:
#             players[memberID] = {
#                 "active": True,
#                 "currentPoints": 0,
#                 "highestPoints": 0,
#                 "lastTimePlayed": datetime.datetime.now(),
#                 "losses": 0,
#                 "timesChampion": 0,
#                 "timesPlayed": 0,
#                 "timesPushed": 0,
#                 "wins": 0,
#             }
#             guildConfig["players"] = players
#             self.config["guilds"][guildID] = guildConfig
#             self.saveConfig()
#
#     def getWinner(self, guildID: int) -> Optional[int]:
#         """Returns the current game leader for a specific guild."""
#         sortedPlayers = self.getPlayerIDs(guildID)
#         return sortedPlayers[0] if sortedPlayers else None
#
#     def updateWinner(self, guildID: int):
#         """Updates a guild's winner's win stat."""
#         players = self.config["guilds"][guildID]["players"]
#         winnerID = self.getWinner(guildID)
#
#         if winnerID is None:
#             return
#
#         winnerConfig = players[winnerID]
#         winnerConfig["wins"] += 1
#
#         players[winnerID] = winnerConfig
#         self.config["guilds"][guildID]["players"] = players
#
#     @staticmethod
#     def getChampion(
#             currentChampionID: Optional[int], playersConfig: dict
#     ) -> Optional[int]:
#         """Retrieves a guild's current champion based on the highest number of wins."""
#         playerWins = []
#         for playerID, playerConfig in playersConfig.items():
#             playerWins.append(playerConfig["wins"])
#         maxWins = max(playerWins)
#
#         potentialChampions = [
#             playerID
#             for playerID, playerConfig in playersConfig.items()
#             if playerConfig["wins"] == maxWins
#         ]
#
#         if not potentialChampions:
#             return None
#
#         if currentChampionID not in potentialChampions:
#             return potentialChampions[0]
#         else:
#             return currentChampionID
#
#     @staticmethod
#     async def updateRole(
#             memberID: int, roleID: int, guild: discord.Guild, add: bool
#     ) -> None:
#         """Adds or removes a role to or from a member in a given guild."""
#         try:
#             member = await guild.fetch_member(memberID)
#         except:
#             logger.error(
#                 f"Could not fetch the current champion: {{championID: {memberID}, guildID: {guild.id}}}"
#             )
#             return
#
#         try:
#             championRole = guild.get_role(roleID)
#         except:
#             championRole = None
#             logger.error(
#                 f"No champion role found: {{guildID: {guild.id}, roleID: {roleID}}}."
#             )
#
#         if add:
#             await member.add_roles(championRole)
#         else:
#             await member.remove_roles(championRole)
#
#     async def updateChampion(self, guildID: int) -> None:
#         """Determines and updates a guild's button game champion's stats and roles."""
#         guild = self.bot.get_guild(guildID)
#
#         guildConfig = self.config["guilds"][guildID]
#         previousChampionID = guildConfig["championID"]
#         championRoleID = guildConfig["championRoleID"]
#         players = guildConfig["players"]
#
#         newChampionID = self.getChampion(previousChampionID, players)
#
#         # Same winner
#         sameWinner = True if newChampionID == previousChampionID else False
#         if not sameWinner:
#             await self.updateRole(previousChampionID, championRoleID, guild, False)
#             await self.updateRole(newChampionID, championRoleID, guild, True)
#         championID = newChampionID if not sameWinner else previousChampionID
#
#         championConfig = players[championID]
#         championWins = championConfig["wins"]
#
#         if not sameWinner:
#             championTimesChamp = championConfig["timesChampion"]
#             championTimesChamp = championTimesChamp + 1 if championTimesChamp else 1
#             championConfig["timesChampion"] = championTimesChamp
#             players[championID] = championConfig
#
#         guildConfig["championWins"] = championWins
#         guildConfig["championID"] = championID
#
#         guildConfig["players"] = players
#         self.config["guilds"][guildID] = guildConfig
#
#     def startButtonGame(self, guildID: int):
#         """Activates the buttongame for a given guild."""
#         self.config["guilds"][guildID]["active"] = True
#
#     def stopButtonGame(self, guildID: int):
#         """Deactivates the buttongame for a given guild."""
#         self.config["guilds"][guildID]["active"] = False
#
#     async def finishButtonGame(self, guildID: int):
#         """Stops and restarts the button game once it has finished."""
#         self.stopButtonGame(guildID)
#         self.updatePlayerTimesPlayed(guildID)
#         self.updateWinner(guildID)
#
#         await self.updateChampion(guildID)
#         await self.sendFinishedEmbed(guildID)
#         await self.updateLeaderboardEmbed(guildID)
#
#         self.clearButtonGame(guildID)
#
#         self.saveConfig()
#         self.configUpload()
#
#         self.startButtonGame(guildID)
#
#     async def startTasks(self):
#         """Starts all the tasks for the button game."""
#         self.gameTimers.start()
#         self.pointsTracker.start()
#         self.updateEmbeds.start()
#         self.endChecker.start()
#         self.uploadConfig.start()
#
#     @commands.group()
#     async def buttongame(self, ctx):
#         """Initializes the buttongame command group."""
#         if ctx.invoked_subcommand is None:
#             return
#
#     @buttongame.command(name="test")
#     @commands.is_owner()
#     async def _test(self, ctx):
#         """Simple function used to test group command functionality."""
#         await ctx.send("test successful!")
#
#     @buttongame.command(name="create")
#     @commands.is_owner()
#     async def _create(self, ctx, channel: discord.TextChannel = None):
#         """Create the leaderboard and game embeds in a given channel."""
#         gameChannel = channel if channel else ctx.channel
#
#         leaderboardEmbed = discord.Embed(title="Button Game Leaderboard")
#         gameMessageText = ":zero:"
#
#         leaderboardMessage = await gameChannel.send(embed=leaderboardEmbed)
#         gameMessage = await gameChannel.send(content=gameMessageText)
#         await gameMessage.add_reaction("🔴")
#
#         guildConfigs = self.config["guilds"]
#         if ctx.guild.id not in guildConfigs:
#             guildConfig = {}
#         else:
#             guildConfig = guildConfigs[ctx.guild.id]
#
#         guildConfig["leaderboardMsgID"] = leaderboardMessage.id
#         guildConfig["gameMsgID"] = gameMessage.id
#         guildConfig["channelID"] = ctx.channel.id
#
#         guildConfigs[ctx.guild.id] = guildConfig
#         self.config["guilds"] = guildConfigs
#
#         self.saveConfig()
#
#     @buttongame.command(name="on")
#     @commands.is_owner()
#     async def _on(self, ctx):
#         """Manually starts the button game for a guild."""
#         await ctx.message.delete()
#
#         guildID = ctx.guild.id
#         self.config["guilds"][guildID]["active"] = True
#
#         self.saveConfig()
#
#         msg = await ctx.send("Button game activated!")
#         await msg.delete(delay=5)
#
#     @buttongame.command(name="off")
#     @commands.is_owner()
#     async def _off(self, ctx):
#         """Manually deactivates the button game for a guild."""
#         await ctx.message.delete()
#
#         guildID = ctx.guild.id
#         self.config["guilds"][guildID]["active"] = False
#         self.saveConfig()
#
#         msg = await ctx.send("Button game deactivated!")
#         await msg.delete(delay=5)
#
#     @buttongame.command(name="reset")
#     @commands.is_owner()
#     async def _reset(self, ctx):
#         """Manually resets the button game for a guild."""
#         await ctx.message.delete()
#
#         self.clearButtonGame(ctx.guild.id)
#
#         msg = await ctx.send("Button game has been reset!")
#         await msg.delete(delay=5)
#
#     @buttongame.command(name="activateTasks")
#     @commands.is_owner()
#     async def _activateTasks(self, ctx):
#         """Manually starts all non-active tasks."""
#         await ctx.message.delete()
#
#         try:
#             self.gameTimers.start()
#         except Exception as err:
#             logger.error(f"Could not start the gametimer task. {err}")
#
#         try:
#             self.pointsTracker.start()
#         except Exception as err:
#             logger.error(f"Could not start the pointsTracker task. {err}")
#
#         try:
#             self.updateEmbeds.start()
#         except Exception as err:
#             logger.error(f"Could not start the updateEmbeds task. {err}")
#
#         try:
#             self.endChecker.start()
#         except Exception as err:
#             logger.error(f"Could not start the endChecker task. {err}")
#
#         try:
#             self.gameTimers.start()
#         except Exception as err:
#             logger.error(f"Could not start the gametimer task. {err}")
#
#         response = await ctx.send("Tasks reactived!")
#         await response.delete(delay=5)
#
#     @buttongame.command(name="setminimum")
#     @commands.is_owner()
#     async def _setminimum(self, ctx, duration):
#         """Manually sets the minimum duration for games."""
#         await ctx.message.delete()
#
#         duration = int(duration)
#         self.config["guilds"][ctx.guild.id]["minDuration"] = duration
#         self.saveConfig()
#
#         msg = await ctx.send(f"Minimum duration set to {duration}s.")
#         await msg.delete(delay=5)
#
#     @buttongame.command(name="setmaximum")
#     @commands.is_owner()
#     async def _setmaximum(self, ctx, duration):
#         await ctx.message.delete()
#
#         duration = int(duration)
#         self.config["guilds"][ctx.guild.id]["maxDuration"] = duration
#         self.saveConfig()
#
#         msg = await ctx.send(f"Maximum duration set to {duration}s.")
#         await msg.delete(delay=5)
#
#     @buttongame.command(name="save")
#     @commands.is_owner()
#     async def _save(self, ctx):
#         """Manually saves, writes, and uploads the game data."""
#         await ctx.message.delete()
#
#         self.saveConfig()
#         self.configUpload()
#
#         msg = await ctx.send("Button game data saved!")
#         await msg.delete(delay=5)
#
#     @buttongame.command(name="status")
#     @commands.is_owner()
#     async def _status(self, ctx):
#         """Sends an embed detailing the status of all button game tasks."""
#         await ctx.message.delete()
#
#         taskEmojiPairs = {}
#
#         emoji = "✅" if self.gameTimers.is_running() else "❌"
#         taskEmojiPairs["Game Timer"] = emoji
#
#         emoji = "✅" if self.pointsTracker.is_running() else "❌"
#         taskEmojiPairs["Points Tracker"] = emoji
#
#         emoji = "✅" if self.updateEmbeds.is_running() else "❌"
#         taskEmojiPairs["Leaderboard Updater"] = emoji
#
#         emoji = "✅" if self.endChecker.is_running() else "❌"
#         taskEmojiPairs["End Checker"] = emoji
#
#         emoji = "✅" if self.uploadConfig.is_running() else "❌"
#         taskEmojiPairs["Config Uploader"] = emoji
#
#         taskNameString = ""
#         emojiNameString = ""
#         for taskName, emoji in taskEmojiPairs.items():
#             taskNameString += f"`{taskName}` \n"
#             emojiNameString += f"{emoji} \n"
#
#         embed = discord.Embed(tite="Button Game Tasks Status")
#         embed.set_author(name="Phan Bot", icon_url=self.embedLogoURL)
#         embed.add_field(name="Task Name", value=taskNameString)
#         embed.add_field(name="Status", value=emojiNameString)
#
#         await ctx.send(embed=embed)
#
#     @commands.Cog.listener()
#     async def on_ready(self):
#         """Starts the game automatically when the bot loads up."""
#         self.configDownload()
#
#         configPath = Path.cwd() / "resources" / "buttongame.yaml"
#         with open(str(configPath), "r") as f:
#             config = yaml.safe_load(f)
#
#         self.config = config
#
#         guilds = config["guilds"]
#         guildIDs = guilds.keys()
#
#         for guildID in guildIDs:
#             self.isCurrentlyProcessing[int(guildID)] = False
#
#         await self.startTasks()
#
#     @commands.command()
#     async def stats(self, ctx):
#         """Shows a member's various button game stats."""
#         author = ctx.author
#         authorID = ctx.author.id
#         authorPFPUrl = ctx.author.avatar_url
#         guildID = ctx.guild.id
#
#         try:
#             playerInfo = self.config["guilds"][guildID]["players"][authorID]
#         except ValueError:
#             logger.error(f"Could not find player {ctx.member.id=} in the game files.")
#             await ctx.send(content="Sorry, looks like you don't exist in my database.")
#             return
#
#         embed = discord.Embed(
#             title="Button Game Stats",
#         )
#         embed.set_thumbnail(url=authorPFPUrl)
#         embed.set_author(name=author, icon_url=authorPFPUrl)
#         embed.add_field(name="Highest Score", value=playerInfo["highestPoints"])
#         embed.add_field(name="Total Wins", value=playerInfo["wins"])
#         embed.add_field(name="Games Played", value=playerInfo["timesPlayed"])
#         embed.add_field(name="Times Pushed", value=playerInfo["timesPushed"])
#         embed.add_field(name="Times as Champion", value=playerInfo["timesChampion"])
#
#         await ctx.send(embed=embed)
#
#     async def updateLeaderboardEmbed(self, guildID: int):
#         """Creates and updates the leaderboard for the game."""
#         # Generate the strings to be used in the discord embed.
#         guild = self.bot.get_guild(guildID)
#         guildConfig = self.config["guilds"][guildID]
#         players = guildConfig["players"]
#
#         leaderboardEmbedID = guildConfig["leaderboardMsgID"]
#         buttonGameChannelID = guildConfig["channelID"]
#         buttonGameChannel = self.bot.get_channel(buttonGameChannelID)
#         leaderboardMsg = await buttonGameChannel.fetch_message(leaderboardEmbedID)
#
#         championID = guildConfig["championID"]
#         championWins = guildConfig["championWins"]
#
#         try:
#             champion = guild.get_member(championID)
#             championString = f"{champion}"[:-5]
#         except:
#             logger.error(f"No champion exists yet for {guildID=}.")
#             championString = "No One"
#
#         try:
#             championWinsString = f"{championWins} wins"
#         except:
#             logger.error("Could not find any champion wins in the game file.")
#             championWinsString = ":("
#
#         # Retrieve the current winner points.
#         playersIDs = self.getPlayerIDs(guildID)
#         currentWinnerID = playersIDs[0] if playersIDs else None
#
#         playersString = ""
#         pointsString = ""
#         # Generate strings for use with the leaderboard embed.
#         playerIDs = self.getPlayerIDs(guildID)
#         if playerIDs:
#             for playerID in playerIDs:
#                 player = guild.get_member(playerID)
#                 points = players[playerID]["currentPoints"]
#
#                 if playerID == currentWinnerID:
#                     playersString = f"{player.mention} 👑 \n{playersString}"
#                     pointsString = f"{points} pts \n{pointsString}"
#                 else:
#                     playersString = f"{playersString}{player.mention} \n"
#                     pointsString = f"{pointsString}{points} pts \n"
#         else:
#             playersString = "No one"
#             pointsString = ":("
#
#         # Edit the Leaderboard message with a new embed.
#         embed = discord.Embed(
#             title=f"Champion 👑👑👑 : {championString} with {championWinsString}",
#             color=0xFFFFFF,
#         )
#         embed.add_field(name="Player", value=playersString, inline=True)
#         embed.add_field(name="Points", value=pointsString)
#         embed.set_author(
#             name="Phan Bot Presents: The Button Game", icon_url=self.embedLogoURL
#         )
#
#         # Let the footer show the time remaining in HH:MM:SS format.
#         timeRemaining = guildConfig["timeRemaining"]
#         days, leftovers = divmod(timeRemaining, 86400)
#         timeFormat = datetime.timedelta(seconds=leftovers)
#
#         embed.set_footer(
#             text=f"Time Remaining: {days}d, {timeFormat}",
#         )
#
#         await leaderboardMsg.edit(embed=embed)
#
#     async def updatePointsEmbed(self, guildID: int):
#         """Updates the game message embed displaying the current point value."""
#         guildConfig = self.config["guilds"][guildID]
#
#         messageString = ""
#         currentPoints = guildConfig["currentPoints"]
#         buttonGameChannelID = guildConfig["channelID"]
#         buttonGameMessageID = guildConfig["gameMsgID"]
#         buttonGameChannel = self.bot.get_channel(buttonGameChannelID)
#         buttonGameMessage = await buttonGameChannel.fetch_message(buttonGameMessageID)
#
#         for digit in str(currentPoints):
#             digit = int(digit)
#             digitAsWord = num2words.num2words(digit)
#             messageString += f":{digitAsWord}:"
#
#         await buttonGameMessage.edit(content=messageString)
#
#     async def sendFinishedEmbed(self, guildID: int):
#         """Creates the embed indicating the end of the game."""
#         guildConfig = self.config["guilds"][guildID]
#         guild = self.bot.get_guild(guildID)
#
#         try:
#             winnerID = self.getWinner(guildID)
#             winnerConfig = guildConfig["players"][winnerID]
#             winner = guild.get_member(winnerID)
#             winnerPoints = winnerConfig["currentPoints"]
#             titleDesc = f"Total Points: {winnerPoints}"
#         except:
#             winner = None
#             titleDesc = None
#
#         channelID = guildConfig["channelID"]
#         channel = guild.get_channel(channelID)
#
#         if winner:
#             winnerPFPUrl = winner.avatar_url
#             embed = discord.Embed(
#                 title="Congratulations, we got a winner!!!👑",
#                 description=titleDesc,
#             )
#             embed.set_thumbnail(url=winnerPFPUrl)
#             embed.set_author(name=f"{winner}", icon_url=winnerPFPUrl)
#             embed.set_footer(text="Next game has now commenced!")
#             msg = await channel.send(content=f"{winner.mention}", embed=embed)
#         else:
#             embed = discord.Embed(
#                 title="Looks like there are no winners :( Maybe next time!"
#             )
#             embed.set_thumbnail(url=self.embedLogoURL)
#             embed.set_author(name="Phan Bot", icon_url=self.embedLogoURL)
#             embed.set_footer(text="Next game has now commenced!")
#             msg = await channel.send(embed=embed)
#
#         prevWinnerEmbedID = guildConfig["winnerMsgID"]
#         try:
#             winnerEmbed = await channel.fetch_message(prevWinnerEmbedID)
#             await winnerEmbed.delete()
#         except:
#             logger.error(
#                 f"Could not retrieve previous winner announcement for {guildID=}. Continuing..."
#             )
#
#         prevWinnerEmbedID = msg.id
#         guildConfig["winnerMsgID"] = prevWinnerEmbedID
#         self.config["guilds"][guildID] = guildConfig
#
#     @tasks.loop(seconds=1.0)
#     async def gameTimers(self):
#         """Used to keep track of the game time in the background."""
#         # Increment game timers for all guilds playing the button game.
#         try:
#             guildIDs = self.getActiveGuilds()
#
#             for guildID in guildIDs:
#                 guildConfig = self.config["guilds"][guildID]
#
#                 timer = guildConfig["timer"]
#                 timer = timer if timer else 0
#                 timer += 1
#                 guildConfig["timer"] = timer
#
#                 timeRemaining = guildConfig["timeRemaining"]
#                 timeRemaining = timeRemaining if timeRemaining else 0
#
#                 # Prevents timeRemaining from ever going into the negatives.
#                 if timeRemaining == 0:
#                     continue
#                 else:
#                     timeRemaining -= 1
#
#                 guildConfig["timeRemaining"] = timeRemaining
#
#                 self.config["guilds"][guildID] = guildConfig
#         except Exception as err:
#             logger.error(f"An error occurred in the gameTimers task. Error: \n {err}")
#
#     @tasks.loop(seconds=3.0)
#     async def pointsTracker(self):
#         try:
#             guildIDs = self.getActiveGuilds()
#
#             for guildID in guildIDs:
#                 guildConfig = self.config["guilds"][guildID]
#                 currentPoints = guildConfig["currentPoints"]
#                 currentPoints = currentPoints + 1 if currentPoints else 1
#                 guildConfig["currentPoints"] = currentPoints
#
#                 self.config["guilds"][guildID] = guildConfig
#
#                 await self.updatePointsEmbed(guildID)
#         except Exception as err:
#             logger.error(f"An error occurred in the updateEmbeds task. Error: \n {err}")
#
#     @commands.Cog.listener()
#     async def on_raw_reaction_add(self, payload):
#         """Main game loop."""
#         # Need to create a check to ensure the reaction is for the game.
#         isNotBot = True if payload.user_id != self.bot.user.id else False
#         isEmoji = True if str(payload.emoji) == "🔴" else False
#
#         gameMessageIDs = self.getGameMsgIDs()
#         isGameMessage = True if payload.message_id in gameMessageIDs else False
#
#         valid = isNotBot and isEmoji and isGameMessage
#         if not valid:
#             return
#
#         guildID = payload.guild_id
#         if self.isCurrentlyProcessing[guildID]:
#             return
#
#         self.isCurrentlyProcessing[payload.guild_id] = True
#
#         # Retrieve information from the payload.
#         guildID = payload.guild_id
#         playerID = payload.member.id
#         gameChannelID = payload.channel_id
#         gameChannel = self.bot.get_channel(gameChannelID)
#         gameMessageID = payload.message_id
#         gameMessage = await gameChannel.fetch_message(gameMessageID)
#
#         guildConfig = self.config["guilds"][guildID]
#
#         await gameMessage.clear_reactions()
#
#         # Add the player into the game if they are new.
#         self.checkPlayer(guildID, playerID)
#
#         # Check if they clicked on the same amount of points.
#         currentPoints = guildConfig["currentPoints"]
#         playerInfo = self.config["guilds"][guildID]["players"][playerID]
#         playerPoints = playerInfo["currentPoints"]
#
#         if currentPoints == playerPoints:
#             currentPoints = 0
#
#         # Set player information
#         timesPushed = playerInfo["timesPushed"]
#         timesPushed = timesPushed + 1 if timesPushed else 1
#
#         playerInfo["currentPoints"] = currentPoints
#         playerInfo["lastTimePlayed"] = datetime.datetime.now()
#         playerInfo["timesPushed"] = timesPushed
#         playerInfo["active"] = True
#
#         # Check if this was the user's highest score. If yes, overwrite it.
#         highestScore = playerInfo["highestPoints"]
#         if currentPoints > highestScore:
#             playerInfo["highestPoints"] = currentPoints
#
#         self.config["guilds"][guildID]["players"][playerID] = playerInfo
#
#         # Reset the points and reset the reaction.
#         guildConfig["currentPoints"] = 0
#         self.config["guilds"][guildID] = guildConfig
#
#         await self.updateLeaderboardEmbed(guildID)
#         await self.updatePointsEmbed(guildID)
#
#         self.isCurrentlyProcessing[guildID] = False
#         await gameMessage.add_reaction("🔴")
#
#     @tasks.loop(seconds=10.0)
#     async def updateEmbeds(self):
#         """Updates the points message."""
#         try:
#             guildIDs = self.getActiveGuilds()
#             for guildID in guildIDs:
#                 await self.updateLeaderboardEmbed(guildID)
#         except Exception as err:
#             logger.error(f"An error occurred in the updateEmbeds task. Error: \n {err}")
#
#     @tasks.loop(seconds=3.0)
#     async def endChecker(self):
#         """Continuously checks to see if the current game has ended for each guild."""
#         try:
#             guildIDs = self.getActiveGuilds()
#             for guildID in guildIDs:
#                 guildConfig = self.config["guilds"][guildID]
#                 timeRemaining = guildConfig["timeRemaining"]
#                 if timeRemaining <= 0:
#                     await self.finishButtonGame(guildID)
#         except Exception as err:
#             logger.error(f"An error occurred in the endChecker task. Error: \n {err}")
#
#     @tasks.loop(minutes=10)
#     async def uploadConfig(self):
#         """Uploads the game data every so often to AWS."""
#         try:
#             self.saveConfig()
#             self.configUpload()
#         except Exception as err:
#             logger.error(f"An error occured int he uploadConfig task. Error: \n {err}")

#
# def setup(bot):
#     bot.add_cog(ButtonGame(bot))
