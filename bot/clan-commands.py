import discord
from discord import app_commands
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached, ClanBattleCantHaveMoreThenFiveDaysError, \
    ObjectDoesntExistsInDBError, PlayerAlreadyInClanError, PlayerNotInClanError
from service.service import Service
from db_model.table_classes import Clan, Player, ClanPlayer, ClanBattle, PlayerCBDayInfo, TeamComposition, Boss, \
    BossBooking, \
    ClanRole


class ClanGroup(app_commands.Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = Service("priconne_database")

    @app_commands.command(description="Check info regarding clan")
    async def check(self, interaction: discord.Interaction):
        """ Check clan """
        try:
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            # service.get_clan_battles_in_clan("Automatically fetched clan_id / clan_name")
            await interaction.response.send_message(
                f"__**Info for clan: \_\_\_**__"
                f"\nPosition: \_\_\_\nLap: \_\_\_"
                f"\nTier: (A/B/C/D)\nBoss: \_\_\_"
                f"\nHits Remaining: \_\_\_")
        except:
            return ""

    @app_commands.command(description="List all clans")
    async def list(self, interaction: discord.Interaction):
        """ List of clans """
        try:
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            clan_list = await self.service.get_clans()
            message_string = ''
            for clan in clan_list:
                clan_name = clan[2]
                message_string += f"- {clan_name}\n"
            await interaction.response.send_message(
                f"__List of clans__"
                f"\n{message_string}")
        except TableEntryDoesntExistsError as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Update name of clan")
    @app_commands.describe(clan="Clan name to update", newname="New name to change clan to")
    async def updatename(self, interaction: discord.Interaction, clan: str, newname: str):
        """ Update name of clan """
        try:
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            user_roles = interaction.user.roles
            guild_admins = await self.service.get_guild_admin(guild_id)
            for user_role in user_roles:
                for guild_admin in guild_admins:
                    if user_role.id == guild_admin[2]:
                        existing_clan = await self.service.get_clan_by_name(clan)

                        await self.service.update_clan_name(existing_clan.name, newname)
                        await interaction.response.send_message(f"Changed clan name from **{clan}** to **{newname}**")
                        return
            guild_leads = await self.service.get_guild_lead(guild_id)
            for user_role in user_roles:
                for guild_lead in guild_leads:
                    if user_role.id == guild_lead[2]:
                        existing_clan = await self.service.get_clan_by_name(clan)

                        await self.service.update_clan_name(existing_clan.name, newname)
                        await interaction.response.send_message(f"Changed clan name from **{clan}** to **{newname}**")
                        return
            
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
            message_string = ''
            for player in player_list:
                player_name = player[1]
                message_string += f"- {player_name}\n"
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
            guild_admins = await self.service.get_guild_admin(guild_id)
            for user_role in user_roles:
                for guild_admin in guild_admins:
                    if user_role.id == guild_admin[2]:
                        player_to_add = await self.service.get_player_by_name(player)
                        clan_to_join = await self.service.get_clan_by_name(clan)
                        await self.service.add_player_to_clan(clan_to_join.clan_id, player_to_add.player_id)
                        await interaction.response.send_message(f"Added **{player}** to clan: **{clan}**.")
                        return
            guild_leads = await self.service.get_guild_lead(guild_id)
            for user_role in user_roles:
                for guild_lead in guild_leads:
                    if user_role.id == guild_lead[2]:
                        player_to_add = await self.service.get_player_by_name(player)
                        clan_to_join = await self.service.get_clan_by_name(clan)
                        await self.service.add_player_to_clan(clan_to_join.clan_id, player_to_add.player_id)
                        await interaction.response.send_message(f"Added **{player}** to clan: **{clan}**.")
                        return
            
            await interaction.response.send_message(f"You don't have permission to use this command!")
        except (ObjectDoesntExistsInDBError, ObjectExistsInDBError, ParameterIsNullError, PlayerAlreadyInClanError, TableEntryDoesntExistsError) as e:
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
            player_to_add = await self.service.get_own_player_by_name(player, interaction.user.id)
            clan_to_join = await self.service.get_clan_by_name(clan)
            await self.service.add_player_to_clan(clan_to_join.clan_id, player_to_add.player_id)
            await interaction.response.send_message(f"Added **{player}** to clan: **{clan}**.")
        except (ObjectDoesntExistsInDBError, ObjectExistsInDBError, ParameterIsNullError, PlayerAlreadyInClanError, TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)

    @app_commands.command(description="Remove player from clan")
    @app_commands.describe(player="Player to remove", clan="Clan to remove player from")
    async def removeplayer(self, interaction: discord.Interaction, player: str, clan: str):
        """ Remove player from clan """
        try:
            guild_id = interaction.guild.id
            guild = await self.service.get_guild_by_id(guild_id)
            if not guild:
                raise TableEntryDoesntExistsError("Server doesn't exist! Please run **/server setup**")
            user_roles = interaction.user.roles
            guild_admins = await self.service.get_guild_admin(guild_id)
            for user_role in user_roles:
                for guild_admin in guild_admins:
                    if user_role.id == guild_admin[2]:
                        player_to_remove = await self.service.get_player_by_name(player)
                        from_clan = await self.service.get_clan_by_name(clan)
                        await self.service.remove_player_from_clan(from_clan.clan_id , player_to_remove.player_id)
                        await interaction.response.send_message(f"Removed **{player}** from clan: **{clan}**.")
                        return
            guild_leads = await self.service.get_guild_lead(guild_id)
            for user_role in user_roles:
                for guild_lead in guild_leads:
                    if user_role.id == guild_lead[2]:
                        player_to_remove = await self.service.get_player_by_name(player)
                        from_clan = await self.service.get_clan_by_name(clan)
                        await self.service.remove_player_from_clan(from_clan.clan_id , player_to_remove.player_id)
                        await interaction.response.send_message(f"Removed **{player}** from clan: **{clan}**.")
                        return
            
            await interaction.response.send_message(f"You don't have permission to use this command!")
        except (ObjectDoesntExistsInDBError, ParameterIsNullError, PlayerNotInClanError, TableEntryDoesntExistsError) as e:
            await interaction.response.send_message(e)


async def setup(bot):
    bot.tree.add_command(ClanGroup(name="clan", description="Clan Commands"))
