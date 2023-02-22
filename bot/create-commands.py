import discord
from discord import app_commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached, ClanBattleCantHaveMoreThenFiveDaysError, \
    ObjectDoesntExistsInDBError, PlayerAlreadyInClanError, PlayerNotInClanError, NoActiveCBError
from service.service import Service
from db_model.table_classes import Clan, Player, ClanPlayer, ClanBattle, PlayerCBDayInfo, TeamComposition, Boss, \
    BossBooking,  ClanRole
from datetime import datetime, timedelta
import pytz
from .help_functions import multiple_players_check
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
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            user_roles = interaction.user.roles
            roles = await self.service.get_guild_admin(guild_id)
            roles += await self.service.get_guild_lead(guild_id)
            for user_role in user_roles:
                for role in roles:
                    if user_role.id == role[2]:
                        clan = await self.service.create_clan(clan_name, guild_id)
                        await interaction.response.send_message(f"Created clan: **{clan.name}**")
                        break
                else:
                    continue
                # This will be executed only if the inner loop was terminated by break
                break
            # await interaction.response.send_message('blabla')
        except (ObjectExistsInDBError, TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Create player")
    @app_commands.describe(player_name="Player to create")
    async def player(self, interaction: discord.Interaction, player_name: str):
        """ Create player """
        try:
            await self.service.get_guild_by_id(interaction.guild.id)
            player = await self.service.create_player(player_name, interaction.user.id)
            await interaction.response.send_message(f"Created player: **{player.name}**")

        except (TableEntryDoesntExistsError, ObjectExistsInDBError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Create clan battle")
    @app_commands.describe(cb_name="Clan battle name", start_date="date format is DD-MM-YYYY")
    async def cb(self, interaction: discord.Interaction, cb_name: str, start_date: str):
        """ Create cb """
        try:
            await self.service.get_guild_by_id(interaction.guild.id)
            clan = await self.service.get_clan_by_guild(interaction.guild_id)
            cb = await self.service.create_clan_battle(clan.clan_id, cb_name, start_date)
            clan_players = await self.service.get_players_from_clan(clan.clan_id)

            for clan_player in clan_players:
                for _ in range(5):
                    await self.service.create_player_cb_day_info(cb.cb_id, clan_player.player_id)
            for boss_number in range(5):
                await self.service.create_boss(f'A{boss_number + 1}', boss_number + 1, 1, cb.cb_id)
            boss1 = await self.service.get_boss_by_boss_number(1, cb.cb_id)
            boss1.active = True
            await self.service.update_boss(boss1)

            await interaction.response.send_message(f"Created clan battle start: {cb.start_date}, end: {cb.end_date}, "
                                                    f"bosses and player tables")
        except (ObjectExistsInDBError, TableEntryDoesntExistsError, PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached
                , TableEntryDoesntExistsError, ValueError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Create team composition")
    @app_commands.describe(tc_name="Team composition to create for current day", player_name='Name of your account')
    async def team_composition(self, interaction: discord.Interaction, tc_name: str, player_name: Optional[str] = None):
        """ Create team composition """
        try:
            await self.service.get_guild_by_id(interaction.guild.id)
            clan = await self.service.get_clan_by_guild(interaction.guild_id)
            cb = await self.service.get_clan_battle_active_by_clan_id(clan.clan_id)
            players = await self.service.get_player_by_discord_id(interaction.user.id)
            player = multiple_players_check(player_name, players)

            utc = pytz.UTC  # Create a UTC timezone object
            current_time_object = datetime.now(tz=utc).date()
            start_date_object = datetime.strptime(cb.start_date, "%d-%m-%Y").date()
            end_date_object = datetime.strptime(cb.end_date, "%d-%m-%Y").date()
            if start_date_object <= current_time_object <= end_date_object:
                day_of_cb = (current_time_object - start_date_object).days + 1

                pcdi = await self.service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id, day_of_cb)
                tc = await self.service.create_team_composition(tc_name, pcdi.pcbdi_id)

                await interaction.response.send_message(f"Created team compositon: {tc.name}")
            else:
                await interaction.response.send_message(f"Today is not cb day")

        except (ParameterIsNullError, ClanBattleCantHaveMoreThenFiveDaysError, ValueError, TableEntryDoesntExistsError,
                NoActiveCBError) as e:
            await interaction.response.send_message(e)


async def setup(bot):
    bot.tree.add_command(CreateGroup(name="create", description="Create Commands"))