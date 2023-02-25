import discord
from discord import app_commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached, ClanBattleCantHaveMoreThenFiveDaysError, \
    ObjectDoesntExistsInDBError, PlayerAlreadyInClanError, PlayerNotInClanError
from service.service import Service
from db_model.table_classes import Clan, Player, ClanPlayer, ClanBattle, PlayerCBDayInfo, TeamComposition, Boss, \
    BossBooking, \
    ClanRole
from .help_functions import multiple_players_check, update_bosses_when_tier_change, get_cb_day
from typing import Optional


class ClanGroup(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = Service("priconne_database")
    #
    # @app_commands.command(description="Check info regarding clan")
    # async def check(self, interaction: discord.Interaction):
    #     """ Check clan """
    #     try:
    #         guild_id = interaction.guild.id
    #         guild = await self.service.get_guild_by_id(guild_id)
    #         if not guild:
    #             raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
    #         # service.get_clan_battles_in_clan("Automatically fetched clan_id / clan_name")
    #         await interaction.response.send_message(
    #             f"__**Info for clan: \_\_\_**__"
    #             f"\nPosition: \_\_\_\nLap: \_\_\_"
    #             f"\nTier: (A/B/C/D)\nBoss: \_\_\_"
    #             f"\nHits Remaining: \_\_\_")
    #     except:
    #         return ""

    @app_commands.command(description="List all clans")
    async def list(self, interaction: discord.Interaction):
        """ List of clans """
        try:
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            clan_list = await self.service.get_clans(guild_id)
            message_string = ''
            for clan in clan_list:
                message_string += f"- {clan.name}\n"
            await interaction.response.send_message(
                f"__List of clans__"
                f"\n{message_string}")
        except TableEntryDoesntExistsError as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Update name of clan")
    @app_commands.describe(clan_name="Clan name to update", newname="New name to change clan to")
    async def updatename(self, interaction: discord.Interaction, clan_name: str, newname: str):
        """ Update name of clan """
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
                        existing_clan = await self.service.get_clan_by_name(clan_name)
                        existing_clan.name = newname
                        await self.service.update_clan(existing_clan)
                        await interaction.response.send_message(f"Changed clan name from **{clan_name}** to **{newname}**")
                        break

                else:
                    continue
                # This will be executed only if the inner loop was terminated by break
                break
            
            await interaction.response.send_message(f"You don't have permission to use this command!")
        except (TableEntryDoesntExistsError, ParameterIsNullError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Check players in clan")
    async def playerlist(self, interaction: discord.Interaction, clan: str):
        """ Check list of players in clan """
        try:
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            player_list = await self.service.get_players_from_clan_name(clan)
            # print(player_list)
            message_string = ''
            i = 1
            for player in player_list:
                player_name = player[1]
                message_string += f"{i}. {player_name}\n"
                i += 1
            await interaction.response.send_message(f"List of players in clan: **{clan}**\n{message_string}")
        except (ObjectDoesntExistsInDBError, PlayerNotInClanError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Add player to clan")
    @app_commands.describe(player="Player to add", clan="Clan to add player to")
    async def addplayer(self, interaction: discord.Interaction, player: str, clan: str):
        """ Add player to an existing clan """
        try:
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            user_roles = interaction.user.roles
            roles = await self.service.get_guild_admin(guild_id)
            roles += await self.service.get_guild_lead(guild_id)
            clan_player = None
            for user_role in user_roles:
                for role in roles:
                    if user_role.id == role[2]:
                        player_to_add = await self.service.get_player_by_name(player)
                        clan_to_join = await self.service.get_clan_by_name(clan)
                        clan_player = await self.service.add_player_to_clan(clan_to_join.clan_id, player_to_add.player_id)
                        await interaction.response.send_message(f"Added **{player}** to clan: **{clan}**.")
                        break
                else:
                    continue
                # This will be executed only if the inner loop was terminated by break
                break
            if not clan_player:
                await interaction.response.send_message(f"You don't have permission to use this command!")
        except (ObjectDoesntExistsInDBError, ObjectExistsInDBError, ParameterIsNullError, PlayerAlreadyInClanError,
                TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Join clan")
    @app_commands.describe(player="Player to add", clan="Clan to join")
    async def join(self, interaction: discord.Interaction, player: str, clan: str):
        """ Join clan with player """
        try:
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            player_to_add = await self.service.get_player_by_name(player)
            clan_to_join = await self.service.get_clan_by_name(clan)
            await self.service.add_player_to_clan(clan_to_join.clan_id, player_to_add.player_id)
            await interaction.response.send_message(f"Joined __{clan}__ under player: **{player}**.")
        except (ObjectDoesntExistsInDBError, ObjectExistsInDBError, ParameterIsNullError, PlayerAlreadyInClanError, TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Remove player from clan")
    @app_commands.describe(player="Player to remove", clan="Clan to remove player from")
    async def removeplayer(self, interaction: discord.Interaction, player: str, clan: str):
        """ Remove player from clan """
        try:
            guild_id = interaction.guild.id
            await self.service.get_guild_by_id(guild_id)
            user_roles = interaction.user.roles
            roles = await self.service.get_guild_admin(guild_id)
            roles += await self.service.get_guild_lead(guild_id)
            for user_role in user_roles:
                for role in roles:
                    if user_role.id == role[2]:
                        player_to_remove = await self.service.get_player_by_name(player)
                        from_clan = await self.service.get_clan_by_name(clan)
                        await self.service.remove_player_from_clan(from_clan.clan_id , player_to_remove.player_id)
                        await interaction.response.send_message(f"Removed **{player}** from clan: **{clan}**.")
                        break
                else:
                    continue
                # This will be executed only if the inner loop was terminated by break
                break

            await interaction.response.send_message(f"You don't have permission to use this command!")
        except (ObjectDoesntExistsInDBError, ParameterIsNullError, PlayerNotInClanError, TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(name="endcb", description="Ends cb")
    async def end_cb(self, interaction: discord.Interaction):
        """ ends clan battles in guild """
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
                            cb = await self.service.get_clan_battle_active_by_clan_id(clan.id)
                            cb.active = False
                            await self.service.update_clan_batte(cb)
                            await interaction.response.send_message(f"Clan battle {cb.name} has ended")
                        break
                else:
                    continue
                # This will be executed only if the inner loop was terminated by break
                break

            await interaction.response.send_message(f"You don't have permission to use this command!")
        except (ObjectDoesntExistsInDBError, ParameterIsNullError, PlayerNotInClanError, TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(name="editlap", description="Edits lap")
    @app_commands.describe(lap="Current lap", player_name='Name of your account')
    async def edit_lap(self, interaction: discord.Interaction, lap: int, player_name: Optional[str] = None):
        """ edits lap and tier
        """
        tier2_lap = 4
        tier3_lap = 11
        tier4_lap = 35
        try:
            guild_id = interaction.guild.id
            await self.service.get_guild_by_id(guild_id)
            user_roles = interaction.user.roles
            roles = await self.service.get_guild_admin(guild_id)
            roles += await self.service.get_guild_lead(guild_id)
            for user_role in user_roles:
                for role in roles:
                    if user_role.id == role[2]:
                        players = await self.service.get_player_by_discord_id(interaction.user.id)
                        player = multiple_players_check(player_name, players)
                        clan_player = await self.service.get_clan_player(player.player_id)
                        clan = clan_player[1]
                        cb = await self.service.get_clan_battle_active_by_clan_id(clan.clan_id)
                        cb.lap = lap

                        if tier3_lap > cb.lap >= tier2_lap:
                            boss_tier = 2
                            boss_char = 'B'
                            await update_bosses_when_tier_change(self.service, cb, boss_char, boss_tier, False)
                        elif tier4_lap > cb.lap >= tier3_lap:
                            boss_tier = 3
                            boss_char = 'C'
                            await update_bosses_when_tier_change(self.service, cb, boss_char, boss_tier, False)
                        elif cb.lap >= tier4_lap:
                            boss_tier = 4
                            boss_char = 'D'
                            await update_bosses_when_tier_change(self.service, cb, boss_char, boss_tier, False)
                        else:
                            boss_tier = 1
                            boss_char = 'A'
                            await update_bosses_when_tier_change(self.service, cb, boss_char, boss_tier, False)

                        await self.service.update_clan_batte(cb)
                        await interaction.response.send_message(f"You have changed lap to {lap} and tier to {boss_tier}")
                        break
                else:
                    continue
                # This will be executed only if the inner loop was terminated by break
                break

            await interaction.response.send_message(f"You don't have permission to use this command!")
        except (ObjectDoesntExistsInDBError, ParameterIsNullError, PlayerNotInClanError, TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(name="changeboss", description="Changes current boss")
    @app_commands.describe(boss_num="Boss number", player_name='Name of your account')
    async def change_boss(self, interaction: discord.Interaction, boss_num: int, player_name: Optional[str] = None):
        """ changes current boss """

        try:
            guild_id = interaction.guild.id
            await self.service.get_guild_by_id(guild_id)
            user_roles = interaction.user.roles
            roles = await self.service.get_guild_admin(guild_id)
            roles += await self.service.get_guild_lead(guild_id)
            for user_role in user_roles:
                for role in roles:
                    if user_role.id == role[2]:
                        players = await self.service.get_player_by_discord_id(interaction.user.id)
                        player = multiple_players_check(player_name, players)
                        clan_player = await self.service.get_clan_player(player.player_id)
                        clan = clan_player[1]
                        cb = await self.service.get_clan_battle_active_by_clan_id(clan.clan_id)
                        boss = await self.service.get_active_boss_by_cb_id(cb.cb_id)
                        boss.active = False
                        await self.service.update_boss(boss)
                        boss = await self.service.get_boss_by_boss_number(boss_num, cb.cb_id)
                        boss.active = True
                        boss = await self.service.update_boss(boss)

                        await interaction.response.send_message(f"You have changed active boss to {boss.name}")
                        break
                else:
                    continue
                # This will be executed only if the inner loop was terminated by break
                break

            await interaction.response.send_message(f"You don't have permission to use this command!")
        except (ObjectDoesntExistsInDBError, ParameterIsNullError, PlayerNotInClanError, TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(name="edithits", description="Changes hits for player")
    @app_commands.describe(player_name='Name of account', hits='Hits left')
    async def edit_players_hits(self, interaction: discord.Interaction, player_name: str, hits: int):
        """ changes player hits """

        try:
            guild_id = interaction.guild.id
            await self.service.get_guild_by_id(guild_id)
            user_roles = interaction.user.roles
            roles = await self.service.get_guild_admin(guild_id)
            roles += await self.service.get_guild_lead(guild_id)
            for user_role in user_roles:
                for role in roles:
                    if user_role.id == role[2]:
                        if 3 < hits < 0:
                            await interaction.response.send_message(f"Hits must be max 3 and min 0")

                        clans = await self.service.get_clan_by_guild(guild_id)
                        player = await self.service.get_player_by_name(player_name)
                        clan_player = await self.service.get_clan_player(player.id)
                        clan = clan_player[1]
                        if clan not in clans:
                            await interaction.response.send_message(f"Player: {player_name} is not in any of clans "
                                                                    f"on you server")

                        cb = await self.service.get_clan_battle_active_by_clan_id(clan.clan_id)
                        cb_day = get_cb_day(cb)
                        pcdi = await self.service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id,
                                                                                          cb_day)
                        pcdi.hits = hits
                        await self.service.update_pcdi(pcdi)

                        await interaction.response.send_message(f"You have changed today\'s hits to {hits} for "
                                                                f"{player_name}")
                        break
                else:
                    continue
                # This will be executed only if the inner loop was terminated by break
                break

            await interaction.response.send_message(f"You don't have permission to use this command!")
        except (ObjectDoesntExistsInDBError, ParameterIsNullError, PlayerNotInClanError, TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)


async def setup(bot):
    bot.tree.add_command(ClanGroup(name="clan", description="Clan Commands"))
