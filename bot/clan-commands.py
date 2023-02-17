import discord
from discord import app_commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached, ClanBattleCantHaveMoreThenFiveDays, ObjectDoesntExistsInDBError, \
    PlayerAlreadyInClanError, PlayerNotInClanError
from service.service import Service
from db_model.table_classes import Clan, Player, ClanPlayer, ClanBattle, PlayerCBDayInfo, TeamComposition, Boss, \
    BossBooking, \
    ClanRole

service = Service("priconne_database")


class ClanGroup(app_commands.Group):
    @app_commands.command(description="Check info regarding clan")
    async def check(self, interaction: discord.Interaction):
        """ Check clan """
        try:
            # service.get_clan_battles_in_clan("Automatically fetched clan_id / clan_name")
            await interaction.response.send_message(
                f"__**Info for clan: \_\_\_**__\nPosition: \_\_\_\nLap: \_\_\_\nTier: (A/B/C/D)\nBoss: \_\_\_\nHits Remaining: \_\_\_")
        except:
            return ""

    @app_commands.command(description="List all clans")
    async def list(self, interaction: discord.Interaction):
        """ List of clans """
        try:
            clan_list = await service.get_clans()
            await interaction.response.send_message(f"List of clans\n{clan_list}")
        except:
            await interaction.response.send_message(f"Error in command. Please try again in a few moments")

    @app_commands.command(description="Update name of clan")
    @app_commands.describe(clan="Clan name to update", newname="New name to change clan to")
    async def updatename(self, interaction: discord.Interaction, clan: str, newname: str):
        """ Update name of clan """
        try:
            existingClan = await service.get_clan_by_name(clan)
            await service.update_clan(Clan(existingClan[0], newname))
            await interaction.response.send_message(f"Changed clan name from **{clan}** to **{newname}**")
        except:
            await interaction.response.send_message(f"Error in command. Please try again in a few moments")

    @app_commands.command(description="Check players in clan")
    async def playerlist(self, interaction: discord.Interaction):
        """ Check list of players in clan """
        try:
            playerCheck = await service.get_player_by_discord_id(interaction.user.id)
            clanPlayer = await service.get_clanplayer(playerCheck[0])
            clan = await service.get_clan_by_id(clanPlayer[0])
            playerList = await service.get_players_from_clan(clan[0])
            await interaction.response.send_message(f"List of players\n{playerList}")
        except ObjectDoesntExistsInDBError as e:
            await interaction.response.send_message(f"You don't exist!")
        except PlayerNotInClanError as e:
            await interaction.response.send_message(f"You're not in a clan!")

    @app_commands.command(description="Add player to clan")
    @app_commands.describe(player="Player to add", clan="Clan to add player to")
    async def addplayer(self, interaction: discord.Interaction, player: str, clan: str):
        """ Add player to an existing clan """
        try:
            playerToAdd = await service.get_player_by_name(player)
            clanToJoin = await service.get_clan_by_name(clan)
            await service.add_player_to_clan(clanToJoin[0], playerToAdd[0])
            await interaction.response.send_message(f"Added **{player}** to clan: **{clan}**.")
        except ObjectDoesntExistsInDBError as e:
            await interaction.response.send_message(f"Player and/or clan doesn't exist!")
        except ObjectExistsInDBError as e:
            await interaction.response.send_message(f"Clan: {clan} already exists!")
        except ParameterIsNullError as e:
            await interaction.response.send_message(f"Need player and/or clan name!")
        except PlayerAlreadyInClanError as e:
            await interaction.response.send_message(f"Player is already in clan!")

    @app_commands.command(description="Remove player from clan")
    @app_commands.describe(player="Player to remove", clan="Clan to remove player from")
    async def removeplayer(self, interaction: discord.Interaction, player: str, clan: str):
        """ Remove player from clan """
        try:
            playerToRemove = await service.get_player_by_name(player)
            clanToRemove = await service.get_clan_by_name(clan)
            await service.remove_player_from_clan(clanToRemove[0], playerToRemove[0])
            await interaction.response.send_message(f"Removed **{player}** from clan: **{clan}**.")
        except ObjectDoesntExistsInDBError as e:
            await interaction.response.send_message(f"Player and/or clan doesn't exist!")
        except ParameterIsNullError as e:
            await interaction.response.send_message(f"Need player and/or clan name!")
        except PlayerNotInClanError as e:
            await interaction.response.send_message(f"Player is not in clan!")


async def setup(bot):
    bot.tree.add_command(ClanGroup(name="clan", description="Clan Commands"))
