import discord
from discord import app_commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, \
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

    @app_commands.command(description="List all clans")
    async def list(self, interaction: discord.Interaction):
        """ List of clans """
        try:
            guild_id = interaction.guild.id
            await self.service.get_guild_by_id(guild_id)

            clan_list = await self.service.get_clans(guild_id)
            message_string = ''
            for clan in clan_list:
                message_string += f"- {clan.name}\n"
            embed = discord.Embed(title="Clan List", color=0xffff00,
                                description=f"{message_string}")
            return await interaction.response.send_message(embed=embed, ephemeral=False)
        except ObjectDoesntExistsInDBError as e:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Update name of clan")
    @app_commands.describe(clan_name="Clan name to update", newname="New name to change clan to")
    async def updatename(self, interaction: discord.Interaction, clan_name: str, newname: str):
        """ Update name of clan """
        try:
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")
            user_roles = interaction.user.roles
            roles = await self.service.get_guild_admin(guild_id)
            roles += await self.service.get_guild_lead(guild_id)
            for user_role in user_roles:
                for role in roles:
                    if user_role.id == role[2]:
                        existing_clan = await self.service.get_clan_by_name(clan_name)
                        existing_clan.name = newname
                        await self.service.update_clan(existing_clan)
                        embed = discord.Embed(title="Clan name update success!", color=0xffff00,
                                description=f"Changed clan name from **{clan_name}** to **{newname}**")
                        return await interaction.response.send_message(embed=embed, ephemeral=False)

            embed = discord.Embed(title="Error", color=0xff0000,
                                description=f"You don't have permission to use this command!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except (ObjectDoesntExistsInDBError, ParameterIsNullError) as e:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Check players in clan")
    async def playerlist(self, interaction: discord.Interaction, clan: str):
        """ Check list of players in clan """
        try:
            guild_id = interaction.guild.id
            await self.service.get_guild_by_id(guild_id)
            player_list = await self.service.get_players_from_clan_name(clan)
            message_string = ''
            i = 1
            for player in player_list:
                player_name = player[1]
                message_string += f"{i}. {player_name}\n"
                i += 1
            embed = discord.Embed(title=f"List of players in **{clan}**", color=0xffff00,
                                description=f"{message_string}")
            return await interaction.response.send_message(embed=embed, ephemeral=False)
        except (ObjectDoesntExistsInDBError, PlayerNotInClanError) as e:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description=e)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Add player to clan")
    @app_commands.describe(player="Player to add", clan="Clan to add player to")
    async def addplayer(self, interaction: discord.Interaction, player: str, clan: str):
        """ Add player to an existing clan """
        try:
            guild_id = interaction.guild.id
            await self.service.get_guild_by_id(guild_id)
            user_roles = interaction.user.roles
            roles = await self.service.get_guild_admin(guild_id)
            roles += await self.service.get_guild_lead(guild_id)
            clan_player = None
            for user_role in user_roles:
                for role in roles:
                    if user_role.id == role[2]:
                        player_to_add = await self.service.get_player_by_name(player)
                        clan_to_join = await self.service.get_clan_by_name(clan)
                        await self.service.add_player_to_clan(clan_to_join.clan_id, player_to_add.player_id)
                        embed = discord.Embed(title="Add success!", color=0xffff00,
                                description=f"Added **{player}** to clan: **{clan}**.")
                        return await interaction.response.send_message(embed=embed, ephemeral=False)

            embed = discord.Embed(title="Error", color=0xff0000,
                                description=f"You don't have permission to use this command!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except (ObjectDoesntExistsInDBError, ObjectExistsInDBError, ParameterIsNullError, PlayerAlreadyInClanError,
                ObjectDoesntExistsInDBError) as e:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Join clan")
    @app_commands.describe(player="Player to add", clan="Clan to join")
    async def join(self, interaction: discord.Interaction, player: str, clan: str):
        """ Join clan with player """
        try:
            guild_id = interaction.guild.id
            await self.service.get_guild_by_id(guild_id)
            player_to_add = await self.service.get_player_by_name(player)
            clan_to_join = await self.service.get_clan_by_name(clan)
            await self.service.add_player_to_clan(clan_to_join.clan_id, player_to_add.player_id)
            embed = discord.Embed(title="Join success!", color=0xffff00,
                                description=f"Joined __{clan}__ under player: **{player}**.")
            await interaction.response.send_message(embed=embed, ephemeral=False)
        except (ObjectDoesntExistsInDBError, ObjectExistsInDBError, ParameterIsNullError, PlayerAlreadyInClanError,
                ObjectDoesntExistsInDBError) as e:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

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
                        await self.service.remove_player_from_clan(from_clan.clan_id, player_to_remove.player_id)
                        embed = discord.Embed(title="Remove success!", color=0xffff00,
                                description=f"Removed **{player}** from clan: **{clan}**.")
                        return await interaction.response.send_message(embed=embed, ephemeral=False)
            embed = discord.Embed(title="Error", color=0xff0000,
                                description=f"You don't have permission to use this command!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except (ObjectDoesntExistsInDBError, ParameterIsNullError, PlayerNotInClanError,
                ObjectDoesntExistsInDBError) as e:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

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
                            cb = await self.service.get_clan_battle_active_by_clan_id(clan.clan_id)
                            cb.active = False
                            await self.service.update_clan_batte(cb)
                            embed = discord.Embed(title="CB End Success!", color=0xffff00,
                                description=f"Clan battle {cb.name} has ended")
                            return await interaction.response.send_message(embed=embed, ephemeral=False)

            embed = discord.Embed(title="Error", color=0xff0000,
                                description=f"You don't have permission to use this command!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except (ObjectDoesntExistsInDBError, ParameterIsNullError, PlayerNotInClanError,
                ObjectDoesntExistsInDBError) as e:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

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
                        embed = discord.Embed(title="Edit Lap Success!", color=0xffff00,
                                description=f"You have changed lap to {lap} and tier to {boss_tier}")
                        return await interaction.response.send_message(embed=embed, ephemeral=False)

            embed = discord.Embed(title="Error", color=0xff0000,
                                description=f"You don't have permission to use this command!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except (ObjectDoesntExistsInDBError, ParameterIsNullError, PlayerNotInClanError,
                ObjectDoesntExistsInDBError) as e:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

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
                        embed = discord.Embed(title="Change Boss Success!", color=0xffff00,
                                description=f"You have changed active boss to {boss.name}")
                        return await interaction.response.send_message(embed=embed, ephemeral=False)

            embed = discord.Embed(title="Error", color=0xff0000,
                                description=f"You don't have permission to use this command!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except (ObjectDoesntExistsInDBError, ParameterIsNullError, PlayerNotInClanError,
                ObjectDoesntExistsInDBError) as e:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

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
                        clan_player = await self.service.get_clan_player(player.player_id)
                        clan = clan_player[1]
                        if clan not in clans:
                            embed = discord.Embed(title="Change Boss Success!", color=0xffff00,
                                description=f"**{player_name}** is not in any clans on your server")
                            return await interaction.response.send_message(embed=embed, ephemeral=False)

                        cb = await self.service.get_clan_battle_active_by_clan_id(clan.clan_id)
                        cb_day = get_cb_day(cb)
                        pcdi = await self.service.get_pcdi_by_player_id_and_cb_id_and_day(player.player_id, cb.cb_id,
                                                                                          cb_day)
                        pcdi.hits = hits
                        await self.service.update_pcdi(pcdi)
                        embed = discord.Embed(title="Edit Hits Success!", color=0xffff00,
                                description=f"You have changed today\'s hits to {hits} for {player_name}")
                        return await interaction.response.send_message(embed=embed, ephemeral=False)

            embed = discord.Embed(title="Error", color=0xff0000,
                                description=f"You don't have permission to use this command!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except (ParameterIsNullError, PlayerNotInClanError, ObjectDoesntExistsInDBError) as e:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="deletecb", description="Delete clan battle and related information")
    @app_commands.describe(cb_name='Clan battle name')
    async def delete_cb(self, interaction: discord.Interaction, cb_name: str):
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
                        for i in range(len(clans)):
                            await self.service.delete_clan_battle_by_name_and_clan_id(cb_name, clans[i].clan_id)
                            return await interaction.response.send_message(
                                f'You have deleted cb: {cb_name} and all related information '
                                f'for clans in your server')

            embed = discord.Embed(title="Error", color=0xff0000,
                                description=f"You don't have permission to use this command!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except ObjectDoesntExistsInDBError as e:
            embed = discord.Embed(title="Error", color=0xff0000,
                                  description=e)
            return await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    bot.tree.add_command(ClanGroup(name="clan", description="Clan Commands"))
