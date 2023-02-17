import discord
from discord import app_commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached, ClanBattleCantHaveMoreThenFiveDays, ObjectDoesntExistsInDBError, \
    PlayerAlreadyInClanError, PlayerNotInClanError
from service.service import Service
from db_model.table_classes import Clan, Player, ClanPlayer, ClanBattle, PlayerCBDayInfo, TeamComposition, Boss, BossBooking, \
    ClanRole

service = Service("priconne_database")

class PlayerGroup(app_commands.Group):
    
    @app_commands.command(description="Delete a player")
    @app_commands.describe(player = "Player to add")
    async def delete(self, interaction: discord.Interaction, player: str):
        try:
            # Need delete player function
            await interaction.response.send_message(f"I'm the **/player delete** command!\n*(Still working on functionality)*")
        except:
            await interaction.response.send_message(f"Player: **{player}** doesn't exist!")
    

    @app_commands.command(description="Check info regarding self")
    async def selfcheck(self, interaction: discord.Interaction):
        try:
            playerCheck = service.get_player_by_discord_id(interaction.user.id)
            clanPlayer = service.get_clanplayer(playerCheck[0])
            clan = service.get_clan_by_id(clanPlayer[0])
            await interaction.response.send_message(f"Checking self\nClan: {clan[1]}")
        except ObjectDoesntExistsInDBError as e:
            await interaction.response.send_message(f"You don't exist!")
        except PlayerNotInClanError as e:
            await interaction.response.send_message(f"You're not in a clan!")
    

    @app_commands.command(description="Check info about specified player")
    @app_commands.describe(player = "Player to check")
    async def check(self, interaction: discord.Interaction, player: str):
        try:
            playerCheck = service.get_player_by_name(player)
            clanPlayer = service.get_clanplayer(playerCheck[0])
            clan = service.get_clan_by_id(clanPlayer[0])
            await interaction.response.send_message(f"Checking {player}\nClan: {clan[1]}")
        except ObjectDoesntExistsInDBError as e:
            await interaction.response.send_message(f"Player: **{player}** doesn't exist!")
        except PlayerNotInClanError as e:
            await interaction.response.send_message(f"Player: **{player}** is not in a clan!")


async def setup(bot):
    bot.tree.add_command(PlayerGroup(name="player", description="Player Commands"))