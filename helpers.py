import functools

import discord


def makeSimpleTextEmbed(text: str) -> discord.Embed:
    """Returns a simple embed containing text."""
    embed = discord.Embed(description=text, color=0xFFFFFF)
    return embed


def makeSimpleImageEmbed(imageURL: str) -> discord.Embed:
    """Returns a simple embed containing a picture from an url."""
    embed = discord.Embed(color=0xFFFFFF)
    embed.set_image(url=imageURL)
    return embed


def logCommand(logger, logArgs=False):
    """A wrapper used to capture user and guild information when a command is used."""

    def inner(func):
        @functools.wraps(func)
        async def wrapper(*func_args, **func_kwargs):
            ctx = func_args[1]
            user = ctx.author
            guild = ctx.guild
            logger.info(
                f"{user} used the {func.__name__} command in {guild.name}. User ID: {user.id}, Guild ID: {guild.id}")
            if logArgs:
                logger.debug(f"Args: {func_args[2:]}, Kwargs: {func_kwargs}")

            return await func(*func_args, **func_kwargs)

        return wrapper

    return inner
