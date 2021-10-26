import datetime
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import discord
import requests
import yaml
from discord.ext import commands, tasks

from helpers import makeSimpleTextEmbed

logger = logging.getLogger("main.twitch")


class Twitch(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.config = self.getTwitchConfig()
        self.clientID = None
        self.clientSecret = None
        self.tokenExpirationLength = None
        self.lastAuthCallTime = None
        self.access_token = None

    async def cog_check(self, ctx) -> None:
        """Check to see if the user is has administrative privileges."""
        isAdministrator = ctx.author.guild_permissions.administrator
        return isAdministrator

    @commands.group()
    async def twitch(self, ctx) -> None:
        """Initializes the twitch command group."""
        logger.info(f"{ctx.author} used the twitch command.")
        if not ctx.invoked_subcommand:
            message = self.makeTwitchOverviewEmbed(ctx.guild)
            await ctx.send(embed=message)

    @twitch.group(name='streamers')
    async def twitch_streamers(self, ctx) -> None:
        """Initializes the twitch streamers subcommand group."""
        logger.info(f"{ctx.author} used the twitch streamers command.")
        if not ctx.invoked_subcommand:
            message = self.makeTwitchStreamerListEmbed(ctx.guild)
            await ctx.send(embed=message)

    @twitch_streamers.command(name='add')
    async def twitch_streamers_add(self, ctx, twitchUsername: str) -> None:
        """Adds a twitch streamer to a guild's notification list."""
        logger.info(f"{ctx.author} used the twitch streamers add command.")

        guild = ctx.guild
        self.addStreamer(guild, twitchUsername.lower())

        logger.info(f"Streamer {twitchUsername} added to {ctx.guild.name}'s streamer list.")
        confirmation = makeSimpleTextEmbed(f"Streamer {twitchUsername} successfully added!")
        await ctx.send(embed=confirmation)

    @twitch_streamers.command(name="remove")
    async def twitch_streamers_remove(self, ctx, twitchUsername: str) -> None:
        """Removes a twitch streamer to a guild's notification list."""
        logger.info(f"{ctx.author} used the twitch streamers remove command.")

        guild = ctx.guild
        try:
            self.removeStreamer(guild, twitchUsername)
            logger.info(f"Streamer {twitchUsername} removed from {ctx.guild.name}'s streamer list.")
            confirmation = makeSimpleTextEmbed(f"Streamer {twitchUsername} successfully removed!")
            await ctx.send(embed=confirmation)
        except KeyError:
            logger.info(f"Unable to find {twitchUsername} on {ctx.guild.name}'s streamer list.")
            errorMessage = makeSimpleTextEmbed(f"Streamer {twitchUsername} is not on the streamer list.")
            await ctx.send(embed=errorMessage)

    @twitch.group(name='channel')
    async def twitch_channel(self, ctx) -> None:
        """Initializes the twitch channel subcommand group."""
        logger.info(f"{ctx.author} used the twitch channel command.")
        if ctx.invoked_subcommand is None:
            notificationChannel = self.getTwitchChannel(ctx.guild)
            match notificationChannel:
                case None:
                    message = makeSimpleTextEmbed('No channel has been set for the arcdps update notifier.')
                case _:
                    message = makeSimpleTextEmbed(
                        f'The arcdps update notification channel is currently set to {notificationChannel.mention}')
            await ctx.send(embed=message)

    @twitch_channel.command(name="set")
    async def twitch_channel_set(self, ctx, channel: discord.TextChannel = None) -> None:
        """Sets the twitch notification channel for a guild."""
        logger.info(f"{ctx.author} used the twitch channel set command.")
        if not channel:
            channel = ctx.channel
        self.setTwitchChannel(ctx.guild, channel.id)
        self.enableTwitch(ctx.guild)

        logger.info(f"")
        confirmationMessage = makeSimpleTextEmbed(
            f'The twitch notification channel has been set to {channel.mention}.')
        await ctx.send(embed=confirmationMessage)

    @twitch.group(name='role')
    async def twitch_role(self, ctx) -> None:
        """Initializes the twitch role subcommand group."""
        logger.info(f"{ctx.author} used the twitch role command.")
        if ctx.invoked_subcommand is None:
            notificationRole = self.getTwitchRole(ctx.guild)
            match notificationRole:
                case None:
                    message = makeSimpleTextEmbed('No role has been set for the twitch update notifier.')
                case _:
                    message = makeSimpleTextEmbed(
                        f'The twitch update notification role is currently set to {notificationRole.mention}')
            await ctx.send(embed=message)

    @twitch_role.command(name='set')
    async def twitch_role_set(self, ctx, role: discord.Role) -> None:
        """Sets the twitch notification role for a guild."""
        logger.info(f"{ctx.author} used the twitch role set command.")
        self.setTwitchRole(ctx.guild, role.id)

        logger.info(f"The twitch notification role for {ctx.guild.name} has been set to {role.name}.")
        confirmationMessage = makeSimpleTextEmbed(
            f'The twitch notification role has been set to {role.mention}.')
        await ctx.send(embed=confirmationMessage)

    @twitch_role.command(name='remove')
    async def twitch_role_remove(self, ctx) -> None:
        """Removes the twitch notification role for a guild."""
        logger.info(f"{ctx.author} used the twitch role remove command.")
        self.setTwitchRole(ctx.guild, None)

        logger.info(f"The twitch notification role for {ctx.guild.name} has been removed.")
        confirmationMessage = makeSimpleTextEmbed(
            f'The twitch notification role has been removed.')
        await ctx.send(embed=confirmationMessage)

    @twitch.command(name='enable')
    async def twitch_enable(self, ctx) -> None:
        """Enables the twitch notifier for a guild."""
        logger.info(f"{ctx.author} used the twitch enable command.")

        self.enableTwitch(ctx.guild)
        confirmationMessage = makeSimpleTextEmbed('The twitch notifier has been enabled!')
        await ctx.send(embed=confirmationMessage)

    @twitch.command(name='disable')
    async def twitch_disable(self, ctx) -> None:
        """Disables the twitch notifier for a guild."""
        logger.info(f"{ctx.author} used the twitch disable command.")

        self.disableTwitch(ctx.guild)
        confirmationMessage = makeSimpleTextEmbed('The twitch notifier has been disabled!')
        await ctx.send(embed=confirmationMessage)

    @tasks.loop(seconds=60)
    async def checkTwitch(self) -> None:
        if not self.validToken():
            self.createNewTwitchToken()

        guilds = self.getEnabledGuilds()
        for guild in guilds:
            liveStreamers = []

            streamerList = self.getStreamers(guild)
            liveData = self.getLiveTwitchData(streamerList)
            if liveData:
                for streamData in liveData:
                    streamer = streamData['user_login'].lower()
                    liveStreamers.append(streamer)
                    await self.alertGuild(guild, streamData)

            self.cleanInactiveStreamers(guild, liveStreamers)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.cacheTwitchEnvironmentVariables()
        self.createNewTwitchToken()

        self.checkTwitch.start()

    def cacheTwitchEnvironmentVariables(self) -> None:
        """Caches the required environment variables for HTTP requests to Twitch."""
        self.clientID = os.environ['TWITCH_CLIENT_ID']
        self.clientSecret = os.environ['TWITCH_CLIENT_SECRET']

    @staticmethod
    def getTwitchConfig() -> dict:
        """Returns the twitch configurations for all guilds."""
        configPath = Path.cwd() / 'configurations' / 'twitch.yaml'
        with open(configPath, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def saveTwitchConfig(self) -> None:
        """Saves the cached twitch configuration for all guilds."""
        configPath = Path.cwd() / 'configurations' / 'twitch.yaml'

        logger.info('Saving configuration to file...')
        with open(configPath, 'w') as f:
            yaml.dump(self.config, f)
        logger.info('Configuration saved!')

    def getGuildTwitchConfig(self, guild: discord.Guild) -> dict:
        """Returns the twitch configuration for a given guild."""
        try:
            assert guild.id in self.config['guilds'].keys()
        except AssertionError:
            self.initializeGuildTwitchConfig(guild)
        finally:
            return self.config['guilds'][guild.id]

    def initializeGuildTwitchConfig(self, guild: discord.Guild) -> None:
        """Initializes a basic twitch configuration for a new guild."""
        self.config['guilds'][guild.id] = {
            'enabled': False,
            'channelID': None,
            'roleID': None,
            'streamers': {},
        }
        self.saveTwitchConfig()

    def getGuildTwitchEnabledStatus(self, guild: discord.Guild) -> bool:
        """Determines if a guild has the twitch module enabled."""
        guildConfig = self.getGuildTwitchConfig(guild)
        return guildConfig['enabled']

    def enableTwitch(self, guild: discord.Guild) -> None:
        """Enables the twitch notifier for a given guild."""
        guildConfig = self.getGuildTwitchConfig(guild)
        guildConfig['enabled'] = True
        self.saveTwitchConfig()

    def disableTwitch(self, guild: discord.Guild) -> None:
        """Disables the twitch notifier for a given guild."""
        guildConfig = self.getGuildTwitchConfig(guild)
        guildConfig['enabled'] = False
        self.saveTwitchConfig()

    def getEnabledGuilds(self) -> list[discord.Guild]:
        """Returns a list of guilds that have the twitch notifier enabled."""
        config = self.getTwitchConfig()
        guildsConfig = config['guilds']

        enabledGuilds = []
        for guildID, guildConfig in guildsConfig.items():
            enabled = guildConfig['enabled']
            if enabled:
                guild = self.bot.get_guild(guildID)
                enabledGuilds.append(guild)

        return enabledGuilds

    def getTwitchChannel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Returns a guild's twitch notification channel."""
        guildConfig = self.getGuildTwitchConfig(guild)
        channelID = guildConfig['channelID']

        match channelID:
            case None:
                return None
            case _:
                channel = self.bot.get_channel(channelID)
                return channel

    def setTwitchChannel(self, guild: discord.Guild, channelID: int) -> None:
        """Sets the twitch notification channel for a given guild."""
        self.config['guilds'][guild.id]['channelID'] = channelID
        self.saveTwitchConfig()

    def getTwitchRole(self, guild: discord.Guild) -> Optional[discord.Role]:
        """Returns a guild's twitch notification role."""
        guildConfig = self.getGuildTwitchConfig(guild)
        roleID = guildConfig['roleID']

        match roleID:
            case None:
                return None
            case _:
                role = guild.get_role(roleID)
                return role

    def setTwitchRole(self, guild: discord.Guild, roleID: int | None) -> None:
        """Sets the twitch notification role for a given guild."""
        self.config['guilds'][guild.id]['roleID'] = roleID
        self.saveTwitchConfig()

    def getStreamers(self, guild: discord.Guild) -> list[str]:
        """Returns a list of streamer names that a given guild is notified of."""
        guildConfig = self.getGuildTwitchConfig(guild)
        streamers = list(guildConfig['streamers'].keys())
        return streamers

    def addStreamer(self, guild: discord.Guild, twitchUsername: str) -> None:
        """Adds a streamer to a given guild's streamer list."""
        guildConfig = self.getGuildTwitchConfig(guild)
        guildConfig['streamers'][twitchUsername] = {
            'lastTimePinged': None,
            'currentlyLive': False,
        }
        self.saveTwitchConfig()

    def removeStreamer(self, guild: discord.Guild, twitchUsername: str) -> None:
        """Removes a streamer from a given guild's streamer list."""
        guildConfig = self.getGuildTwitchConfig(guild)
        del guildConfig['streamers'][twitchUsername]
        self.saveTwitchConfig()

    def getStreamerCachedLiveStatus(self, guild: discord.Guild, twitchUsername: str) -> bool:
        """Returns a streamer's cached live status for a given guild."""
        guildConfig = self.getGuildTwitchConfig(guild)
        streamerConfig = guildConfig['streamers'][twitchUsername]
        return streamerConfig['currentlyLive']

    def setStreamerToLive(self, guild: discord.Guild, twitchUsername: str) -> None:
        """Sets a streamer to show as currently live in the configuration."""
        guildConfig = self.getGuildTwitchConfig(guild)
        streamerConfig = guildConfig['streamers'][twitchUsername]
        streamerConfig['currentlyLive'] = True

    def setStreamerToInactive(self, guild: discord.Guild, twitchUsername: str) -> None:
        """Sets a streamer to show as currently inactive in the configuration."""
        guildConfig = self.getGuildTwitchConfig(guild)
        streamerConfig = guildConfig['streamers'][twitchUsername]
        streamerConfig['currentlyLive'] = False

    def getStreamerLastTimePinged(self, guild: discord.Guild, twitchUsername: str) -> datetime:
        """Returns a streamer's last time pinged for a given guild."""
        guildConfig = self.getGuildTwitchConfig(guild)
        streamerConfig = guildConfig['streamers'][twitchUsername]
        return streamerConfig['lastTimePinged']

    def setStreamerLastTimePinged(self, guild: discord.Guild, twitchUsername: str) -> None:
        """Sets the last time pinged value for a streamer for a give guild."""
        guildConfig = self.getGuildTwitchConfig(guild)
        streamerConfig = guildConfig['streamers'][twitchUsername]
        streamerConfig['lastTimePinged'] = datetime.now()

    def getCachedLiveStreamers(self, guild: discord.Guild) -> list[str]:
        """Returns a list of streamers marked as live in the cached configuration."""
        guildConfig = self.getGuildTwitchConfig(guild)
        streamersConfig = guildConfig['streamers']

        cachedLiveStreamers = []
        for streamer, streamerConfig in streamersConfig.items():
            live = streamerConfig['currentlyLive']
            if live:
                cachedLiveStreamers.append(streamer)

        return cachedLiveStreamers

    def alreadyPinged(self, guild, twitchUsername: str) -> bool:
        """Checks to see if there was already a ping for a given streamer a certain amount of time ago."""
        delaySeconds = 7200

        lastTimePinged = self.getStreamerLastTimePinged(guild, twitchUsername)
        currentTime = datetime.now()

        timeDiff = currentTime - lastTimePinged
        timeDiffSeconds = timeDiff.total_seconds()
        if timeDiffSeconds > delaySeconds:
            return True
        else:
            return False

    async def alertGuild(self, guild, streamData: dict) -> None:
        """Alerts a guild of a live streamer."""
        streamer = streamData['user_login'].lower()
        streamerWasLive = self.getStreamerCachedLiveStatus(guild, streamer)

        if not streamerWasLive:
            self.setStreamerToLive(guild, streamer)
            if self.alreadyPinged(guild, streamer):
                return

            twitchMessage = self.makeTwitchStreamEmbed(streamData)
            twitchChannel = self.getTwitchChannel(guild)
            twitchRole = self.getTwitchRole(guild)

            if twitchRole:
                await twitchChannel.send(content=twitchRole.mention, embed=twitchMessage)
            else:
                await twitchChannel.send(embed=twitchMessage)

            self.setStreamerLastTimePinged(guild, streamer)

    def cleanInactiveStreamers(self, guild, liveStreamers: list[str]) -> None:
        """Mark cached live streamers as inactive if they do not appear in the API call for live streamers."""
        cachedLiveStreamers = self.getCachedLiveStreamers(guild)
        for streamer in cachedLiveStreamers:
            if streamer not in liveStreamers:
                self.setStreamerToInactive(guild, streamer)

    def makeTwitchStreamEmbed(self, streamData: dict) -> discord.Embed:
        """Makes an embed containing information about a live twitch stream."""
        streamer = streamData['user_login'].lower()
        title = streamData['title']
        game = streamData['game_name']
        thumbnailUrl = streamData['thumbnail_url']
        modifiedThumbnailUrl = self.substituteDimensions(thumbnailUrl, 474, 267)

        embed = discord.Embed(
            title=f"{streamer} is now live!",
            description=f"Currently Playing: `{game}` \n Title: `{title}`",
            color=0x9147FF,
        )
        embed.set_author(name="Phan Bot", icon_url='https://i.imgur.com/CkAoqD2.png')
        embed.set_thumbnail(url="https://i.imgur.com/RBXNWC5.jpg")
        embed.set_image(url=modifiedThumbnailUrl)
        embed.add_field(
            name="Check them out here!",
            value=f"https://twitch.tv/{streamer}",
        )

        return embed

    def makeTwitchOverviewEmbed(self, guild: discord.Guild) -> discord.Embed:
        """Creates an embed containing an overview of all the guild's twitch configurations."""
        enabled = self.getGuildTwitchEnabledStatus(guild)
        role = self.getTwitchRole(guild)
        channel = self.getTwitchChannel(guild)

        enabledSymbol = '✅' if enabled else '❌'

        embed = discord.Embed(title="Twitch Stream Alerts")
        embed.set_author(name="Phan Bot", icon_url="https://i.imgur.com/CkAoqD2.png")
        embed.add_field(name="Channel", value=f"{channel.mention}")
        if role:
            embed.add_field(name="Role", value=f"{role.mention}")
        else:
            embed.add_field(name="Role", value=f"None")
        embed.add_field(name="Enabled", value=enabledSymbol)

        return embed

    def makeTwitchStreamerListEmbed(self, guild: discord.Guild) -> discord.Embed:
        """Creates an embed containing a list of all streamers on a guild's notification list."""
        streamers = self.getStreamers(guild)
        streamersText = '\n'.join(streamers) if streamers != [] else 'None'

        embed = discord.Embed(title='Streamer List', description=streamersText)
        embed.set_author(name="Phan Bot", icon_url="https://i.imgur.com/CkAoqD2.png")

        return embed

    @staticmethod
    def substituteDimensions(url: str, width: int, height: int) -> str:
        """Substitute the {width} and {height} keywords in a streamer's thumbnail url with actual values."""
        newURL = re.sub(r"{width}", str(width), url)
        newURL = re.sub(r"{height}", str(height), newURL)
        return newURL

    def getAuthorization(self) -> requests.Response:
        """Retrieves authorization data for Twitch API calls."""
        authUrl = "https://id.twitch.tv/oauth2/token"
        authPerms = {
            "client_id": self.clientID,
            "client_secret": self.clientSecret,
            "grant_type": "client_credentials",
        }
        authCall = requests.post(url=authUrl, params=authPerms)
        self.lastAuthCallTime = datetime.now()
        return authCall

    def createNewTwitchToken(self) -> None:
        """Creates a new twitch token from an authorization call."""
        authCall = self.getAuthorization()
        self.access_token = authCall.json()['access_token']
        self.tokenExpirationLength = authCall.json()['expires_in']

    def validToken(self) -> bool:
        """Determines if the cached twitch api token is valid."""
        timeElapsed = datetime.now() - self.lastAuthCallTime
        timeElapsedSeconds = timeElapsed.seconds

        if timeElapsedSeconds >= self.tokenExpirationLength:
            return False
        else:
            return True

    def getLiveTwitchData(self, streamers: list[str]) -> Optional[dict]:
        """Returns a dictionary containing data on the live streams of a list of streamers."""
        headers = {
            "Client-Id": self.clientID,
            "Authorization": f"Bearer {self.access_token}",
        }
        searchParams = {"user_login": streamers}

        r = requests.get(
            "https://api.twitch.tv/helix/streams",
            headers=headers,
            params=searchParams,
        )

        try:
            data = r.json()["data"]
            return data
        except Exception as err:
            logger.error(f"Something went wrong! Error: {err}")
            return None


def setup(bot):
    bot.add_cog(Twitch(bot))
