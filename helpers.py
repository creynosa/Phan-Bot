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
