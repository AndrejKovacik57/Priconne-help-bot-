import discord
from discord import app_commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached, ClanBattleCantHaveMoreThenFiveDays, ObjectDoesntExistsInDBError, \
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
            # Need delete player function
            await interaction.response.send_message(f"I'm the **/player delete** command!\n*(Still working on functionality)*")
        except TableEntryDoesntExistsError as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Check info regarding self")
    async def selfcheck(self, interaction: discord.Interaction):
        try:
            guild = await self.service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            playerCheck = await self.service.get_player_by_discord_id(interaction.user.id)
            clanPlayer = await self.service.get_clan_player(playerCheck.player_id)
            clan = await self.service.get_clan_by_id(clanPlayer.player_id)
            await interaction.response.send_message(f"Checking self\nClan: {clan}")
        except ObjectDoesntExistsInDBError as e:
            await interaction.response.send_message(f"You don't exist!")
        except PlayerNotInClanError as e:
            await interaction.response.send_message(f"You're not in a clan!")

    @app_commands.command(description="Check info about specified player")
    @app_commands.describe(player = "Player to check")
    async def check(self, interaction: discord.Interaction, player: str):
        try:
            guild = await self.service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            playerCheck = await self.service.get_player_by_name(player)
            clanPlayer = await self.service.get_clan_player(playerCheck.player_id)
            clan = await self.service.get_clan_by_id(clanPlayer.clan_id)
            await interaction.response.send_message(
                f"Checking {player}"
                f"\nClan: {clan}")
        except ObjectDoesntExistsInDBError as e:
            await interaction.response.send_message(f"Player: **{player}** doesn't exist!")
        except PlayerNotInClanError as e:
            await interaction.response.send_message(f"Player: **{player}** is not in a clan!")


async def setup(bot):
    bot.tree.add_command(PlayerGroup(name="player", description="Player Commands"))
