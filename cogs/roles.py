# A module containing various commands and listeners for use with
# role-assignment embedded messages.


import logging
from pathlib import Path

import discord
import yaml
from discord.ext import commands

from helpers import logoURL, embedMessage

logger = logging.getLogger("main.role_assignment")


class RoleAssignment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.configPath = str(Path.cwd() / "resources" / "role_assignment.yaml")
        self.config = None
        self.guild = None
        self.channel = None

    def cacheValues(self):
        self.setConfig()
        self.setGuild()
        self.setChannel()

    def setConfig(self) -> None:
        """Sets the role assignment configurations."""
        with open(self.configPath, "r") as f:
            config = yaml.safe_load(f)

        self.config = config

    def setGuild(self) -> None:
        """Sets the Guild object."""
        guildID = self.config['guildID']
        guild = self.bot.get_guild(guildID)

        self.guild = guild

    def setChannel(self) -> None:
        """Sets the role assignment GuildChannel object."""
        channelID = self.config['channelID']
        channel = self.guild.get_channel_or_thread(channelID)

        self.channel = channel

    def saveConfig(self):
        """Saves the cached role assignment configurations to file."""
        with open(self.configPath, "w") as f:
            yaml.dump(self.config, f)

    def createRoleAssignmentEmbed(self):
        """Creates the main embed showing all roles available for assignment."""
        categories = list(self.config["roles"].keys())  # Currently only "Games" and "General"

        categoryRoles = {}  # {str: list,...}
        for category in categories:
            roleNames = list(self.config["roles"][category].keys())  # role names under each category
            roleNames = [f"`{roleName}`" for roleName in roleNames]
            categoryRoles[category] = roleNames

        embed = discord.Embed(title="Available Roles")
        embed.set_author(name="PhanBot", icon_url=logoURL)

        for category, roleNames in categoryRoles.items():
            rolesString = '\n'.join(roleNames)  # format necessary for discord embeds
            embed.add_field(name=category, value=rolesString)

        embed.set_footer(
            text="Use !role add <role> or !role remove <role> to add or remove a role."
        )

        return embed

    @commands.command(name='roles')
    async def _roles(self, ctx):
        await self.channel.send(embed=self.createRoleAssignmentEmbed())

    @commands.group(name='role')
    async def _role(self, ctx):
        if ctx.invoked_subcommand is None:
            return

    @_role.command(name='add')
    async def _role_add(self, ctx, roleName: str):
        """Adds a role to a given member."""
        member = ctx.author

        logger.info(f"Member {member.mention} used the !add command for role: {roleName}")

        if roleName.lower() == 'all':
            pass

        try:
            role = self.getRoleFromRoleName(roleName)
        except:
            messageText = f"Sorry, could not find the role: {roleName}. Please try again!"
            messageEmbed = embedMessage(messageText)
            msg = await ctx.send(embed=messageEmbed)
            return

        if self.memberHasRole(member, role):
            logger.debug(f"Member {member.mention} already has the role: {roleName}")

            messageText = 'You already have that role!'
        else:
            logger.debug(f"Adding role {roleName} to member {member.mention} ")

            await self.addRoleToMember(member, role)
            messageText = f'Added the {role.mention} role to {member.mention}!'

        messageEmbed = embedMessage(messageText)
        msg = await ctx.send(embed=messageEmbed)

    @_role.command(name='remove')
    async def _role_remove(self, ctx, roleName: str):
        """Removes a role from a given member."""

        member = ctx.author
        try:
            role = self.getRoleFromRoleName(roleName)
        except:
            messageText = "Sorry, could not find that role. Please try again!"
            messageEmbed = embedMessage(messageText)
            msg = await ctx.send(embed=messageEmbed)
            return

        if self.memberHasRole(member, role):
            await self.removeRoleFromMember(member, role)
            messageText = f"Removed the {role.mention} role from {member.mention}!"
        else:
            messageText = "You don't have that role!"

        messageEmbed = embedMessage(messageText)
        msg = await ctx.send(embed=messageEmbed)

    def getFullRolesDict(self) -> dict:
        """Gets the full dictionary of roles and their IDs without their categories."""
        roleDicts = self.config['roles']

        allRoles = {}
        for _, roles in roleDicts.items():
            allRoles = allRoles | roles

        return allRoles

    def getRoleFromRoleName(self, roleName: str) -> discord.Role:
        """Returns the Role object for a specified role."""
        allRoles = self.getFullRolesDict()
        roleID = allRoles[roleName]

        return self.guild.get_role(roleID)

    @staticmethod
    def memberHasRole(member: discord.Member, role: discord.Role) -> bool:
        return role in member.roles

    @staticmethod
    async def addRoleToMember(member: discord.Member, role: discord.Role) -> None:
        """Adds a given role to a member."""

        oldRoles = member.roles
        newRoles = oldRoles + [role]

        await member.edit(roles=newRoles)

    @staticmethod
    async def removeRoleFromMember(member: discord.Member, role: discord.Role) -> None:
        oldRoles = member.roles
        newRoles = [oldRole for oldRole in oldRoles if oldRole != role]

        await member.edit(roles=newRoles)

    @commands.Cog.listener()
    async def on_ready(self):
        self.cacheValues()


async def setup(bot):
    await bot.add_cog(RoleAssignment(bot))
