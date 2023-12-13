import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from logs import loggers

logger = loggers.createLogger("main")


def loadEnvironmentVars() -> None:
    """Loads environment variables from the directory's env file"""
    load_dotenv('.env')


def getIntents() -> discord.Intents:
    """Returns customized intents for the discord bot."""
    customIntents = discord.Intents.all()

    return customIntents


def getToken() -> str:
    tokenName = "PHAN-BOT-TOKEN"

    return os.environ[tokenName]


def createBot() -> commands.Bot:
    """Creates the discord bots."""
    prefix = "!"
    logger.debug(f"Prefix set to {prefix}")
    customIntents = getIntents()

    return commands.Bot(command_prefix=prefix, intents=customIntents, help_command=None)


async def loadCogs(discordBot: commands.Bot) -> None:
    """Loads all the included cogs when ready."""
    cogFiles = os.listdir("cogs")

    for filename in cogFiles:
        if filename.endswith(".py") and filename != "__init__.py":
            cogName = filename[:-3]
            await discordBot.load_extension(f"cogs.{cogName}")
            logger.debug(f"Loaded the {cogName} cog.")


async def startBot():
    """Creates a coroutine used to start the discord bot."""
    logger.info("Initializing bot...")
    await loadCogs(bot)

    async with bot:
        token = getToken()
        await bot.start(token)

        @bot.event
        async def on_message(self, message: discord.Message):
            """Executes certain code blocks upon a message being sent."""
            if message.author == self.bot.user:
                return
            await bot.process_commands(message)


if __name__ == "__main__":
    loadEnvironmentVars()

    bot = createBot()
    asyncio.run(startBot())
