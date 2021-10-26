import logging

import discord
import helpers
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

logger = logging.getLogger("main.wigglyfriends")


class Fun(commands.Cog):
    """Stores all fun commands and functions"""

    def __init__(self, bot):
        """Initializes the cog."""
        self.bot = bot

    async def cog_check(self, ctx) -> None:
        """Global check to see if the guild utilizing the commands is the WigglyFriends guild."""
        return ctx.guild.id == 721891483359379606

    @commands.command()
    async def bap(self, ctx) -> None:
        logger.info(f"{ctx.author.name} used the bap command.")

        phanID = 435141251797483540
        phanUser = await self.bot.fetch_user(phanID)
        emoji = "<a:phanbap:722239855618293760>"

        await ctx.channel.send(f"{phanUser.mention} {emoji}")

    @commands.command()
    async def corona(self, ctx):
        logger.info(f"{ctx.author.name} used the corona command.")
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/mG10VIX.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def traitor(self, ctx):
        logger.info(f"{ctx.author.name} used the traitor command.")
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/deOBda9.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def traitorti(self, ctx):
        logger.info(f"{ctx.author.name} used the traitorti command.")
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/K9YURW6.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def shower(self, ctx):
        logger.info(f"{ctx.author.name} used the shower command.")

        dot = await self.bot.fetch_user(226166683046248448)
        embed = helpers.makeSimpleTextEmbed("pls <:wuhh:724762759421624461> Go shower!")

        await ctx.send(f"{dot.mention}", embed=embed)

    @commands.command()
    async def whitty(self, ctx):
        logger.info(f"{ctx.author.name} used the whitty command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/7kVeHV3.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def kieran(self, ctx):
        logger.info(f"{ctx.author.name} used the kieran command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/1U4AqJe.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def corn(self, ctx):
        logger.info(f"{ctx.author.name} used the corn command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/IFitNY3.jpg")
        await ctx.send(embed=embed)

    @commands.command()
    async def boxbaby(self, ctx):
        logger.info(f"{ctx.author.name} used the boxbaby command.")

        embed = helpers.makeSimpleTextEmbed("A baby. In a box. Box baby.")
        await ctx.send(embed=embed)

    @commands.command()
    async def stroke(self, ctx):
        logger.info(f"{ctx.author.name} used the stroke command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/1b0yE2R.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def sexy(self, ctx):
        logger.info(f"{ctx.author.name} used the sexy command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/r6itxP0.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def nobelprize(self, ctx):
        logger.info(f"{ctx.author.name} used the nobelprize command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/tdZfj0Z.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def john(self, ctx):
        logger.info(f"{ctx.author.name} used the john command.")

        embed = helpers.makeSimpleTextEmbed("Thank you John! :)")
        await ctx.send(embed=embed)

    @commands.command()
    async def canadian(self, ctx):
        logger.info(f"{ctx.author.name} used the canadian command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/I53BoAf.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def duality(self, ctx):
        logger.info(f"{ctx.author.name} used the duality command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/IKgQY2g.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def chickens(self, ctx):
        logger.info(f"{ctx.author.name} used the chickens command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/lHGL0yt.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def quarantine(self, ctx):
        logger.info(f"{ctx.author.name} used the quarantine command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/C7RP47V.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def bape(self, ctx):
        logger.info(f"{ctx.author.name} used the bape command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/dvu4guN.png")
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return


def setup(bot):
    bot.add_cog(Fun(bot))
