import datetime
import logging
import re
import time
from pathlib import Path
from typing import Optional

import discord
import requests
import yaml
from discord.ext import commands, tasks

from helpers import logoURL

logger = logging.getLogger("main.twitch")


class TwitchStreamNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logoURL = logoURL
        self.configPath = str(Path.cwd() / "resources" / "twitchstreams.yaml")
        self.authUrl = "https://id.twitch.tv/oauth2/token"
        self.clientID = "6avjizucskdltven7u0uwczle9e9j8"
        self.clientSecret = "g7gpwv165dq92wsns844sibv72gwn7"
        self.authPerms = {
            "client_id": self.clientID,
            "client_secret": self.clientSecret,
            "grant_type": "client_credentials",
        }
        self.tokenExpirationLength = 0
        self.lastAuthCallTime = None
        self.access_token = None
        self.config = None

    def setConfig(self):
        with open(self.configPath, "r") as f:
            config = yaml.safe_load(f)
        self.config = config

    def updateConfigFile(self):
        with open(self.configPath, "w") as f:
            yaml.dump(self.config, f)

    def getGuildIDs(self) -> Optional[list]:
        try:
            guildIDs = list(self.config["guilds"].keys())
            return guildIDs
        except:
            logger.error("No guilds found in the Twitch Streams config file.")
            return None

    def checkGuild(self, guildID: int):
        try:
            guildConfig = self.config["guilds"][guildID]
        except KeyError:
            self.config["guilds"][guildID] = {}

    def getStreamers(self, guildID: int) -> Optional[list]:
        try:
            streamers = list(self.config["guilds"][guildID]["streamers"].keys())
            return streamers
        except KeyError:
            return None

    def replaceUrlDimensions(self, oldURL: str, width: int, height: int) -> str:
        newURL = re.sub(r"{width}", str(width), oldURL)
        newURL = re.sub(r"{height}", str(height), newURL)

        return newURL

    def validToken(self):
        if self.lastAuthCallTime:
            timeElapsed = datetime.datetime.now() - self.lastAuthCallTime
            timeElapsed = timeElapsed.seconds
        else:
            timeElapsed = 0

        if timeElapsed >= self.tokenExpirationLength:
            AuthorizationCall = requests.post(url=self.authUrl, params=self.authPerms)
            self.lastAuthCallTime = datetime.datetime.now()
            self.access_token = AuthorizationCall.json()["access_token"]
            self.tokenExpirationLength = AuthorizationCall.json()["expires_in"]

        return False if not self.access_token else True

    @commands.group()
    async def twitch(self, ctx):
        if not ctx.invoked_subcommand:
            return

    @twitch.command(name="add")
    @commands.is_owner()
    async def _add(self, ctx, twitchUsername: str):
        guildID = ctx.guild.id

        self.checkGuild(guildID)
        self.config["guilds"][guildID]["streamers"][twitchUsername.lower()] = {
            "live": False,
            "lastNotification": None,
        }
        self.updateConfigFile()

        await ctx.send(f"Streamer `{twitchUsername}` successfully added!")

    @twitch.command(name="remove")
    @commands.is_owner()
    async def _remove(self, ctx, twitchUsername: str):
        guildID = ctx.guild.id
        self.checkGuild(guildID)

        try:
            self.config["guilds"][guildID]["streamers"].pop(twitchUsername)
            self.updateConfigFile()

            await ctx.send(f"Streamer `{twitchUsername}` successfully removed!")
        except:
            await ctx.send(f"No such streamer found for guild {guildID}.")

    @twitch.command(name="setchannel")
    @commands.is_owner()
    async def _setchannel(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel

        channelID = channel.id
        guildID = ctx.guild.id
        self.checkGuild(guildID)

        self.config["guilds"][guildID]["channelID"] = channelID
        self.updateConfigFile()

        await ctx.send(
            f"Channel {channel} has been set to the stream notification channel."
        )

    @twitch.command(name="setrole")
    @commands.is_owner()
    async def _setrole(self, ctx, role: discord.Role):
        guildID = ctx.guild.id
        self.checkGuild(guildID)

        roleID = role.id
        self.config["guilds"][guildID]["roleID"] = roleID
        self.updateConfigFile()

        await ctx.send(f"Role {role} has been set to the stream notification role.")

    @twitch.command(name="streamers")
    @commands.is_owner()
    async def _streamers(self, ctx):
        guildID = ctx.guild.id
        self.checkGuild(guildID)

        if streamers := self.getStreamers(guildID):
            streamerMsg = ", ".join(streamers)
            await ctx.send(f"Current list of streamers: {streamerMsg}")
        else:
            await ctx.send(f"No streamers have been set up for this server.")

    @tasks.loop(seconds=60)
    async def checkTwitch(self):
        if not self.validToken():
            pass

        headers = {
            "Client-Id": self.clientID,
            "Authorization": f"Bearer {self.access_token}",
        }

        newChanges = False
        if guildIDs := self.getGuildIDs():
            for guildID in guildIDs:
                self.checkGuild(guildID)
                guildConfig = self.config["guilds"][guildID]

                try:
                    channelID = guildConfig["channelID"]
                    roleID = guildConfig["roleID"]
                except KeyError:
                    logger.error(
                        f"No channel or role has been set for guild {guildID}."
                    )
                    return

                guild = self.bot.get_guild(guildID)
                channel = guild.get_channel(channelID)
                role = guild.get_role(roleID)

                streamers = self.getStreamers(guildID)
                searchParams = {"user_login": streamers}
                r = requests.get(
                    "https://api.twitch.tv/helix/streams",
                    headers=headers,
                    params=searchParams,
                )

                try:
                    data = r.json()["data"]
                except Exception as err:
                    logger.error(f"Something went wrong! Error: {err}")
                    return

                verifiedStreamers = []
                if data:
                    for stream in data:
                        streamer = stream["user_login"].lower()
                        verifiedStreamers.append(streamer)
                        streamerConfig = guildConfig["streamers"][streamer.lower()]

                        status = streamerConfig["live"]
                        if not status:
                            self.config["guilds"][guildID]["streamers"][streamer][
                                "live"
                            ] = True

                            lastNotificationTime = streamerConfig["lastNotification"]
                            currentTime = datetime.datetime.now()
                            if lastNotificationTime:
                                timeDiff = currentTime - lastNotificationTime
                                if timeDiff.total_seconds() < 7200:
                                    continue

                            self.config["guilds"][guildID]["streamers"][streamer][
                                "lastNotification"
                            ] = currentTime

                            game = stream["game_name"]
                            rawUrl = stream["thumbnail_url"]
                            logger.debug(f"{rawUrl=}")
                            newUrl = (
                                    self.replaceUrlDimensions(rawUrl, 474, 267)
                                    + f"?{int(time.time())}"
                            )
                            logger.debug(f"{newUrl=}")
                            title = stream["title"]
                            if "please ignore" in title:
                                continue

                            embed = discord.Embed(
                                title=f"{streamer} is now streaming!",
                                description=f"Currently Playing: `{game}` \n Title: `{title}`",
                                color=0x9147FF,
                            )
                            embed.set_author(name="Phan Bot", icon_url=self.logoURL)
                            embed.set_thumbnail(url="https://i.imgur.com/RBXNWC5.jpg")
                            embed.set_image(url=newUrl)
                            embed.add_field(
                                name="Check them out here!",
                                value=f"https://twitch.tv/{streamer}",
                            )

                            await channel.send(content=f"{role.mention}", embed=embed)

                            newChanges = True
                for streamer, streamerConfig in self.config["guilds"][guildID][
                    "streamers"
                ].items():
                    if (
                            streamer not in verifiedStreamers
                            and streamerConfig["live"] == True
                    ):
                        newChanges = True
                        self.config["guilds"][guildID]["streamers"][streamer][
                            "live"
                        ] = False
        if newChanges:
            self.updateConfigFile()

    @commands.Cog.listener()
    async def on_ready(self):
        self.setConfig()
        self.checkTwitch.start()


async def setup(bot):
    await bot.add_cog(TwitchStreamNotifier(bot))
