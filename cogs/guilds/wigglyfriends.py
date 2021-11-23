import logging

from discord.ext import commands

import helpers

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
    @helpers.logCommand(logger=logger)
    async def bap(self, ctx) -> None:
        phanID = 435141251797483540
        phanUser = await self.bot.fetch_user(phanID)
        emoji = "<a:phanbap:722239855618293760>"

        await ctx.channel.send(f"{phanUser.mention} {emoji}")

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def corona(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/mG10VIX.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def traitor(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/deOBda9.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def traitorti(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/K9YURW6.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def shower(self, ctx):
        dot = await self.bot.fetch_user(226166683046248448)
        embed = helpers.makeSimpleTextEmbed("pls <:wuhh:724762759421624461> Go shower!")

        await ctx.send(f"{dot.mention}", embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def whitty(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/7kVeHV3.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def kieran(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/1U4AqJe.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def corn(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/IFitNY3.jpg")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def boxbaby(self, ctx):
        embed = helpers.makeSimpleTextEmbed("A baby. In a box. Box baby.")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def stroke(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/1b0yE2R.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def sexy(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/r6itxP0.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def nobelprize(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/tdZfj0Z.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def john(self, ctx):
        embed = helpers.makeSimpleTextEmbed("Thank you John! :)")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def canadian(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/I53BoAf.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def duality(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/IKgQY2g.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def chickens(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/lHGL0yt.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def quarantine(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/C7RP47V.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def bape(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/dvu4guN.png")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
