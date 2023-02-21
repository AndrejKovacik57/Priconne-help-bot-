import discord
from discord import app_commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached, ClanBattleCantHaveMoreThenFiveDaysError, ObjectDoesntExistsInDBError, \
    PlayerAlreadyInClanError, PlayerNotInClanError
from service.service import Service
from db_model.table_classes import Clan, Player, ClanPlayer, ClanBattle, PlayerCBDayInfo, TeamComposition, Boss, BossBooking, \
    ClanRole


class PlayerGroup(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = Service("priconne_database")

    @app_commands.command(description="Delete a player")
    @app_commands.describe(player = "Player to add")
    async def delete(self, interaction: discord.Interaction, player: str):
        try:
            guild = await self.service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            player_name = await self.service.get_own_player_by_name(player, interaction.user.id)
            await self.service.remove_player(player_name.player_id)
            await interaction.response.send_message(f"Successfully deleted **{player}**")
        except TableEntryDoesntExistsError as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Check info regarding self")
    async def selfcheck(self, interaction: discord.Interaction):
        try:
            guild = await self.service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            player_check = await self.service.get_player_by_discord_id(interaction.user.id)
            player_list_message = ''
            for player in player_check:
                clan_player = await self.service.get_clan_player(player[0])
                player_list_message += f"Player: **{clan_player.player_name}** is in clan: **{clan_player.clan_name}**\n"
            await interaction.response.send_message(f"{player_list_message}")
        except (ObjectDoesntExistsInDBError, PlayerNotInClanError, TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Check info about specified player")
    @app_commands.describe(player = "Player to check")
    async def check(self, interaction: discord.Interaction, player: str):
        try:
            guild = await self.service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            player_check = await self.service.get_player_by_name(player)
            clan_player = await self.service.get_clan_player(player_check.player_id)
            if clan_player.clan_name == "NONE":
                await interaction.response.send_message(
                f"Checking Player: **{player}**"
                f"\nClan: __NONE__")
                return
            clan = await self.service.get_clan_by_id(clan_player.clan_id)
            await interaction.response.send_message(
                f"Checking Player: **{player}**"
                f"\nClan: __{clan.name}__")
        except (ObjectDoesntExistsInDBError, PlayerNotInClanError) as e:
            await interaction.response.send_message(e)


async def setup(bot):
    bot.tree.add_command(PlayerGroup(name="player", description="Player Commands"))
