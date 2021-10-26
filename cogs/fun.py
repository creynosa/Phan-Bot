import logging
import random
import re
from typing import Optional

import discord
from discord.ext import commands

import helpers

logger = logging.getLogger("main.fun")


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def thanoscat(self, ctx) -> None:
        """Sends an image of a cat crying while being thanosed."""
        logger.info(f"{ctx.author.name} used the thanoscat command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/z2RtWzN.jpg")
        await ctx.send(embed=embed)

    @commands.command()
    async def caprikachu(self, ctx) -> None:
        logger.info(f"{ctx.author.name} used the caprikachu command.")
        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/aqe7pfU.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def hi(self, ctx):
        logger.info(f"{ctx.author.name} used the hi command.")
        embed = helpers.makeSimpleTextEmbed("Hi! It me, Phan Bot :)")
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        logger.info(f"{ctx.author.name} used the ping command.")
        embed = helpers.makeSimpleTextEmbed("Pong!")
        await ctx.send(embed=embed)

    @commands.command()
    async def ily(self, ctx):
        logger.info(f"{ctx.author.name} used the ily command.")
        embed = helpers.makeSimpleTextEmbed("I love you more! :heart:")
        await ctx.send(embed=embed)

    @commands.command()
    async def beep(self, ctx):
        logger.info(f"{ctx.author.name} used the beep command.")

        embed = helpers.makeSimpleTextEmbed("Boop boop!")
        await ctx.send(embed=embed)

    @commands.command()
    async def hackermanz(self, ctx):
        logger.info(f"{ctx.author.name} used the hackermanz command.")

        embed = helpers.makeSimpleImageEmbed("https://i.imgur.com/TuN1P65.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def popo(self, ctx):
        logger.info(f"{ctx.author.name} used the popo command.")

        embed = helpers.makeSimpleTextEmbed(
            ":rotating_light: Woop\-woop! :rotating_light: Dats the sound of da police! :police_car:"
        )
        await ctx.send(embed=embed)

    # ====================================================================================
    # ====================================================================================
    # ROLL COMMAND AND HELPERS

    @commands.command()
    async def roll(self, ctx, dieRoll: str = None) -> None:
        """Rolls a 20-sided die by default, otherwise rolls a die specified by the user in DND die-roll format. (Example: 2d10, 5d5)"""
        logger.info(f"{ctx.author.name} used the roll command. Arguments: {dieRoll}")

        if dieRoll is not None:
            try:
                die, faces = self.getDieAndFaces(dieRoll)
            except TypeError:
                await self.sendWrongDieFormatMsg(ctx)
                return
        else:
            die, faces = 1, 20

        if not self.isValidRoll(die, faces):
            await self.sendDieRollErrorMsg(ctx, die, faces)
            return

        rolls = self.generateRolls(die, faces)
        text = self.generateRollsString(rolls)
        rollsEmbed = helpers.makeSimpleTextEmbed(text)

        await ctx.send(embed=rollsEmbed)

    @staticmethod
    def getDieAndFaces(dieRoll: str) -> Optional[tuple]:
        """Returns the number of die and faces to use when given a DND-like dieroll format."""
        rollRegex = re.compile(r"(\d*)d(\d*)")
        match = re.search(rollRegex, dieRoll)
        logger.debug(f"{match=}")

        if match is None:
            return None

        numDie = int(match.group(1))
        numFaces = int(match.group(2))

        logger.debug(f"{numDie=}, {numFaces=}")
        return (numDie, numFaces)

    @staticmethod
    def isValidRoll(die: int, faces: int) -> bool:
        """Determines is a roll is valid or not."""
        logger.debug("Validating die roll...")

        if die == 0 or faces == 0:
            logger.debug("Invalid die roll.")
            return False
        if die is None or faces is None:
            logger.debug("Invalid die format.")
            return False
        else:
            logger.debug("Valid die roll!")
            return True

    async def sendDieRollErrorMsg(self, ctx, die: int, faces: int) -> None:
        """Sends the appropriate error message regarding an invalid roll."""
        if die == 0 and faces == 0:
            logger.info("Sending error message to user: Incorrect number of die and faces.")
            await self.sendInvalidNumDieAndNumFacesMsg(ctx)
        elif die == 0:
            logger.info("Sending error message to user: Incorrect number of die.")
            await self.sendInvalidNumDieMsg(ctx)
        elif faces == 0:
            logger.info("Sending error message to user: Incorrect number of faces.")
            await self.sendInvalidNumFacesMsg(ctx)
        elif die is None or faces is None:
            logger.info("Sending error message to user: Incorrect die roll format.")
            await self.sendWrongDieFormatMsg(ctx)
        logger.info(f"Error message sent!")

    async def sendWrongDieFormatMsg(self, ctx) -> None:
        """Alerts the user that the roll specified is in an invalid format."""
        text = "Incorrect die roll format. Please try again. \n\n Examples: 2d20, 1d20, 3d40."
        errorEmbed = discord.Embed(description=text, color=0xFFFFFF)
        await ctx.send(embed=errorEmbed)

    async def sendInvalidNumFacesMsg(self, ctx) -> None:
        """Alerts the user that the number of faces they specified is invalid."""
        text = "Sorry, the number of faces you specified is invalid. Please try again."
        errorEmbed = discord.Embed(description=text, color=0xFFFFFF)
        await ctx.send(embed=errorEmbed)

    async def sendInvalidNumDieMsg(self, ctx) -> None:
        """Alerts the user that the number of die they specified is invalid."""
        text = "Sorry, the number of die you specified is invalid. Please try again."
        errorEmbed = discord.Embed(description=text, color=0xFFFFFF)
        await ctx.send(embed=errorEmbed)

    async def sendInvalidNumDieAndNumFacesMsg(self, ctx) -> None:
        """Alerts the user that the number of die and faces they specified is invalid."""
        text = "Sorry, the number of die and faces you specified is invalid. Please try again."
        errorEmbed = discord.Embed(description=text, color=0xFFFFFF)
        await ctx.send(embed=errorEmbed)

    @staticmethod
    def generateRolls(die: int, faces: int) -> list:
        """Generates a list of rolls given the number of die and faces."""
        rolls = []
        for _ in range(die):
            roll = random.randint(1, faces)
            rolls.append(roll)

        return rolls

    @staticmethod
    def generateRollsString(rolls: list) -> str:
        """Generates text indicating what the user rolled."""
        rolls = [str(roll) for roll in rolls]
        if len(rolls) == 1:
            text = f"You rolled: {rolls[0]}"
        elif len(rolls) == 2:
            text = f"You rolled: {rolls[0]} and {rolls[1]}"
        elif len(rolls) >= 3:
            text = f"You rolled: {', '.join(rolls[:-1])} and {rolls[-1]}"
        return text

    # ====================================================================================

    @commands.command(name="8ball")
    async def _8ball(self, ctx, *, question: str) -> None:
        """Responds with a magic 8ball command when the user uses this command."""
        logger.info(f"{ctx.author.name} used the 8ball command. Arguments: {question}")

        responses = {
            1: "It is certain",
            2: "Outlook good",
            3: "You may rely on it",
            4: "Ask again later",
            5: "Concentrate and ask again",
            6: "Reply hazy, try again",
            7: "My reply is no",
            8: "My sources say no",
        }

        randomNum = random.randint(1, 8)
        answer = responses[randomNum]
        embedAnswer = helpers.makeSimpleTextEmbed(answer)

        await ctx.send(embed=embedAnswer)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Executes certain code blocks upon a message being sent."""
        if message.author == self.bot.user:
            return

        elif message.content.startswith("!"):
            targetEmote = message.content[1:].lower()
            guild = message.guild

            animatedEmotes = [
                str(emoji).lower() for emoji in guild.emojis if str(emoji).startswith("<a:")
            ]
            for emote in animatedEmotes:
                if f":{targetEmote}:" in emote:
                    logger.info(
                        f"{message.author.name} triggered an emote. Command: {message.content}"
                    )
                    await message.channel.send(emote)
                    return


def setup(bot):
    bot.add_cog(Fun(bot))
