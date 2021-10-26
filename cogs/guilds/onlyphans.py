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
    async def eversong(self, ctx):
        logger.info(f"{ctx.author.name} used the eversong command.")
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/HijmLV8.jpg")
        await ctx.send(embed=embed)

    @commands.command()
    async def bagu4k(self, ctx):
        logger.info(f"{ctx.author.name} used the bagu4k command.")
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/Wp9aJ4q.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def enter(self, ctx):
        logger.info(f"{ctx.author.name} used the enter command.")
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/tNSoLk5.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def marshiie(self, ctx):
        logger.info(f"{ctx.author.name} used the marshiie command.")

        marshiieID = 142809966749679616
        marshiieUser = await self.bot.fetch_user(marshiieID)

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/UgiwdJV.png")
        await ctx.send(
            f"Introducing: the <:ayaya:745792801215610930> Ayaya"
            f"{marshiieUser.mention} Collection™ <:ayaya:745792801215610930>",
            embed=embed,
        )

    @commands.command()
    async def maniicc(self, ctx):
        logger.info(f"{ctx.author.name} used the maniic command.")
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/k94JJVU.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def kat(self, ctx):
        logger.info(f"{ctx.author.name} used the kat command.")
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/FJgfFTi.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def pusher(self, ctx):
        logger.info(f"{ctx.author.name} used the pusher command.")
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/0mHp2wx.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def neph(self, ctx):
        logger.info(f"{ctx.author.name} used the neph command.")
        embed = helpers.makeSimpleTextEmbed("<a:loading:868329043081183272> Loading...")
        await ctx.send(embed=embed)

    @commands.command()
    async def crab(self, ctx):
        logger.info(f"{ctx.author.name} used the crab command.")

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
    async def auto(self, ctx):
        logger.info(f"{ctx.author.name} used the auto command.")

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
    async def heck(self, ctx, member: discord.Member):
        logger.info(f"{ctx.author.name} used the heck command on {member.name}.")

        if member != self.bot.user:
            embed = helpers.makeSimpleTextEmbed(
                f"Yeah! Heck {member.mention}! <a:MadNephGIF:832088703618908160>"
            )
        else:
            embed = helpers.makeSimpleTextEmbed(
                f"Nah! Heck you instead, {ctx.author.name}! <a:MadNephGIF:832088703618908160>"
            )

        await ctx.send(embed=embed)

    # @commands.command()
    # async def trickortreat(self, ctx):
    #     """A surprise for users!"""
    #     guild = ctx.guild
    #     guildChannels = guild.channels
    #
    #     randomNum = random.randint(1, 1000)
    #     if randomNum == 1000:
    #         message = f"You've won 10g from Phan! <:NephEyes:891904818296262697> Congrats!!"
    #         embed = self.embedMessage(message)
    #         await ctx.send(content='<@!435141251797483540>', embed=embed)
    #     else:
    #         await ctx.send('<:wigglysneer:823689813474934824>')
    #         for _ in range(10):
    #             randomChannel = random.choice(guildChannels)
    #             if type(randomChannel) != discord.TextChannel:
    #                 continue
    #             message = await randomChannel.send(f"{ctx.author.mention}")
    #             await message.delete()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        phrases = ["fractal god", "fractalgod", "fractalg0d", "fractal g0d"]
        if message.author != self.bot.user:
            if any(phrase in message.content.lower() for phrase in phrases):
                logger.info(f"User {message.author.name} triggered the fractal god response.")
                await message.channel.send("<:fractalGod:783118002009800714>")


def setup(bot):
    bot.add_cog(OnlyPhans(bot))
