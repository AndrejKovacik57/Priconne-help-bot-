import discord
from discord import app_commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached, ClanBattleCantHaveMoreThenFiveDaysError, \
    ObjectDoesntExistsInDBError, PlayerAlreadyInClanError, PlayerNotInClanError, NoActiveCBError
from service.service import Service
from db_model.table_classes import Clan, Player, ClanPlayer, ClanBattle, PlayerCBDayInfo, TeamComposition, Boss, \
    BossBooking,  ClanRole

from .help_functions import multiple_players_check, get_cb_day
from typing import Optional


class CreateGroup(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = Service("priconne_database")

    @app_commands.command(description="Create clan")
    @app_commands.describe(clan_name="Clan to create")
    async def clan(self, interaction: discord.Interaction, clan_name: str):
        """ Create clan """
        try:
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")
            user_roles = interaction.user.roles
            roles = await self.service.get_guild_admin(guild_id)
            roles += await self.service.get_guild_lead(guild_id)
            for user_role in user_roles:
                for role in roles:
                    if user_role.id == role[2]:
                        clan = await self.service.create_clan(clan_name, guild_id)
                        return await interaction.response.send_message(f"Created clan: **{clan.name}**")
            return await interaction.response.send_message('blabla')
        except (ObjectExistsInDBError, ObjectDoesntExistsInDBError) as e:
            embed = discord.Embed(title=f"Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Create player")
    @app_commands.describe(player_name="Player to create")
    async def player(self, interaction: discord.Interaction, player_name: str):
        """ Create player """
        try:
            guild_id = interaction.guild.id
            await self.service.get_guild_by_id(guild_id)
            player = await self.service.create_player(player_name, interaction.user.id)
            embed = discord.Embed(title="Created Player Success!", color=0xffff00,
                                description=f"Created player: **{player.name}**")
            return await interaction.response.send_message(embed=embed, ephemeral=False)

        except (ObjectDoesntExistsInDBError, ObjectExistsInDBError) as e:
            embed = discord.Embed(title=f"Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(description="Create player for someone else")
    @app_commands.describe(player_name="Player to create", discord_id="ID of person to create player for")
    async def playerforyou(self, interaction: discord.Interaction, player_name: str, discord_id: str):
        """ Create player """
        try:
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            user_roles = interaction.user.roles
            roles = await self.service.get_guild_admin(guild_id)
            roles += await self.service.get_guild_lead(guild_id)
            for user_role in user_roles:
                for role in roles:
                    if user_role.id == role[2]:
                        player = await self.service.create_player(player_name, discord_id)
                        embed = discord.Embed(title="Created Player Success!", color=0xffff00,
                                description=f"Created player: **{player.name}** for <@{discord_id}>")
                        return await interaction.response.send_message(embed=embed)
            embed = discord.Embed(title="Error", color=0xff0000,
                                description="""
                    You don't have permission to use this command!
                """)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except (ObjectDoesntExistsInDBError, ObjectExistsInDBError) as e:
            embed = discord.Embed(title=f"Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Create clan battle")
    @app_commands.describe(cb_name="Ex. CB25", start_date="Date format is DD-MM-YYYY")
    async def cb(self, interaction: discord.Interaction, cb_name: str, start_date: str):
        """ Create cb """
        try:
            guild_id = interaction.guild.id
            await self.service.get_guild_by_id(guild_id)
            user_roles = interaction.user.roles
            roles = await self.service.get_guild_admin(guild_id)
            roles += await self.service.get_guild_lead(guild_id)
            for user_role in user_roles:
                for role in roles:
                    if user_role.id == role[2]:
                        clans = await self.service.get_clans(guild_id)
                        for clan in clans:
                            exists = await self.service.exists_cb_in_date_by_clan_id(start_date, clan.clan_id)
                            if exists:
                                embed = discord.Embed(title="Error", color=0xff0000,
                                    description=f"Cant create clan battle because there is clan battle at this date: {exists}")
                                return await interaction.response.send_message(embed=embed, ephemeral=True)
                            cb = await self.service.create_clan_battle(clan.clan_id, cb_name, start_date)
                            cb.active = True
                            cb = await self.service.update_clan_batte(cb)

                            clan_players = await self.service.get_players_from_clan(clan.clan_id)
                            for clan_player in clan_players:
                                for _ in range(5):
                                    await self.service.create_player_cb_day_info(cb.cb_id, clan_player.player_id)
                            for boss_number in range(5):
                                await self.service.create_boss(f'A{boss_number + 1}', boss_number + 1, 1, cb.cb_id)
                            boss1 = await self.service.get_boss_by_boss_number(1, cb.cb_id)
                            boss1.active = True
                            await self.service.update_boss(boss1)
                            embed = discord.Embed(title="Create clan battle success!", color=0xffff00,
                                description=f"Created clan battle for all clans on `{start_date}`")
                            return await interaction.response.send_message(embed=embed, ephemeral=False)
            embed = discord.Embed(title="Error", color=0xff0000,
                                description=f"You don't have permission to use this command!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except (ObjectExistsInDBError, ObjectDoesntExistsInDBError, PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached
                , ObjectDoesntExistsInDBError, ValueError) as e:
            embed = discord.Embed(title=f"Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Create team composition")
    @app_commands.describe(comp="Team composition to create for current day", player_name='Name of your account')
    async def team_composition(self, interaction: discord.Interaction, comp: str, player_name: Optional[str] = None):
        """ Create team composition """
        try:
            await self.service.get_guild_by_id(interaction.guild.id)
            players = await self.service.get_player_by_discord_id(interaction.user.id)
            player = multiple_players_check(player_name, players)
            clan_player = await self.service.get_clan_player(player.player_id)
            clan = clan_player[1]
            cb = await self.service.get_clan_battle_active_by_clan_id(clan.clan_id)
            day_of_cb = get_cb_day(cb)
            if day_of_cb:
                pcdi = await self.service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)
                tc = await self.service.create_team_composition(comp, pcdi.pcbdi_id)

                await interaction.response.send_message(f"Created team compositon: {tc.name}")
            else:
                await interaction.response.send_message(f"Today is not cb day")

        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, ValueError, ObjectDoesntExistsInDBError,
                NoActiveCBError) as e:
            embed = discord.Embed(title=f"Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    bot.tree.add_command(CreateGroup(name="create", description="Create Commands"))