import datetime
import logging

import discord
from discord.ext import commands

from helpers import convertToCST, getDatetimeString

logger = logging.getLogger("main.moderation")


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        # Check to see if the user is a moderator.
        isOwner = await self.bot.is_owner(ctx.author)
        return isOwner

    @commands.command()
    async def load(self, ctx, module: str) -> None:
        """Loads an unused module."""
        await ctx.message.delete()

        moduleName = module + ".py"
        try:
            self.bot.load_extension(moduleName)
        except Exception as e:
            logger.error(f"Could not load module {moduleName=}. Error: {e=}")
            await ctx.send("Error. Could not load module. For more details, CHECK THE LOGS.")

    @commands.command()
    async def unload(self, ctx, module: str) -> None:
        """Unloads a specified module."""
        await ctx.message.delete()

        moduleName = module + ".py"
        try:
            self.bot.unload_extension(moduleName)
        except Exception as e:
            logger.error(f"Could not unload module {moduleName=}. Error: {e=}")
            await ctx.send("Error. Could not unload module. For more details, CHECK THE LOGS.")

    @commands.command()
    async def clear(self, ctx, num: str):
        # Delete the original "!clear" command used to execute this block.
        await ctx.message.delete()

        # COMMENCE THE PURGE!!
        channel = ctx.channel
        await channel.purge(limit=int(num))
        return

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Executes certain code when a message is deleted."""
        logger.debug(f"A message was deleted in #{message.channel.name}")
        # Set the channel used for notifications.
        delMsgsChannelID = 1164681575292731552
        delMsgsChannel = self.bot.get_channel(delMsgsChannelID)

        # Retrieve information from the deleted message.
        author = message.author

        # Completely ignore any bot messages that get deleted.
        if author == self.bot.user or author.bot:
            return

        # Ignore any messages that were used for commands
        if message.content.startswith('!'):
            return

        authorPFPUrl = author.display_avatar.url
        content = message.content
        channel = message.channel
        timeCreated = message.created_at
        timeCreatedCST = convertToCST(timeCreated)
        timeCreatedCSTString = getDatetimeString(timeCreatedCST)

        # Create the embed containing the message's information.
        newEmbed = discord.Embed(
            title=f"Looks like a message was deleted in #{channel}!",
            description=f"{content}",
            color=0xFFFFFF,
        )
        newEmbed.set_thumbnail(url=authorPFPUrl)
        newEmbed.set_author(name=author, icon_url=authorPFPUrl)
        newEmbed.set_footer(text=f"Deleted message was created on {timeCreatedCSTString}")

        await delMsgsChannel.send(embed=newEmbed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        newMemberChannelID = 1164681596046159942
        newMemberChannel = self.bot.get_channel(newMemberChannelID)

        # Creating the embed generated for a new member join.
        authorPFPUrl = member.display_avatar.url
        timeJoined = member.joined_at
        timeJoinedCST = convertToCST(timeJoined)
        timeJoinedCSTString = getDatetimeString(timeJoinedCST)

        newEmbed = discord.Embed(
            title=f"Looks like someone became a phan!",
            color=0xFFFFFF,
        )
        newEmbed.set_thumbnail(url=authorPFPUrl)
        newEmbed.set_author(name=member, icon_url=authorPFPUrl)
        newEmbed.set_footer(text=f"Joined on {timeJoinedCSTString}")

        await newMemberChannel.send(embed=newEmbed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        departMemberChannelID = 1164681621442674838
        departMemberChannel = self.bot.get_channel(departMemberChannelID)

        authorPFPUrl = member.display_avatar.url
        timeLeft = datetime.datetime.now()
        timeLeftCST = convertToCST(timeLeft)
        timeLeftCSTString = getDatetimeString(timeLeftCST)

        # Create the embed containing the message's information.
        newEmbed = discord.Embed(
            title=f"Looks like someone wasn't a phan... :(",
            color=0xFFFFFF,
        )
        newEmbed.set_thumbnail(url=authorPFPUrl)
        newEmbed.set_author(name=member, icon_url=authorPFPUrl)
        newEmbed.set_footer(text=f"Left on {timeLeftCSTString}")

        await departMemberChannel.send(embed=newEmbed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
