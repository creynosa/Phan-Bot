import calendar
import logging
import random

import discord
import pytz
from discord.ext import commands

logger = logging.getLogger("main.fun")


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='itschristmastime')
    @commands.is_owner()
    async def _itschristmastime(self, ctx, off=None):
        guild = ctx.guild
        channels = guild.channels

        emote_list = ['🔔', '🎁', '🎅', '❄️', '⛄', '🌟', '🎄']

        for channel in channels:
            try:
                prev_name = channel.name
                prev_name = ''.join([char for char in prev_name if char not in emote_list])

                if not off:
                    random_emote = random.choice(emote_list)
                    await channel.edit(name=f'{random_emote}{prev_name}')

                await channel.edit(name=f'{prev_name}')
            except Exception:
                continue

        logger.debug('Christmastifying done!')

    @commands.command()
    async def say(self, ctx, *, text):
        """Makes the bot repeat whatever the user inputted in a given channel."""
        await ctx.message.delete()

        await ctx.send(text)

    @staticmethod
    def embedMessage(text: str) -> discord.Embed:
        """Returns a simple embed containing text or a picture."""
        if text.startswith("http"):
            embed = discord.Embed(color=0xFFFFFF)
            embed.set_image(url=text)
        else:
            embed = discord.Embed(description=text, color=0xFFFFFF)

        return embed

    @commands.command()
    async def pusher(self, ctx):
        embed = self.embedMessage("https://i.imgur.com/0mHp2wx.png")
        await ctx.send(embed=embed)

    @commands.command(name='manicc')
    async def _manicc(self, ctx):
        links = ['https://i.imgur.com/k94JJVU.png',
                 'https://i.imgur.com/VJr3GxN.png']
        embed = self.embedMessage(random.choice(links))
        await ctx.send(embed=embed)

    @commands.command(name='crab')
    async def _crab(self, ctx):
        logger.debug("entering crab command")

        member = ctx.author

        try:
            member_global_name = member.global_name
        except Exception as e:
            logger.debug(f"Error in obtaining global name: {e}")

        logger.debug(
            f"User Info -- name: {member.name}, member display name: {member.display_name}, member nickname: {member.nick}")
        logger.debug(f"{member.display_name} just used the crab command")

        old_display_name = member.display_name
        new_display_name = f"🦀{old_display_name}🦀"

        logger.debug(f"new display name: {new_display_name}")

        logger.debug("editing nickname")
        try:
            await member.edit(nick=new_display_name)
        except Exception as e:
            logger.debug(f"nicknaming error: {e}")
            return

        logger.debug("nickname successfully changed. leaving command")

    @commands.command()
    async def tierlist(self, ctx, target_page: int = 1):
        central = pytz.timezone("US/Central")
        guild = ctx.guild

        memberAges = []
        for member in guild.members:
            memberID = member.id
            memberName = member.mention
            if memberID in (200393280779714560, 1078495978983788685):
                continue
            memberAgeUTC = member.joined_at.replace(tzinfo=pytz.utc)
            memberAges.append([memberName, memberAgeUTC])

        logger.debug(f"{memberAges=}")
        memberAges = sorted(memberAges, key=lambda x: x[1])

        membersString = ""
        agesString = ""
        i = 1
        for (member, age) in memberAges:
            if i == 13:
                i += 1
                continue

            membersString += f"{i}. {member}\n"

            agesUnixTimestamp = calendar.timegm(age.utctimetuple())
            agesString += f"{i}. <t:{agesUnixTimestamp}:F>\n"

            i += 1

            # ageCST = age.astimezone(central).strftime("%m/%d/%y at %I:%M %p")
            # agesString += f"{ageCST}\n"

        memberLines = membersString.split("\n")
        memberLines.insert(0, "1. <@!1078495978983788685>")
        memberLines.insert(12, "13. <@!200393280779714560>")

        ageLines = agesString.split("\n")
        ageLines.insert(0, "1. omegalol")
        ageLines.insert(12, "13. omegalol")

        numEmbeds, extraEmbeds = divmod(len(memberLines), 20)
        if extraEmbeds != 0:
            numEmbeds += 1

        tierlistEmbeds = []
        page = 0
        for i in range(numEmbeds):
            page += 1

            try:
                memberString = "\n".join(memberLines[:20])
                memberLines = memberLines[20:]
            except IndexError:
                pass

            try:
                ageString = "\n".join(ageLines[:20])
                ageLines = ageLines[20:]
            except IndexError:
                pass

            newEmbed = discord.Embed(title=f"Member Tier List", color=0xFFFFFF)
            newEmbed.add_field(name="Member", value=memberString)
            newEmbed.add_field(name="Joined On (CST)", value=ageString)
            newEmbed.set_footer(text=f"Page {page} of {numEmbeds}")

            tierlistEmbeds.append(newEmbed)

        target_embed = tierlistEmbeds[target_page - 1]
        await ctx.send(embed=target_embed)

    @commands.command()
    async def me(self, ctx):

        logger.debug(f"Entering '!me' command")

        logger.debug(f"Retrieving author info...")
        author = ctx.author
        authorID = ctx.author.id
        authorPFPUrl = ctx.author.avatar.url
        guildID = ctx.guild.id

        logger.debug(f"Retrieving joined_at data...")
        joinedOn = author.joined_at.replace(tzinfo=pytz.utc)
        joinedOnUnix = calendar.timegm(joinedOn.utctimetuple())
        joinedOnString = f"<t:{joinedOnUnix}:F>"

        premiumSince = author.premium_since

        logger.debug(f"Retrieving roles...")
        topRole = author.top_role
        roleString = f" {topRole.mention}"

        logger.debug(f"Generating embed...")
        embed = discord.Embed(title="Member Information", color=author.color.value)
        embed.set_thumbnail(url=authorPFPUrl)
        embed.set_author(name=author, icon_url=authorPFPUrl)
        embed.add_field(name="Username", value=author.name)
        embed.add_field(name="Nickname", value=author.nick)
        if roleString != "":
            embed.add_field(name="Top Role", value=roleString)
        # embed.add_field(name="User ID", value=authorID)
        embed.add_field(name="Joined On", value=joinedOnString)

        # if guildID == 733944519640350771:
        #     heckConfigPath = str(Path.cwd() / "resources" / "hecks.yaml")
        #     with open(heckConfigPath, "r") as f:
        #         heckConfig = yaml.safe_load(f)
        #     timesHecking = heckConfig["memberID"][authorID]["heckCount"]
        #     timesHecked = heckConfig["memberID"][authorID]["heckedCount"]
        #     embed.add_field(name="Times Hecking", value=timesHecking)
        #     embed.add_field(name="Times Hecked", value=timesHecked)

        if premiumSince is not None:
            premiumSince = premiumSince.replace(tzinfo=pytz.utc)
            premiumSinceUnix = calendar.timegm(premiumSince.utctimetuple())
            premiumSinceString = f"<t:{premiumSinceUnix}:F>"
            embed.add_field(name="Boosting Since", value=premiumSinceString)

        await ctx.send(embed=embed)

    @commands.command(name="8ball")
    async def _8ball(self, ctx, *, text=None):
        logger.debug(f"Entering 8ball command...")
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
        embedAnswer = self.embedMessage(answer)

        await ctx.send(embed=embedAnswer)

    # def downloadConfig(self):
    #     s3.download_file("phanbot", "colorme.yaml", self.configPath)
    #
    # def uploadConfig(self):
    #     s3.upload_file(self.configPath, "phanbot", "colorme.yaml")
    #
    # def setConfig(self):
    #     with open(self.configPath, "r") as f:
    #         config = yaml.safe_load(f)
    #     return config
    #
    # def saveConfig(self):
    #     with open(self.configPath, "w") as f:
    #         yaml.dump(self.config, f)
    #
    # @commands.group()
    # @isOnlyPhans()
    # async def colorme(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         text = 'Available Commands: \n\n ' \
    #                '!colorme help \n ' \
    #                '!colorme add `<color hex code>` `<role name>`\n ' \
    #                '!colorme remove \n ' \
    #                '!colorme change name `<new role name>`\n ' \
    #                '!colorme change color `<color hex code>`'
    #         await ctx.send(embed=self.embedMessage(text))
    #
    # @colorme.command(name='help')
    # @isOnlyPhans()
    # async def _colorme_help(self, ctx):
    #     text = 'This command requires you to input a hex code for your color. Please utilize this website and ' \
    #            'copy/paste the hex code when prompted including the hashtag: https://htmlcolorcodes.com/ \n\n' \
    #            'Command to add colored role: `!color add <color hex code> <role name>`'
    #     embed = self.embedMessage(text)
    #     await ctx.send(embed=embed)
    #
    # @colorme.command(name='add')
    # @isOnlyPhans()
    # async def _add(self, ctx, color: str, *, roleName: str):
    #     """Creates a role with no permissions with a given color."""
    #     try:
    #         assert ctx.author.id in self.config
    #     except AssertionError:
    #         self.config[ctx.author.id] = {
    #             'hasRole': False,
    #             'roleName': None,
    #             'roleColor': None,
    #         }
    #         self.saveConfig()
    #
    #     if self.config[ctx.author.id]['hasRole']:
    #         errorMessage = 'Sorry, looks like you already have a colored role.'
    #         await ctx.send(embed=self.embedMessage(errorMessage))
    #         return
    #
    #     print(f"{roleName=}")
    #     validRoleNameRegex = re.compile(r"^[a-zA-Z \d]*$")
    #     if not re.match(validRoleNameRegex, roleName):
    #         text = 'Invalid role name. Please try again.'
    #         await ctx.send(embed=self.embedMessage(text))
    #         return
    #
    #     print(f"{color=}")
    #     validColorRegex = re.compile(r"^#[a-zA-Z\d]{6}$")
    #     if not re.match(validColorRegex, color):
    #         text = 'Invalid hex code. Please try again and make sure the hashtag is included.' \
    #                "Make sure to use https://htmlcolorcodes.com/ for your hex code selection."
    #         await ctx.send(embed=self.embedMessage(text))
    #         return
    #
    #     rgbValues = ImageColor.getrgb(color)
    #     Color = discord.Color.from_rgb(*rgbValues)
    #     guild = ctx.guild
    #     newRole = await guild.create_role(name=roleName, color=Color, mentionable=True)
    #     await ctx.author.add_roles(newRole)
    #     await ctx.send(embed=self.embedMessage('Role added!'))
    #
    #     self.config[ctx.author.id]['roleName'] = roleName
    #     self.config[ctx.author.id]['color'] = color
    #     self.config[ctx.author.id]['hasRole'] = True
    #     self.config[ctx.author.id]['roleID'] = newRole.id
    #     self.saveConfig()
    #     self.uploadConfig()
    #
    # @colorme.command(name='remove')
    # @isOnlyPhans()
    # async def _colorme_remove(self, ctx):
    #     roleID = self.config[ctx.author.id]['roleID']
    #     role = ctx.guild.get_role(roleID)
    #
    #     await ctx.author.remove_roles(role)
    #     await role.delete()
    #     message = 'Role removed!'
    #     await ctx.send(embed=self.embedMessage(message))
    #
    #     self.config.pop(ctx.author.id)
    #     self.saveConfig()
    #     self.uploadConfig()
    #
    # @colorme.group()
    # async def change(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         return
    #
    # @change.command(name='name')
    # @isOnlyPhans()
    # async def _colorme_change_name(self, ctx, *, roleName: str):
    #     validRoleNameRegex = re.compile(r"^[a-zA-Z \d]*$")
    #     if not re.match(validRoleNameRegex, roleName):
    #         text = 'Invalid role name. Please try again.'
    #         await ctx.send(embed=self.embedMessage(text))
    #         return
    #
    #     roleID = self.config[ctx.author.id]['roleID']
    #     role = ctx.guild.get_role(roleID)
    #
    #     await role.edit(name=roleName)
    #     self.config[ctx.author.id]['roleName'] = roleName
    #     message = 'Role name changed!'
    #     await ctx.send(embed=self.embedMessage(message))
    #
    #     self.saveConfig()
    #     self.uploadConfig()
    #
    # @change.command(name='color')
    # @isOnlyPhans()
    # async def _colorme_change_color(self, ctx, *, color: str):
    #     validColorRegex = re.compile(r"^#[a-zA-Z\d]{6}$")
    #     if not re.match(validColorRegex, color):
    #         text = 'Invalid hex code. Please try again and make sure the hashtag is included. ' \
    #                "Make sure to use https://htmlcolorcodes.com/ for your hex code selection."
    #         await ctx.send(embed=self.embedMessage(text))
    #         return
    #
    #     roleID = self.config[ctx.author.id]['roleID']
    #     role = ctx.guild.get_role(roleID)
    #
    #     rgbValues = ImageColor.getrgb(color)
    #     Color = discord.Color.from_rgb(*rgbValues)
    #
    #     await role.edit(color=Color)
    #     self.config[ctx.author.id]['roleColor'] = color
    #     message = 'Role color changed!'
    #     await ctx.send(embed=self.embedMessage(message))
    #
    #     self.saveConfig()
    #     self.uploadConfig()


async def setup(bot):
    await bot.add_cog(Fun(bot))
