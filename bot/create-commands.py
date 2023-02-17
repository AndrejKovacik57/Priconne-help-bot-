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
    @app_commands.describe(clan="Clan to create")
    async def clan(self, interaction: discord.Interaction, clan: str):
        """ Create clan """
        try:
            await self.service.create_clan(clan)
            await interaction.response.send_message(f"{interaction.user.name} said to create the clan: '{clan}'")
        except ObjectExistsInDBError as e:
            await interaction.response.send_message(f"Clan: {clan} already exists!")

    @app_commands.command(description="Create player")
    @app_commands.describe(player="Player to create")
    async def player(self, interaction: discord.Interaction, player: str):
        """ Create player """
        try:
            await self.service.create_player(player, interaction.user.id)
            await interaction.response.send_message(f"Created \n{player}")
        except ObjectExistsInDBError as e:
            await interaction.response.send_message(f"Player: {player} already exists!")


async def setup(bot):
    bot.tree.add_command(CreateGroup(name="create", description="Create Commands"))