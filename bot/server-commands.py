import discord
from discord import app_commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached, ClanBattleCantHaveMoreThenFiveDaysError, ObjectDoesntExistsInDBError, \
    PlayerAlreadyInClanError, PlayerNotInClanError
from service.service import Service
from db_model.table_classes import Clan, Player, ClanPlayer, ClanBattle, PlayerCBDayInfo, TeamComposition, Boss, BossBooking, \
    ClanRole
from datetime import datetime, timedelta
import pytz


# async def is_admin(interaction: discord.Interaction):
#     has_admin_permissions = interaction.guild.
#     if not has_add_permission:
#         permissionError = discord.Embed(title="Error", color=0xff4f4f, description="You don't have permission to delete this server's account. You need `Administrator` permission to use this.")
#         await ctx.respond(embed=permissionError, view=None)
#     return has_add_permission


class ServerGroup(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = Service("priconne_database")

    @app_commands.command(description="Register server in bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        """ Register server in bot """
        try:
            guild_id = interaction.guild.id
            await self.service.add_server(guild_id)
            embed = discord.Embed(title="Setup", color=0x3083e3, description="Sweet! Your server is set up!")
            await interaction.response.send_message(embed=embed, ephemeral=False)
        except ObjectExistsInDBError as e:
            await interaction.response.send_message(e)

    @setup.error
    async def setup_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            embed = discord.Embed(title="Error", color=0x3083e3, description="You don't have permissions to run this command! Please consult your **server admin**.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Add admin role")
    @app_commands.checks.has_permissions(administrator=True)
    async def addadminrole(self, interaction: discord.Interaction, role_id: str):
        """ Add admin role"""
        try:
            role_id_int = int(role_id)
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")
            await self.service.add_admin_role(guild_id, role_id_int)
            await interaction.response.send_message(f"Added role: <@&{role_id}> to admin role", ephemeral=False)
        except (ParameterIsNullError, ObjectExistsInDBError, ObjectDoesntExistsInDBError, ValueError) as e:
            await interaction.response.send_message(e)

    @addadminrole.error
    async def addadminrole_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            embed = discord.Embed(title="Error", color=0x3083e3, description="You don't have permissions to run this command! Please consult your **server admin**.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Remove admin role")
    @app_commands.checks.has_permissions(administrator=True)
    async def removeadminrole(self, interaction: discord.Interaction, role_id: str):
        """ Remove admin role"""
        try:
            role_id_int = int(role_id)
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")
            await self.service.remove_admin_role(guild_id, role_id_int)
            await interaction.response.send_message(f"Removed role: <@&{role_id}> from admin role", ephemeral=False)
        except (ParameterIsNullError, ObjectExistsInDBError, ObjectDoesntExistsInDBError, ValueError) as e:
            await interaction.response.send_message(e)

    @removeadminrole.error
    async def removeadminrole_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            embed = discord.Embed(title="Error", color=0x3083e3, description="You don't have permissions to run this command! Please consult your **server admin**.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Add lead role")
    async def addleadrole(self, interaction: discord.Interaction, role_id: str):
        """ Add lead role """
        try:
            role_id_int = int(role_id)
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")
            user_roles = interaction.user.roles
            guild_admins = await self.service.get_guild_admin(guild_id)
            for user_role in user_roles:
                for guild_admin in guild_admins:
                    if user_role.id == guild_admin[2]:
                        await self.service.add_lead_role(guild_id, role_id_int)
                        await interaction.response.send_message(f"Added <@&{role_id}> as a lead role!")
                        return
            await interaction.response.send_message(f"You don't have permission to use this command!")
        except (ParameterIsNullError, ObjectExistsInDBError, ObjectDoesntExistsInDBError, ValueError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Remove lead role")
    async def removeleadrole(self, interaction: discord.Interaction, role_id: str):
        """ Remove lead role """
        try:
            role_id_int = int(role_id)
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")
            user_roles = interaction.user.roles
            guild_admins = await self.service.get_guild_admin(guild_id)
            for user_role in user_roles:
                for guild_admin in guild_admins:
                    if user_role.id == guild_admin[2]:
                        await self.service.remove_lead_role(guild_id, role_id_int)
                        await interaction.response.send_message(f"Removed <@&{role_id}> from the lead role!")
                        return
            await interaction.response.send_message(f"You don't have permission to use this command!")
        except (ParameterIsNullError, ObjectExistsInDBError, ObjectDoesntExistsInDBError, ValueError) as e:
            await interaction.response.send_message(e)


async def setup(bot):
    bot.tree.add_command(ServerGroup(name="server", description="Server Commands"))