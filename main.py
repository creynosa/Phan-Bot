import logging
import logging.config
import os
from pathlib import Path

import discord
import yaml
from discord.ext import commands
from dotenv import load_dotenv


def loadEnvironmentVars() -> None:
    """Reads and loads the environment variables specified in the project directory."""
    load_dotenv()


def getLoggingConfig() -> dict:
    """Returns the logging configurations from the project directory."""
    configPath = str(Path.cwd() / 'configurations' / 'logging.yaml')
    with open(configPath, "r") as f:
        loggingConfig = yaml.safe_load(f)
    return loggingConfig


def createLogger() -> logging.Logger:
    """Returns a logger created using the project's logging configuration file."""
    loggingConfig = getLoggingConfig()
    logging.config.dictConfig(loggingConfig)
    projectLogger = logging.getLogger("main")

    return projectLogger


def getSettingsConfig() -> dict:
    """Returns the settings configurations from the project directory."""
    filepath = Path.cwd() / "configurations" / "main.yaml"
    with open(filepath, "r") as f:
        settingsConfig = yaml.safe_load(f)
    return settingsConfig


def isTesting() -> bool:
    """Returns True if the bot configuration is set to run locally."""
    settings = getSettingsConfig()
    return settings["testing"]


def getIntents() -> discord.Intents:
    """Returns all user-specified intents."""
    intents = discord.Intents.all()

    return intents


def getMainBotToken() -> str:
    """Returns the main bot token."""
    return os.environ["BOT_TOKEN"]


def getTestBotToken() -> str:
    """Returns the test bot token."""
    return os.environ["TEST_BOT_TOKEN"]


def createMainBot() -> commands.Bot:
    """Constructs and returns the main discord bot."""
    return commands.Bot(command_prefix="!", intents=getIntents())


def createTestBot() -> commands.Bot:
    """Constructs and returns the test discord bot."""
    return commands.Bot(command_prefix=">", intents=getIntents())


def getMainCogs() -> list[str]:
    """Returns the module names along with the .py extension for all the main cogs."""
    cogModules = os.listdir("cogs")
    return cogModules


def getMainCogsFilepaths() -> list[str]:
    """Returns the filepaths of all the main cogs to be loaded."""
    cogModules = getMainCogs()
    cogFilepaths = [
        f"cogs.{filename[:-3]}"
        for filename in cogModules
        if filename != "__init__.py" and filename.endswith(".py")
    ]

    return cogFilepaths


def getGuildCogs() -> list[str]:
    """Returns the module names along with the .py extension for all the guild cogs."""
    guildCogsFilepath = Path.cwd() / "cogs" / "guilds"
    guildModules = os.listdir(guildCogsFilepath)
    return guildModules


def getGuildCogsFilepaths() -> list[str]:
    """Returns the filepaths of all the guild cogs to be loaded."""
    cogModules = getGuildCogs()
    cogFilepaths = [
        f"cogs.guilds.{filename[:-3]}"
        for filename in cogModules
        if filename != "__init__.py" and filename.endswith(".py")
    ]

    return cogFilepaths


def loadAllCogs(discordBot: commands.Bot) -> None:
    """Loads specified guild modules from the cog directory of the project onto the bot for testing."""
    cogFiles = getMainCogsFilepaths() + getGuildCogsFilepaths()

    logger.info(f"Loading cogs: {cogFiles}")
    for filename in cogFiles:
        discordBot.load_extension(filename)
    logger.info(f"Cogs loaded!")


def initializeMainBot() -> commands.Bot:
    """Initializes the main discord bot."""
    logger.info("Initializing main bot...")

    discordBot = createMainBot()
    loadAllCogs(discordBot)
    discordBot.remove_command("help")

    logger.info("Main bot initialized!")

    return discordBot


def initializeTestBot() -> commands.Bot:
    """Initializes the test discord bot."""
    logger.info("Initializing test bot...")

    discordBot = createTestBot()
    loadAllCogs(discordBot)
    discordBot.remove_command("help")

    logger.info("Test bot initialized!")

    return discordBot


if __name__ == "__main__":
    loadEnvironmentVars()
    logger = createLogger()

    if isTesting():
        logger.info("Running in test mode.")
        token = getTestBotToken()
        bot = initializeTestBot()
    else:
        logger.info("Running in non-test mode.")
        token = getMainBotToken()
        bot = initializeMainBot()


    @bot.event
    async def on_ready():
        """Print a console message when the bot is ready and active."""
        logger.info("Bot successfully started!")


    @bot.event
    async def on_message(message: discord.Message):
        """Executes certain code blocks upon a message being sent."""
        # Ignore the bot's own messages.
        if message.author == bot.user:
            return

        await bot.process_commands(message)


    bot.run(token)
