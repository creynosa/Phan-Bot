import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import discord
import requests
import yaml
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from requests.models import HTTPError

from helpers import makeSimpleTextEmbed
from main import isTesting

logger = logging.getLogger("main.arcdps")


class Arcdps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.getArcdpsConfig()

    async def cog_check(self, ctx) -> None:
        """Check to see if the user is has administrative privileges."""
        isAdministrator = ctx.author.guild_permissions.administrator
        return isAdministrator

    @commands.group()
    async def arcdps(self, ctx):
        """Initializes the arcdps command group."""
        logger.info(f"{ctx.author} used the arcdps command.")
        if ctx.invoked_subcommand is None:
            message = self.makeArcdpsOverviewEmbed(ctx.guild)
            await ctx.send(embed=message)

    @arcdps.group(name='channel')
    async def arcdps_channel(self, ctx):
        """Initializes the arcdps channel subcommand group."""
        logger.info(f"{ctx.author.name} used the arcdps channel command.")
        if ctx.invoked_subcommand is None:
            notificationChannel = self.getGuildArcdpsChannel(ctx.guild)
            match notificationChannel:
                case None:
                    message = makeSimpleTextEmbed('No channel has been set for the arcdps update notifier.')
                case _:
                    message = makeSimpleTextEmbed(
                        f'The arcdps update notification channel is currently set to {notificationChannel.mention}')
            await ctx.send(embed=message)

    @arcdps_channel.command(name='set')
    async def arcdps_channel_set(self, ctx, channel: discord.TextChannel = None) -> None:
        """Sets the arcdps notification channel for a guild."""
        logger.info(f"{ctx.author.name} used the arcdps channel set command.")
        if not channel:
            channel = ctx.channel
        self.setGuildArcdpsChannel(ctx.guild, channel.id)
        self.enableArcdpsChecker(ctx.guild)

        logger.info(f"The arcdps notification channel for {ctx.guild.name} has been set to #{channel.name}.")
        confirmationMessage = makeSimpleTextEmbed(
            f'The arcdps update notification channel has been set to {channel.mention}.')
        await ctx.send(embed=confirmationMessage)

    @arcdps.group(name='role')
    async def arcdps_role(self, ctx):
        """Initializes the arcdps role subcommand group."""
        logger.info(f"{ctx.author.name} used the arcdps role command.")
        if ctx.invoked_subcommand is None:
            notificationRole = self.getGuildArcdpsRole(ctx.guild)
            match notificationRole:
                case None:
                    message = makeSimpleTextEmbed('No role has been set for the arcdps update notifier.')
                case _:
                    message = makeSimpleTextEmbed(
                        f'The arcdps update notification role is currently set to {notificationRole.mention}')
            await ctx.send(embed=message)

    @arcdps_role.command(name='set')
    async def arcdps_role_set(self, ctx, role: discord.Role) -> None:
        """Sets the arcdps notification role for a guild."""
        logger.info(f"{ctx.author.name} used the arcdps role set command.")
        self.setGuildArcdpsRole(ctx.guild, role.id)

        logger.info(f"The arcdps notification role for {ctx.guild.name} has been set to {role.name}.")
        confirmationMessage = makeSimpleTextEmbed(
            f'The arcdps update notification role has been set to {role.mention}.')
        await ctx.send(embed=confirmationMessage)

    @arcdps_role.command(name='remove')
    async def arcdps_role_remove(self, ctx) -> None:
        """Removes the arcdps notification role for a guild."""
        logger.info(f"{ctx.author.name} used the arcdps role remove command.")
        self.setGuildArcdpsRole(ctx.guild, None)

        logger.info(f"The arcdps notification role for {ctx.guild.name} has been removed.")
        confirmationMessage = makeSimpleTextEmbed(
            f'The arcdps update notification role has been removed.')
        await ctx.send(embed=confirmationMessage)

    @arcdps.command(name='enable')
    async def arcdps_enable(self, ctx) -> None:
        """Enables the arcdps update notifier for a guild."""
        logger.info(f"{ctx.author.name} used the arcdps enable command.")

        self.enableArcdpsChecker(ctx.guild)
        confirmationMessage = makeSimpleTextEmbed('The arcdps update notifier has been enabled!')
        await ctx.send(embed=confirmationMessage)

    @arcdps.command(name='disable')
    async def arcdps_disable(self, ctx) -> None:
        """Disables the arcdps update notifier for a guild."""
        logger.info(f"{ctx.author.name} used the arcdps disable command.")

        self.disableArcdpsChecker(ctx.guild)
        confirmationMessage = makeSimpleTextEmbed('The arcdps update notifier has been disabled!')
        await ctx.send(embed=confirmationMessage)

    @arcdps.group(name='reset')
    @commands.is_owner()
    async def arcdps_reset(self, ctx) -> None:
        """Removes the last update time in the configuration."""
        self.setLastUpdateTime(None)
        message = makeSimpleTextEmbed('Removed the last update time for testing purposes.')
        await ctx.send(embed=message)

    @tasks.loop(minutes=1)
    async def arcdpsCheck(self):
        if self.newUpdate():
            await self.alertGuilds()

            currentUpdateTime = self.getCurrentUpdateTime()
            self.setLastUpdateTime(currentUpdateTime)

    @commands.Cog.listener()
    async def on_ready(self):
        if not isTesting():
            self.arcdpsCheck.start()

    @staticmethod
    def getArcdpsConfig() -> dict:
        """Returns the arcdps checker configuration for all guilds."""
        configPath = Path.cwd() / 'configurations' / 'arcdps.yaml'
        with open(configPath, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def saveArcdpsConfig(self) -> None:
        """Saves the cached arcdps checker configuration for all guilds."""
        configPath = Path.cwd() / 'configurations' / 'arcdps.yaml'

        logger.info('Saving configuration to file...')
        with open(configPath, 'w') as f:
            yaml.dump(self.config, f)
        logger.info('Configuration saved!')

    def getGuildArcdpsConfig(self, guild: discord.Guild) -> dict:
        """Returns the arcdps checker configuration for a given guild."""
        try:
            assert guild.id in self.config['guilds'].keys()
        except AssertionError:
            self.initializeGuildArcdpsConfig(guild)
        finally:
            return self.config['guilds'][guild.id]

    def initializeGuildArcdpsConfig(self, guild: discord.Guild) -> None:
        """Initializes a basic arcdps checker configuration for a new guild."""
        self.config['guilds'][guild.id] = {
            'enabled': False,
            'channelID': None,
            'roleID': None,
        }
        self.saveArcdpsConfig()

    def getGuildArcdpsEnabledStatus(self, guild: discord.Guild) -> bool:
        """Determines if a guild has the arcdps checker module enabled."""
        guildConfig = self.getGuildArcdpsConfig(guild)
        return guildConfig['enabled']

    def enableArcdpsChecker(self, guild: discord.Guild) -> None:
        """Enables the arcdps update checker for a given guild."""
        guildConfig = self.getGuildArcdpsConfig(guild)
        guildConfig['enabled'] = True
        self.saveArcdpsConfig()

    def disableArcdpsChecker(self, guild: discord.Guild) -> None:
        """Disables the arcdps update checker for a given guild."""
        guildConfig = self.getGuildArcdpsConfig(guild)
        guildConfig['enabled'] = False
        self.saveArcdpsConfig()

    def getEnabledGuilds(self) -> list[discord.Guild]:
        """Returns a list of guilds that have the arcdps update checker enabled."""
        config = self.getArcdpsConfig()
        guildsConfig = config['guilds']

        enabledGuilds = []
        for guildID, guildConfig in guildsConfig.items():
            enabled = guildConfig['enabled']
            if enabled:
                guild = self.bot.get_guild(guildID)
                enabledGuilds.append(guild)

        return enabledGuilds

    def getGuildArcdpsChannel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Returns a guild's arcdps notification channel."""
        guildConfig = self.getGuildArcdpsConfig(guild)
        channelID = guildConfig['channelID']

        match channelID:
            case None:
                return None
            case _:
                channel = self.bot.get_channel(channelID)
                return channel

    def setGuildArcdpsChannel(self, guild: discord.Guild, channelID: int) -> None:
        """Sets the arcdps notification channel for a given guild."""
        self.config['guilds'][guild.id]['channelID'] = channelID
        self.saveArcdpsConfig()

    def getGuildArcdpsRole(self, guild: discord.Guild) -> Optional[discord.Role]:
        """Returns a guild's arcdps notification role."""
        guildConfig = self.getGuildArcdpsConfig(guild)
        roleID = guildConfig['roleID']

        match roleID:
            case None:
                return None
            case _:
                role = guild.get_role(roleID)
                return role

    def setGuildArcdpsRole(self, guild: discord.Guild, roleID: int | None) -> None:
        """Sets the arcdps notification role for a given guild."""
        self.config['guilds'][guild.id]['roleID'] = roleID
        self.saveArcdpsConfig()

    def getLastUpdateTime(self) -> Optional[datetime]:
        """Returns the last time arcdps was updated."""
        return self.config['lastUpdateTime']

    def setLastUpdateTime(self, updateTime: datetime | None) -> None:
        """Sets the last time arcdps was updated."""
        self.config['lastUpdateTime'] = updateTime
        self.saveArcdpsConfig()

    @staticmethod
    def getArcdpsHTML() -> str:
        """Returns the HTML of the arcdps site as text."""
        arcdpsSite = "https://www.deltaconnected.com/arcdps/x64/"
        r = requests.get(arcdpsSite)
        if r.ok:
            return r.text
        else:
            logger.error(
                f"Website couldn't be reached. HTTP Error Code: {r.status_code}"
            )
            raise HTTPError(f"Code: {r.status_code}.")

    def getArcdpsSoup(self) -> BeautifulSoup:
        """Returns the BeautifulSoup object made from the arcdps website html."""
        htmlText = self.getArcdpsHTML()
        soup = BeautifulSoup(htmlText, "html.parser")
        return soup

    def getCurrentUpdateTime(self) -> datetime:
        """Returns the update time for the latest version of arcdps."""
        soup = self.getArcdpsSoup()
        lastUpdateTimeText = (
            soup.find(href="d3d9.dll").parent.find_next_sibling("td").text.strip()
        )
        lastUpdateTime = datetime.strptime(lastUpdateTimeText, "%Y-%m-%d %H:%M")
        return lastUpdateTime

    def newUpdate(self) -> bool:
        """Determines if there is a new update to arcdps."""
        lastUpdateTime = self.getLastUpdateTime()
        currentUpdateTime = self.getCurrentUpdateTime()

        if not lastUpdateTime:
            return True
        elif lastUpdateTime < currentUpdateTime:
            return True
        else:
            return False

    async def alertGuilds(self) -> None:
        """Sends a message to all guilds that a new update for arcdps is available."""
        message = self.makeNewUpdateEmbed()

        guilds = self.getEnabledGuilds()
        for guild in guilds:
            channel = self.getGuildArcdpsChannel(guild)
            role = self.getGuildArcdpsRole(guild)
            if role:
                await channel.send(content=role.mention, embed=message)
            else:
                await channel.send(embed=message)

    def makeNewUpdateEmbed(self) -> discord.Embed:
        lastUploadTime = self.getLastUpdateTime()
        currentUploadTime = self.getCurrentUpdateTime()

        match lastUploadTime:
            case None:
                lastUploadTimeText = 'None'
            case _:
                lastUploadTimeText = lastUploadTime.strftime("%Y-%m-%d %H:%M")
        currentUploadTimeText = currentUploadTime.strftime("%Y-%m-%d %H:%M")

        embed = discord.Embed(
            title="There is a new ArcDPS Update!",
            url="https://www.deltaconnected.com/arcdps/x64/",
            color=0xFFFFFF,
        )
        embed.set_author(name="Phan Bot", icon_url='https://i.imgur.com/CkAoqD2.png')
        embed.add_field(name="Previous Version", value=lastUploadTimeText)
        embed.add_field(name="Current Version", value=currentUploadTimeText)

        return embed

    def makeArcdpsOverviewEmbed(self, guild: discord.Guild) -> discord.Embed:
        """Creates an embed containing an overview of all the guild's arcdps configurations."""
        enabled = self.getGuildArcdpsEnabledStatus(guild)
        role = self.getGuildArcdpsRole(guild)
        channel = self.getGuildArcdpsChannel(guild)

        enabledSymbol = '✅' if enabled else '❌'

        embed = discord.Embed(title="Arcdps Notifier")
        embed.set_author(name="Phan Bot", icon_url="https://i.imgur.com/CkAoqD2.png")
        embed.add_field(name="Channel", value=f"{channel.mention}")
        if role:
            embed.add_field(name="Role", value=f"{role.mention}")
        else:
            embed.add_field(name="Role", value=f"None")
        embed.add_field(name="Enabled", value=enabledSymbol)

        return embed


def setup(bot):
    bot.add_cog(Arcdps(bot))
