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
            clan = await self.service.create_clan(clan_name)
            await interaction.response.send_message(f"{clan}")
        except ObjectExistsInDBError as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Create clan role")
    @app_commands.describe(role_name="Role to create")
    async def role(self, interaction: discord.Interaction, player_name: str):
        """ Create player """
        try:
            player = await self.service.create_player(player_name, interaction.user.id)
            await interaction.response.send_message(f"Created \n{player}")
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



async def setup(bot):
    bot.tree.add_command(CreateGroup(name="create", description="Create Commands"))