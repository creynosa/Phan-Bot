import logging

import discord
from discord.ext import commands

import helpers

logger = logging.getLogger("main.onlyphans")


class OnlyPhans(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        """Global check to see if the guild utilizing the commands is the OnlyPhans guild."""
        return ctx.guild.id == 733944519640350771

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def eversong(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/HijmLV8.jpg")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def bagu4k(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/Wp9aJ4q.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def enter(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/tNSoLk5.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def marshiie(self, ctx):
        marshiieID = 142809966749679616
        marshiie = await self.bot.fetch_user(marshiieID)

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/UgiwdJV.png")
        await ctx.send(
            f"Introducing: the <:ayaya:745792801215610930> Ayaya"
            f"{marshiie.mention} Collection™ <:ayaya:745792801215610930>",
            embed=embed,
        )

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def maniicc(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/k94JJVU.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def kat(self, ctx):
        await ctx.send(content='<:why:745691113939009638>')

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def pusher(self, ctx):
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/0mHp2wx.png")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def neph(self, ctx):
        embed = helpers.makeSimpleTextEmbed("<a:loading:868329043081183272> Loading...")
        await ctx.send(embed=embed)

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def crab(self, ctx):
        oldNick = ctx.author.nick
        if oldNick is None:
            oldNick = str(ctx.author.name)

        crab = "🦀"
        newNick = f"{crab}{oldNick}{crab}"

        try:
            await ctx.author.edit(nick=newNick)
        except Exception as err:
            logger.error(f"Unknown error occurred when editing nickname! \n Error: {err}")

        await ctx.send("https://media.giphy.com/media/2dK0W3oUksQk0Xz8OK/giphy.gif")

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def auto(self, ctx):
        def autoMessageCheck(message: discord.Message) -> bool:
            """A message check for the auto command."""
            validResponses = ["y", "n", "yes", "no"]
            return message.author == ctx.author and message.content.lower() in validResponses

        counter = 0
        while True:
            if counter == 0:
                textModifier = ""
            else:
                textModifier = "REALLY " * counter

            embed = helpers.makeSimpleTextEmbed(
                f"Are you {textModifier}sure you want to kick auto? y/n"
            )
            await ctx.send(embed=embed)

            try:
                response = await self.bot.wait_for("message", check=autoMessageCheck, timeout=30)
            except Exception as err:
                print(err)
                embed = helpers.makeSimpleTextEmbed(
                    "Too late. Guess you don't really want to kick auto."
                )
                await ctx.send(embed=embed)
                return

            if response.content.lower() in ["no", "n"]:
                embed = helpers.makeSimpleTextEmbed("Okay... :(")
                await ctx.send(embed=embed)
                break

            counter += 1

    @commands.command()
    @helpers.logCommand(logger=logger)
    async def heck(self, ctx, member: discord.Member):
        if member != self.bot.user:
            embed = helpers.makeSimpleTextEmbed(
                f"Yeah! Heck {member.mention}! <a:MadNephGIF:832088703618908160>"
            )
        else:
            embed = helpers.makeSimpleTextEmbed(
                f"Nah! Heck you instead, {ctx.author.name}! <a:MadNephGIF:832088703618908160>"
            )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(OnlyPhans(bot))
