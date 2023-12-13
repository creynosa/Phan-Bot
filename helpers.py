from datetime import datetime

import pytz
from discord import Embed

# URL to the discord bot's profile picture
logoURL = 'https://i.imgur.com/CkAoqD2.png'


def convertToCST(date: datetime) -> datetime:
    """Converts a naive datetime object to CST."""
    central = pytz.timezone("US/Central")
    datetimeUTC = date.replace(tzinfo=pytz.utc)

    datetimeCST = datetimeUTC.astimezone(central)
    return datetimeCST


def getDatetimeString(date: datetime) -> str:
    """Retrieves a readable representation of a datetime object."""

    return date.strftime("%m/%d/%y at %I:%M %p %Z")


def embedMessage(text: str) -> Embed:
    """Returns a simple embed containing text or a picture."""
    if text.startswith("http"):
        embed = Embed(color=0xFFFFFF)
        embed.set_image(url=text)
    else:
        embed = Embed(description=text, color=0xFFFFFF)

    embed.set_author(name="PhanBot", icon_url=logoURL)

    return embed
