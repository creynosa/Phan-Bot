import logging

from discord.ext import commands
from main import getGuildCogs, getMainCogs

logger = logging.getLogger("main.owner")


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx) -> None:
        """Global check to see if the guild utilizing the commands is the bot owner."""
        return await self.bot.is_owner(ctx.author)

    @commands.group()
    async def module(self, ctx) -> None:
        """Initializes the module command group."""
        if ctx.invoked_subcommand is None:
            return

    @module.command(name="load")
    async def _load(self, ctx, moduleName: str) -> None:
        """Loads a cog onto the bot."""
        logger.info(f"{ctx.author.name} used the module load command. Module: {moduleName}")
        logger.info(f"Loading {moduleName}.py...")

        pretext = self.getModulePretext(moduleName)
        if pretext is None:
            logger.info(f"Module {moduleName}.py not found.")
            await ctx.send("No such module exists.")

        try:
            self.bot.load_extension(pretext + moduleName)
            logger.info(f"Module {moduleName}.py was loaded.")
            await ctx.send(f"Loaded module {moduleName}!")
        except:
            logger.info(f"Module {moduleName}.py was already loaded.")
            await ctx.send(f"The {moduleName} module is already loaded.")

    @module.command(name="unload")
    async def _unload(self, ctx, moduleName: str) -> None:
        """Unloads a cog from the bot."""
        logger.info(f"{ctx.author.name} used the module unload command. Module: {moduleName}")
        logger.info(f"Unloading {moduleName}.py...")

        pretext = self.getModulePretext(moduleName)
        if pretext is None:
            logger.info(f"Module {moduleName}.py not found.")
            await ctx.send("No such module exists.")

        try:
            self.bot.unload_extension(pretext + moduleName)
            logger.info(f"Module {moduleName}.py was unloaded.")
            await ctx.send(f"Unloaded the {moduleName} module from the bot!")
        except:
            logger.info(f"Module {moduleName}.py was already unloaded.")
            await ctx.send(f"The {moduleName} module is already unloaded.")

    @module.command(name="reload")
    async def _reload(self, ctx, moduleName: str) -> None:
        """Reloads a cog on the bot."""
        logger.info(f"{ctx.author.name} used the module reload command. Module: {moduleName}")
        logger.info(f"Reloading {moduleName}.py...")

        pretext = self.getModulePretext(moduleName)
        if pretext is None:
            logger.info(f"Module {moduleName}.py not found.")
            await ctx.send("No such module exists.")

        try:
            self.bot.unload_extension(pretext + moduleName)
            logger.info(f"Module {moduleName}.py unloaded. Proceeding to load module...")
        except:
            logger.info(
                f"Module {moduleName}.py was already unloaded. Proceeding to load module..."
            )

        self.bot.load_extension(pretext + moduleName)
        logger.info(f"Module {moduleName}.py was loaded.")

        logger.info(f"Module {moduleName} reloaded successfully!")
        await ctx.send(f"Reloaded module {moduleName}!")

    @staticmethod
    def getModulePretext(module: str) -> str:
        """Returns the relative path for the modules in dot format. Excludes the filename."""
        mainCogs = getMainCogs()
        guildCogs = getGuildCogs()

        moduleNameExt = module + ".py"
        if moduleNameExt in mainCogs:
            pretext = "cogs."
        elif moduleNameExt in guildCogs:
            pretext = "cogs.guilds."
        else:
            pretext = None

        return pretext


def setup(bot):
    bot.add_cog(Owner(bot))
