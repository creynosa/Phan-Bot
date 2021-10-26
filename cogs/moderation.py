import datetime
import logging
import re
from pathlib import Path
from typing import Optional

import discord
import pytz
import yaml
from discord.ext import commands
from helpers import makeSimpleTextEmbed

logger = logging.getLogger("main.moderation")


class Moderation(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.configPath = Path.cwd() / "configurations" / "moderation.yaml"
        self.config = self.getModerationConfig()

    async def cog_check(self, ctx) -> None:
        """Check to see if the user is has administrative privileges."""
        isAdministrator = ctx.author.guild_permissions.administrator
        return isAdministrator

    # -------------COMMANDS-------------------

    @commands.command()
    async def say(self, ctx, *, text) -> None:
        """Makes the bot repeat whatever the user inputted in a given channel."""
        logger.info(f"{ctx.author.name} used the say command. Argument: {text}")
        await ctx.message.delete()

        if "@here" in text or "@everyone" in text:
            await ctx.send(f"{ctx.author.mention} just tried to ping everyone! 😡")
            return

        channel = await self.getSayChannel(ctx, text)
        updatedText = self.removeChannelNameFromText(text)

        await channel.send(updatedText)

    @commands.command()
    async def clear(self, ctx, num: str) -> None:
        """Command use to delete a specified number of messages in a given channel."""
        logger.info(f"{ctx.author.name} used the clear command. Number of messages: {num}")
        await ctx.message.delete()

        channel = ctx.channel
        await channel.purge(limit=int(num))

    @commands.group()
    async def channels(self, ctx) -> None:
        """Initializes the moderation command group."""
        if ctx.invoked_subcommand is None:
            logger.info(f"{ctx.author.name} used the channels command.")
            guild = ctx.guild
            embed = self.makeChannelOverviewEmbed(guild)
            await ctx.send(embed=embed)

    @channels.group()
    async def deletions(self, ctx) -> None:
        """Initializes the deletions command subgroup for the channels command group."""
        if ctx.invoked_subcommand is None:
            return

    @deletions.command(name="enable")
    async def deletions_enable(self, ctx) -> None:
        """Enables the deletions notification channel."""
        logger.info(f"{ctx.author.name} used the channels deletions enable command.")
        guild = ctx.guild
        try:
            self.enableChannel(guild, "deletions")
            embed = makeSimpleTextEmbed(f"The deletions notification channel has been enabled!")
        except Exception:
            embed = makeSimpleTextEmbed(
                f"The deletions notification channel has not been set yet."
            )
        await ctx.send(embed=embed)

    @deletions.command(name="disable")
    async def deletions_disable(self, ctx) -> None:
        """Disables the deletions notification channel."""
        logger.info(f"{ctx.author.name} used the channels deletions disable command.")
        guild = ctx.guild
        self.disableChannel(guild, "deletions")
        embed = makeSimpleTextEmbed(f"The deletions notification channel has been disabled!")
        await ctx.send(embed=embed)

    @deletions.command(name="get")
    async def deletions_get(self, ctx) -> None:
        """Gets the deletions notification channel for a guild."""
        logger.info(f"{ctx.author.name} used the channels deletions get command.")

        guild = ctx.guild

        channel = self.getModerationChannel(guild, "deletions")
        if channel is not None:
            embed = makeSimpleTextEmbed(
                f"The channel for deletions notifications is currently set to {channel.mention}."
            )
        else:
            embed = makeSimpleTextEmbed(f"There is no deletions notification channel set.")

        await ctx.send(embed=embed)

    @deletions.command(name="set")
    async def deletions_set(self, ctx, channel: discord.TextChannel = None) -> None:
        """Sets a channel to be the deletions notification channel for a guild."""
        logger.info(f"{ctx.author.name} used the channels deletions set command.")

        guild = ctx.guild

        if channel is None:
            channel = ctx.channel

        self.setModerationChannel(guild, "deletions", channel)
        self.enableChannel(guild, "deletions")
        self.saveModerationConfig()

        embed = makeSimpleTextEmbed(
            f"The deletions notification channel has been set to {channel.mention}."
        )
        await ctx.send(embed=embed)

    @deletions.command(name="remove")
    async def deletions_remove(self, ctx) -> None:
        """Removes the deletions notification channel for a guild."""
        logger.info(f"{ctx.author.name} used the channels deletions remove command.")

        guild = ctx.guild

        self.disableChannel(guild, "deletions")
        self.removeModerationChannel(guild, "deletions")
        self.saveModerationConfig()

        embed = makeSimpleTextEmbed(f"The deletions notification channel has been removed.")
        await ctx.send(embed=embed)

    @deletions.group(name="ignorelist")
    async def deletions_ignorelist(self, ctx) -> None:
        if ctx.invoked_subcommand is None:
            logger.info(f"{ctx.author.name} used the channels deletions ignorelist command.")
            embed = await self.makeIgnoreListEmbed(ctx, "deletions")
            await ctx.send(embed=embed)

    @deletions_ignorelist.command(name="add")
    async def deletions_ignorelist_add(self, ctx, ignoredItem: str) -> None:
        logger.info(f"{ctx.author.name} used the channels deletions ignorelist add command.")
        if not await self.isValidUserOrChannel(ctx, ignoredItem):
            embed = makeSimpleTextEmbed(f"Invalid channel or user. Please try again.")
            await ctx.send(embed=embed)
            return

        await self.addToIgnorelist(ctx, "deletions", ignoredItem)
        self.saveModerationConfig()

    @deletions_ignorelist.command(name="remove")
    async def deletions_ignorelist_remove(self, ctx, ignoredItem: str) -> None:
        logger.info(f"{ctx.author.name} used the channels deletions ignorelist remove command.")
        if not await self.isValidUserOrChannel(ctx, ignoredItem):
            embed = makeSimpleTextEmbed(f"Invalid channel or user. Please try again.")
            await ctx.send(embed=embed)
            return

        await self.removeFromIgnorelist(ctx, "deletions", ignoredItem)
        self.saveModerationConfig()

    @channels.group()
    async def arrivals(self, ctx) -> None:
        """Initializes the arrivals command subgroup for the channels command group."""
        if ctx.invoked_subcommand is None:
            return

    @arrivals.command(name="enable")
    async def arrivals_enable(self, ctx) -> None:
        """Enables the arrivals notification channel."""
        logger.info(f"{ctx.author.name} used the channels arrivals enable command.")
        guild = ctx.guild
        try:
            self.enableChannel(guild, "arrivals")
            embed = makeSimpleTextEmbed(f"The arrivals notification channel has been enabled!")
        except Exception:
            embed = makeSimpleTextEmbed(f"The arrivals notificaton channel has not been set yet.")
        await ctx.send(embed=embed)

    @arrivals.command(name="disable")
    async def arrivals_disable(self, ctx) -> None:
        """Disables the arrivals notification channel."""
        logger.info(f"{ctx.author.name} used the channels arrivals disable command.")
        guild = ctx.guild
        self.disableChannel(guild, "arrivals")
        embed = makeSimpleTextEmbed(f"The arrivals notification channel has been disabled!")
        await ctx.send(embed=embed)

    @arrivals.command(name="get")
    async def arrivals_get(self, ctx) -> None:
        """Gets the arrivals notification channel for a guild."""
        logger.info(f"{ctx.author.name} used the channels arrivals get command.")

        guild = ctx.guild

        channel = self.getModerationChannel(guild, "arrivals")
        if channel is not None:
            embed = makeSimpleTextEmbed(
                f"The channel for arrivals notifications is currently set to {channel.mention}."
            )
        else:
            embed = makeSimpleTextEmbed(f"There is no arrivals notification channel set.")

        await ctx.send(embed=embed)

    @arrivals.command(name="set")
    async def arrivals_set(self, ctx, channel: discord.TextChannel = None) -> None:
        """Sets a channel to be the arrivals notification channel for a guild."""
        logger.info(f"{ctx.author.name} used the channels arrivals set command.")

        guild = ctx.guild

        if channel is None:
            channel = ctx.channel

        self.setModerationChannel(guild, "arrivals", channel)
        self.enableChannel(guild, "arrivals")
        self.saveModerationConfig()

        embed = makeSimpleTextEmbed(
            f"The arrivals notification channel has been set to {channel.mention}."
        )
        await ctx.send(embed=embed)

    @arrivals.command(name="remove")
    async def arrivals_remove(self, ctx) -> None:
        """Removes the arrivals notification channel for a guild."""
        logger.info(f"{ctx.author.name} used the channels arrivals remove command.")

        guild = ctx.guild

        self.disableChannel(guild, "arrivals")
        self.removeModerationChannel(guild, "arrivals")
        self.saveModerationConfig()

        embed = makeSimpleTextEmbed(f"The arrivals notification channel has been removed.")
        await ctx.send(embed=embed)

    @arrivals.group(name="ignorelist")
    async def arrivals_ignorelist(self, ctx) -> None:
        if ctx.invoked_subcommand is None:
            logger.info(f"{ctx.author.name} used the channels arrivals ignorelist command.")
            embed = await self.makeIgnoreListEmbed(ctx, "arrivals")
            await ctx.send(embed=embed)

    @arrivals_ignorelist.command(name="add")
    async def arrivals_ignorelist_add(self, ctx, ignoredItem: str) -> None:
        logger.info(f"{ctx.author.name} used the channels arrivals ignorelist add command.")
        if not await self.isValidUserOrChannel(ctx, ignoredItem):
            embed = makeSimpleTextEmbed(f"Invalid channel or user. Please try again.")
            await ctx.send(embed=embed)
            return

        await self.addToIgnorelist(ctx, "arrivals", ignoredItem)
        self.saveModerationConfig()

    @arrivals_ignorelist.command(name="remove")
    async def arrivals_ignorelist_remove(self, ctx, ignoredItem: str) -> None:
        logger.info(f"{ctx.author.name} used the channels arrivals ignorelist remove command.")
        if not await self.isValidUserOrChannel(ctx, ignoredItem):
            embed = makeSimpleTextEmbed(f"Invalid channel or user. Please try again.")
            await ctx.send(embed=embed)
            return

        await self.removeFromIgnorelist(ctx, "arrivals", ignoredItem)
        self.saveModerationConfig()

    @channels.group()
    async def departures(self, ctx) -> None:
        """Initializes the departures command subgroup for the channels command group."""
        if ctx.invoked_subcommand is None:
            return

    @departures.command(name="enable")
    async def departures_enable(self, ctx) -> None:
        """Enables the departures notification channel."""
        logger.info(f"{ctx.author.name} used the channels departures enable command.")
        guild = ctx.guild
        try:
            self.enableChannel(guild, "departures")
            embed = makeSimpleTextEmbed(f"The departures notification channel has been enabled!")
        except Exception:
            embed = makeSimpleTextEmbed(
                f"The departures notificaton channel has not been set yet."
            )
        await ctx.send(embed=embed)

    @departures.command(name="disable")
    async def departures_disable(self, ctx) -> None:
        """Disables the departures notification channel."""
        logger.info(f"{ctx.author.name} used the channels departures disable command.")
        guild = ctx.guild
        self.disableChannel(guild, "departures")
        embed = makeSimpleTextEmbed(f"The departures notification channel has been disabled!")
        await ctx.send(embed=embed)

    @departures.command(name="set")
    async def departures_set(self, ctx, channel: discord.TextChannel = None) -> None:
        """Sets a channel to be the departures notification channel for a guild."""
        logger.info(f"{ctx.author.name} used the channels departures set command.")

        guild = ctx.guild

        if channel is None:
            channel = ctx.channel

        self.setModerationChannel(guild, "departures", channel)
        self.enableChannel(guild, "departures")
        self.saveModerationConfig()

        embed = makeSimpleTextEmbed(
            f"The departures notification channel has been set to {channel.mention}."
        )
        await ctx.send(embed=embed)

    @departures.command(name="get")
    async def departures_get(self, ctx) -> None:
        """Gets the departures notification channel for a guild."""
        logger.info(f"{ctx.author.name} used the channels departures get command.")

        guild = ctx.guild

        channel = self.getModerationChannel(guild, "departures")
        if channel is not None:
            embed = makeSimpleTextEmbed(
                f"The channel for departures notifications is currently set to {channel.mention}."
            )
        else:
            embed = makeSimpleTextEmbed(f"There is no departures notification channel set.")

        await ctx.send(embed=embed)

    @departures.command(name="remove")
    async def departures_remove(self, ctx) -> None:
        """Removes the departures notification channel for a guild."""
        logger.info(f"{ctx.author.name} used the channels departures remove command.")

        guild = ctx.guild

        self.disableChannel(guild, "departures")
        self.removeModerationChannel(guild, "departures")
        self.saveModerationConfig()

        embed = makeSimpleTextEmbed(f"The departures notification channel has been removed.")
        await ctx.send(embed=embed)

    @departures.group(name="ignorelist")
    async def departures_ignorelist(self, ctx) -> None:
        if ctx.invoked_subcommand is None:
            logger.info(f"{ctx.author.name} used the channels departures ignorelist command.")
            embed = await self.makeIgnoreListEmbed(ctx, "departures")
            await ctx.send(embed=embed)

    @departures_ignorelist.command(name="add")
    async def departures_ignorelist_add(self, ctx, ignoredItem: str) -> None:
        logger.info(f"{ctx.author.name} used the channels departures ignorelist add command.")
        if not await self.isValidUserOrChannel(ctx, ignoredItem):
            embed = makeSimpleTextEmbed(f"Invalid channel or user. Please try again.")
            await ctx.send(embed=embed)
            return

        await self.addToIgnorelist(ctx, "departures", ignoredItem)
        self.saveModerationConfig()

    @departures_ignorelist.command(name="remove")
    async def departures_ignorelist_remove(self, ctx, ignoredItem: str) -> None:
        logger.info(f"{ctx.author.name} used the channels departures ignorelist remove command.")
        if not await self.isValidUserOrChannel(ctx, ignoredItem):
            embed = makeSimpleTextEmbed(f"Invalid channel or user. Please try again.")
            await ctx.send(embed=embed)
            return

        await self.removeFromIgnorelist(ctx, "departures", ignoredItem)
        self.saveModerationConfig()

    # -------------LISTENERS-------------------

    @commands.Cog.listener()
    async def on_message_delete(self, message) -> None:
        """Sends a message in a set channel when a message has been deleted."""
        guild = message.guild
        guildID = message.guild.id

        if not self.isChannelEnabled(guild, "deletions"):
            return

        logger.info(
            f"A message by {message.author.name} has been deleted in {guild.name} in #{message.channel.name}."
        )

        channel = self.getModerationChannel(guild, "deletions")
        if channel is None:
            return

        if self.isIgnored(guildID, message):
            return

        embed = self.makeDeletedMessageEmbed(message)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member) -> None:
        """Sends a message in a set channel when a user joins a server."""
        guild = member.guild

        if not self.isChannelEnabled(guild, "arrivals"):
            return

        logger.info(f"User {member.name} has joined {guild.name}.")

        channel = self.getModerationChannel(guild, "arrivals")
        if channel is None:
            return

        embed = self.makeNewArrivalEmbed(member)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member) -> None:
        """Sends a message in a set channel when a user leaves a server."""
        guild = member.guild

        if not self.isChannelEnabled(guild, "departures"):
            return

        logger.info(f"User {member.name} has left {guild.name}.")

        channel = self.getModerationChannel(guild, "departures")
        if channel is None:
            return

        embed = self.makeDepartureEmbed(member)
        await channel.send(embed=embed)

    # -------------HELPERS-------------------

    def enableChannel(self, guild: discord.Guild, channelCategory: str) -> bool:
        """Enables the specified moderation channel for a given guild."""
        channelConfig = self.getGuildChannelConfig(channelCategory, guild.id)

        if channelConfig["channelID"] is not None:
            channelConfig["enabled"] = True
            self.saveModerationConfig()

            logger.info(f"Enabled the {channelCategory} notification channel for {guild.name}.")
        else:
            raise Exception

    def disableChannel(self, guild: discord.Guild, channelCategory: str) -> bool:
        """Disables the specified moderation channel for a given guild."""
        channelConfig = self.getGuildChannelConfig(channelCategory, guild.id)
        channelConfig["enabled"] = False
        self.saveModerationConfig()
        logger.info(f"Disabled the {channelCategory} notification channel for {guild.name}.")

    def isChannelEnabled(self, guild: discord.Guild, channelCategory: str) -> bool:
        """Checks to see if the given moderation channel is enabled."""
        channelConfig = self.getGuildChannelConfig(channelCategory, guild.id)
        return channelConfig["enabled"]

    def makeChannelOverviewEmbed(self, guild: discord.Guild) -> discord.Embed:
        """Creates an embed containing an overview of all the guild's moderation channels."""
        enabledChannels = self.getEnabledChannels(guild)
        disabledChannels = self.getDisabledChannels(guild)

        channelText = ""
        statusText = ""
        categoryText = ""
        for channelCategory, channel in enabledChannels.items():
            categoryText += channelCategory.title() + "\n"
            channelText += f"{channel.mention} \n"
            statusText += "✅\n"

        for channelCategory, channel in disabledChannels.items():
            categoryText += channelCategory.title() + "\n"
            if channel is not None:
                channelText += f"{channel.mention} \n"
            else:
                channelText += f"None \n"
            statusText += "❌\n"

        embed = discord.Embed(title="Moderation Channels")
        embed.set_author(name="Phan Bot", icon_url="https://i.imgur.com/CkAoqD2.png")
        embed.add_field(name="Category", value=categoryText)
        embed.add_field(name="Channel", value=channelText)
        embed.add_field(name="Enabled", value=statusText)

        return embed

    def getEnabledChannels(self, guild: discord.Guild) -> dict[str, discord.TextChannel]:
        """Gets the category name for all enabled moderation channels as well as their channel object."""
        guildChannelsConfig = self.getGuildChannelsConfig(guild.id)

        activeChannels = {}
        for channelCategory, channelConfig in guildChannelsConfig.items():
            enabled = channelConfig["enabled"]
            if enabled:
                channelID = channelConfig["channelID"]
                channel = self.bot.get_channel(channelID)
                activeChannels[channelCategory] = channel

        return activeChannels

    def getDisabledChannels(
        self, guild: discord.Guild
    ) -> dict[str, Optional[discord.TextChannel]]:
        """Gets the category name for all disabled moderation channels."""
        guildChannelsConfig = self.getGuildChannelsConfig(guild.id)

        inactiveChannels = {}
        for channelCategory, channelConfig in guildChannelsConfig.items():
            enabled = channelConfig["enabled"]
            if not enabled:
                channelID = channelConfig["channelID"]
                if channelID is None:
                    inactiveChannels[channelCategory] = None

                channel = self.bot.get_channel(channelID)
                inactiveChannels[channelCategory] = channel

        return inactiveChannels

    async def getSayChannel(self, ctx, text: str) -> Optional[discord.TextChannel]:
        """Returns the discord channel that the bot will send a message in when using the say command."""
        channelNameRegex = re.compile(r"<#\d*>")
        match = re.search(channelNameRegex, text)
        if match is not None:
            channelString = match.group(0)
            channel = await commands.TextChannelConverter().convert(ctx, channelString)
        else:
            channel = ctx.channel

        return channel

    async def makeIgnoreListEmbed(self, ctx, channelCategory: str) -> discord.Embed:
        """Creates an embed containing information about a given channel's ignorelist."""
        ignoredUsersText = await self.getIgnoredUsersMentions(ctx, channelCategory)
        ignoredChannelsText = await self.getIgnoredChannelsMentions(ctx, channelCategory)

        titleText = f"{channelCategory.title()}: Ignorelist"

        embed = discord.Embed(title=titleText)
        embed.set_author(name="Phan Bot", icon_url="https://i.imgur.com/CkAoqD2.png")
        embed.add_field(name="Users", value=ignoredUsersText)
        embed.add_field(name="Channels", value=ignoredChannelsText)

        return embed

    def removeChannelNameFromText(self, text: str) -> str:
        """Removes any channel identifier text from a string."""
        channelNameRegex = re.compile(r"<#\d*>")
        updatedText = re.sub(channelNameRegex, "", text)

        return updatedText

    def makeDepartureEmbed(self, member: discord.Member) -> discord.Embed:
        """Creates an embed containing information about a departure."""
        pfpURL = member.avatar_url
        timeJoinedDatetime = datetime.datetime.now().replace(tzinfo=pytz.utc)
        timeJoined = timeJoinedDatetime.strftime("%m/%d/%y at %I:%M %p %Z")

        # Create the embed containing the message's information.
        embed = discord.Embed(
            title=f"Looks like someone wasn't a phan... :(",
            color=0xFFFFFF,
        )
        embed.set_thumbnail(url=pfpURL)
        embed.set_author(name=member, icon_url=pfpURL)
        embed.set_footer(text=f"Left on {timeJoined}")

        return embed

    def makeNewArrivalEmbed(self, member: discord.Member) -> discord.Embed:
        """Creates an embed containing information about a new arrival."""
        pfpURL = member.avatar_url
        timeJoinedDatetime = member.joined_at.replace(tzinfo=pytz.utc)
        timeJoined = timeJoinedDatetime.strftime("%m/%d/%y at %I:%M %p %Z")

        embed = discord.Embed(
            title=f"Looks like someone became a phan!",
            color=0xFFFFFF,
        )
        embed.set_thumbnail(url=pfpURL)
        embed.set_author(name=member, icon_url=pfpURL)
        embed.set_footer(text=f"Joined on {timeJoined}")

        return embed

    def getModerationConfig(self) -> dict:
        """Gets the moderation configurations for all guilds."""
        with open(self.configPath, "r") as f:
            config = yaml.safe_load(f)
        return config

    def saveModerationConfig(self) -> None:
        """Saves the cached config and any changes to the config file."""
        with open(self.configPath, "w") as f:
            yaml.dump(self.config, f)

    def getGuildConfig(self, guildID: int) -> dict:
        """Gets the moderation configurations for a specified guild."""
        return self.config["guilds"][guildID]

    def getGuildChannelsConfig(self, guildID: int) -> dict:
        """Retrieves a guild's moderation channels configurations"""
        guildConfig = self.getGuildConfig(guildID)
        return guildConfig["channels"]

    def getGuildChannelConfig(self, channelCategory: str, guildID: int) -> dict:
        """Retrieves the configurations for a specified channel for a given guild."""
        channelsConfig = self.getGuildChannelsConfig(guildID)
        return channelsConfig[channelCategory]

    def isIgnored(self, guildID: int, message: discord.Message) -> bool:
        """Determines if a message contains an ignored user ID or channel ID."""
        channelConfig = self.getGuildChannelConfig("deletions", guildID)

        ignoredUserIDs = channelConfig["ignoredUserIDs"]
        ignoredChannelIDs = channelConfig["ignoredChannelIDs"]

        if ignoredUserIDs is not None:
            if message.author.id in ignoredUserIDs:
                return True

        if ignoredChannelIDs is not None:
            if message.channel.id in ignoredChannelIDs:
                return True

        return False

    def makeDeletedMessageEmbed(self, message: discord.Message) -> discord.Embed:
        """Creates an embed containing information about a deleted message."""
        user = message.author
        pfpURL = user.avatar_url
        msgChannel = message.channel
        msgContent = message.content
        msgCreatedAt = message.created_at.replace(tzinfo=pytz.utc)
        msgCreatedAtFormatted = msgCreatedAt.strftime("%m/%d/%y at %I:%M %p %Z")

        embed = discord.Embed(
            title=f"Looks like a message was deleted in #{msgChannel}!",
            description=f"{msgContent}",
            color=0xFFFFFF,
        )
        embed.set_thumbnail(url=pfpURL)
        embed.set_author(name=user, icon_url=pfpURL)
        embed.set_footer(text=f"Deleted message was sent on {msgCreatedAtFormatted}")

        return embed

    def setModerationChannel(
        self, guild: discord.Guild, channelCategory: str, channel: discord.TextChannel
    ) -> None:
        """Sets a channel to be a specified notification channel for a guild."""
        channelConfig = self.getGuildChannelConfig(channelCategory, guild.id)
        channelConfig["channelID"] = channel.id

        logger.info(
            f"Set the {channelCategory} notification channel to #{channel.name} for {guild.name}."
        )

    def getModerationChannel(
        self, guild: discord.Guild, channelCategory: str
    ) -> Optional[discord.TextChannel]:
        """Gets a specified notification channel for a guild."""
        channelConfig = self.getGuildChannelConfig(channelCategory, guild.id)
        channelID = channelConfig["channelID"]

        if channelID is not None:
            channel = self.bot.get_channel(channelID)
        else:
            channel = None

        return channel

    def removeModerationChannel(self, guild: discord.Guild, channelCategory: str) -> None:
        """Removes the specified notification channel for a guild."""
        channelConfig = self.getGuildChannelConfig(channelCategory, guild.id)
        channelConfig["channelID"] = None

        logger.info(f"Removed the {channelCategory} notification channel from {guild.name}.")

    async def isValidUserOrChannel(self, ctx, object: str) -> bool:
        """A check to see if a string yields a valid discord user or channel."""
        if object is None:
            return True

        try:
            await commands.TextChannelConverter().convert(ctx, object)
            return True
        except:
            try:
                await commands.UserConverter().convert(ctx, object)
                return True
            except:
                return False

    async def addToIgnorelist(self, ctx, channelCategory: str, item: str) -> None:
        """Adds a user or channel to the ignored user or channel ID for a specified channel."""
        channelConfig = self.getGuildChannelConfig(channelCategory, ctx.guild.id)

        # Adding users to ignore list
        alreadyExists = False
        if item.startswith("<@"):
            user = await commands.UserConverter().convert(ctx, item)
            pretext = f"user {user.name}"

            if user.id not in channelConfig["ignoredUserIDs"]:
                channelConfig["ignoredUserIDs"].append(user.id)
            else:
                alreadyExists = True

        # Adding channels to ignore list
        elif item.startswith("<#"):
            channel = await commands.TextChannelConverter().convert(ctx, item)
            pretext = f"channel #{channel.name}"

            if channel.id not in channelConfig["ignoredChannelIDs"]:
                channelConfig["ignoredChannelIDs"].append(channel.id)
            else:
                alreadyExists = True

        if not alreadyExists:
            logger.info(
                f"Added {pretext} to the {channelCategory} notification channel ignorelist."
            )

            embed = makeSimpleTextEmbed(
                f"Added {pretext} to the {channelCategory} ignore list for {ctx.guild.name}."
            )
            await ctx.send(embed=embed)
        else:
            embed = makeSimpleTextEmbed(f"Looks like {pretext} is already on the ignore list.")
            await ctx.send(embed=embed)

    async def removeFromIgnorelist(self, ctx, channelCategory: str, item: str) -> None:
        """Adds a user or channel to the ignored user or channel ID for a specified channel."""
        channelConfig = self.getGuildChannelConfig(channelCategory, ctx.guild.id)

        # Removing users
        alreadyExists = True
        if item.startswith("<@"):
            user = await commands.UserConverter().convert(ctx, item)
            pretext = f"user {user.name}"

            if user.id in channelConfig["ignoredUserIDs"]:
                channelConfig["ignoredUserIDs"].remove(user.id)
            else:
                alreadyExists = False

        # Removing channels
        elif item.startswith("<#"):
            channel = await commands.TextChannelConverter().convert(ctx, item)
            pretext = f"channel #{channel.name}"

            if channel.id in channelConfig["ignoredChannelIDs"]:
                channelConfig["ignoredChannelIDs"].remove(channel.id)
            else:
                alreadyExists = False

        if alreadyExists:
            logger.info(
                f"Removed {pretext} from the {channelCategory} ignore list for {ctx.guild.name}."
            )

            embed = makeSimpleTextEmbed(
                f"Removed {pretext} from the {channelCategory} ignore list."
            )
            await ctx.send(embed=embed)
        else:
            embed = makeSimpleTextEmbed(f"Looks like {pretext} isn't on the ignore list.")
            await ctx.send(embed=embed)

    async def getIgnoredUsersMentions(self, ctx, channelCategory: str) -> str:
        """Gets a string of all discord user mentions that are ignored for a given notification channel."""
        channelConfig = self.getGuildChannelConfig(channelCategory, ctx.guild.id)
        ignoredUserIDs = channelConfig["ignoredUserIDs"]

        ignoredUsersMentions = []
        if ignoredUserIDs != []:
            for userID in ignoredUserIDs:
                user = await commands.UserConverter().convert(ctx, str(userID))
                ignoredUsersMentions.append(user.mention)
        else:
            return "None"

        return "\n".join(ignoredUsersMentions)

    async def getIgnoredChannelsMentions(self, ctx, channelCategory: str) -> str:
        """Gets a string of all discord channel mentions that are ignored for a given notification channel."""
        channelConfig = self.getGuildChannelConfig(channelCategory, ctx.guild.id)
        ignoredChannelIDs = channelConfig["ignoredChannelIDs"]

        ignoredChannelsMentions = []
        if ignoredChannelIDs != []:
            for channelID in ignoredChannelIDs:
                channel = await commands.TextChannelConverter().convert(ctx, str(channelID))
                ignoredChannelsMentions.append(channel.mention)
        else:
            return "None"

        return "\n".join(ignoredChannelsMentions)


def setup(bot):
    bot.add_cog(Moderation(bot))
