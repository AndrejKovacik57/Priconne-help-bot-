import discord
from discord import app_commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached, ClanBattleCantHaveMoreThenFiveDays, ObjectDoesntExistsInDBError, \
    PlayerAlreadyInClanError, PlayerNotInClanError
from service.service import Service
from db_model.table_classes import Clan, Player, ClanPlayer, ClanBattle, PlayerCBDayInfo, TeamComposition, Boss, BossBooking, \
    ClanRole


class CreateGroup(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = Service("priconne_database")

    @app_commands.command(description="Create clan")
    @app_commands.describe(clan_name="Clan to create")
    async def clan(self, interaction: discord.Interaction, clan_name: str):
        """ Create clan """
        try:
            clan = await self.service.create_clan(clan_name, interaction.guild_id)
            await interaction.response.send_message(f"guild: \n{clan}")
        except ObjectExistsInDBError as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Create clan role")
    @app_commands.describe(role_name="Role to create")
    async def role(self, interaction: discord.Interaction, role_name: str):
        """ Create clan role """
        try:
            clan = await self.service.get_clan_by_guild(interaction.guild_id)
            role = await self.service.create_clan_role(role_name, clan.clan_id)
            await interaction.response.send_message(f"Created \n{role}")
        except ObjectExistsInDBError as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Create player")
    @app_commands.describe(player_name="Player to create")
    async def player(self, interaction: discord.Interaction, player_name: str):
        """ Create player """
        try:
            player = await self.service.create_player(player_name, interaction.user.id)
            await interaction.response.send_message(f"Created \n{player}")
        except ObjectExistsInDBError as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Create clan battle")
    @app_commands.describe(cb_name="Clan battle name")
    async def cb(self, interaction: discord.Interaction, cb_name: str):
        """ Create cb """
        tiers = ['A', 'B', 'C', 'D']

        try:
            clan = await self.service.get_clan_by_guild(interaction.guild_id)
            cb = await self.service.create_clan_battle(clan.clan_id, cb_name)
            clan_players = await self.service.get_players_from_clan(clan.clan_id)

            for clan_player in clan_players:
                for _ in range(5):
                    await self.service.create_player_cb_day_info(cb.cb_id, clan_player.player_id)

            for index, tier in enumerate(tiers):
                for boss_number in range(5):
                    await self.service.create_boss(f'{tier}{boss_number + 1}', boss_number + 1, index + 1, cb.cb_id)
            boss_a1 = await self.service.get_boss_by_name('A1', cb.cb_id)
            boss_a1.active = True
            await self.service.update_boss(boss_a1)

            await interaction.response.send_message(f"Created clan battle, bosses and player tables")
        except (ObjectExistsInDBError, TableEntryDoesntExistsError, PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached
                , TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)


async def setup(bot):
    bot.tree.add_command(CreateGroup(name="create", description="Create Commands"))