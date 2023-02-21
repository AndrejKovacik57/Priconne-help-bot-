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
    @app_commands.describe(player ="Player to delete")
    async def delete(self, interaction: discord.Interaction, player: str):
        try:
            # guild = await self.service.get_guild_by_id(interaction.guild.id)
            # if not guild:
            #     raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            # player = await self.service.get_player_by_discord_id(interaction.user.id)
            #
            # await self.service.remove_player(player.player_id)
            # await interaction.response.send_message(f"Successfully deleted **{player}**")
            await interaction.response.send_message(f"Function out of service")
        except TableEntryDoesntExistsError as e:
            await interaction.response.send_message(e)
    #
    # async def player_names_autocomplete(self, interaction: discord.Interaction,
    #                                     current: str) -> list:
    #     players = await self.service.get_player_by_discord_id(interaction.user.id)
    #     return [
    #         app_commands.Choice(name=choice.name, value=choice.name)
    #         for choice in players if current.lower() in choice.name.lower()
    #     ]

    @app_commands.command(description="Check info about specified player")
    @app_commands.describe(player_name="Player to check")
    # @app_commands.autocomplete(choice=player_names_autocomplete)
    async def check(self, interaction: discord.Interaction, player_name: str): #, choice: str
        """ Check status of player """
        try:
            guild = await self.service.get_guild_by_id(interaction.guild.id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            clan = await self.service.get_clan_by_guild(guild.guild_id)
            if not clan:
                raise TableEntryDoesntExistsError('Your discord doesnt have clan created')

            player_in_clan = await self.service.get_player_by_name_and_clan_id(player_name, clan.clan_id)
            if player_in_clan:
                await interaction.response.send_message(f'Checking Player: **{player_in_clan.name}** in Clan: {clan.name}')
            else:
                await interaction.response.send_message(f'There is no player: {player_name} in clan')
        except (ObjectDoesntExistsInDBError, PlayerNotInClanError, TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)


async def setup(bot):
    bot.tree.add_command(PlayerGroup(name="player", description="Player Commands"))
