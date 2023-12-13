import logging

import discord
from discord.ext import commands

from helpers import logoURL

logger = logging.getLogger("main.general")


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Print a console message when the bot is ready and active."""
        logger.info('Bot is now up and running!')

        print("Logged in as")
        print(self.bot.user.name)
        print(self.bot.user.id)
        print("------")

    @commands.command()
    async def help(self, ctx):
        helpEmbed = self.makeHelpEmbed()

        await ctx.send(embed=helpEmbed)

    @staticmethod
    def makeHelpEmbed():
        """Creates and returns the embed used for the !help discord command."""
        helpEmbed = discord.Embed(title="Commands", color=0xFFFFFF)
        helpEmbed.set_author(name="PhanBot", icon_url=logoURL)

        generalCommands = """TBD"""
        helpEmbed.add_field(name="General", value=generalCommands)

        buttonGameCommands = """TBD"""
        helpEmbed.add_field(name="Button Game", value=buttonGameCommands)

        extrasCommands1 = """TBD"""

        extrasCommands2 = """TBD"""

        helpEmbed.add_field(name="Extras", value=extrasCommands1)
        helpEmbed.add_field(name="Extras (cont.)", value=extrasCommands2)

        roleAssignmentCommands = """TBD"""
        helpEmbed.add_field(name="Role Assignment", value=roleAssignmentCommands)

        helpEmbed.set_thumbnail(url=logoURL)

        return helpEmbed


async def setup(bot):
    await bot.add_cog(General(bot))
