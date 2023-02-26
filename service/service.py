import aiosqlite
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached, ClanBattleCantHaveMoreThenFiveDaysError, \
    ObjectDoesntExistsInDBError, PlayerAlreadyInClanError, PlayerNotInClanError, ThereIsAlreadyActiveCBError, \
    DesiredBossIsDeadError, CantBookDeadBossError, NoActiveCBError
from db_model.table_classes import Clan, Player, ClanPlayer, ClanBattle, PlayerCBDayInfo, TeamComposition, Boss, \
    BossBooking, Guild, GuildRole
from datetime import datetime, timedelta


class Service:
    def __init__(self, db_name: str):
        self.db = f'{db_name}.db'

    async def add_server(self, guild_id: int):
        """ Insert a new server into the Guild table. """
        if not guild_id:
            raise ParameterIsNullError("Guild id can't be empty!")
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Guild WHERE server_id=:server_id""",
                              {'server_id': guild_id})
            result = await cur.fetchone()

            if result:
                raise ObjectExistsInDBError("Your server is already setup!")

            await cur.execute(""" INSERT INTO Guild(server_id) VALUES (:server_id) """,
                              {'server_id': guild_id})

            await conn.commit()

        return True

    async def get_guild_by_id(self, guild_id: int) -> Guild or None:
        """ Gets Clan by Id """
        if not guild_id:
            raise ParameterIsNullError("Guild id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Guild WHERE server_id=:server_id """, {'server_id': guild_id})
            result = await cur.fetchone()

        if not result:
            raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")

        return Guild(result[0])

    async def add_admin_role(self, guild_id: int, role_id: int):
        """ Insert a new admin role into the GuildAdmin table. """
        if not guild_id:
            raise ParameterIsNullError("Guild id can't be empty!")
        guild = await self.get_guild_by_id(guild_id)
        if not guild:
            raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")

        if not role_id:
            raise ParameterIsNullError("Role id can't be empty!")
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM GuildAdmin WHERE role_id=:role_id and guild_id=:guild_id """,
                              {'role_id': role_id, 'guild_id': guild_id})
            result = await cur.fetchone()

            if result:
                raise ObjectExistsInDBError("Role is already setup!")

            await cur.execute(""" INSERT INTO GuildAdmin(role_id, guild_id) VALUES (:role_id, :guild_id) """,
                              {'role_id': role_id, 'guild_id': guild_id})

            guild_role = GuildRole(guild_id, role_id)

            await conn.commit()

        return guild_role

    async def remove_admin_role(self, guild_id: int, role_id: int):
        """ Remove admin role from server """

        if not guild_id:
            raise ParameterIsNullError("Guild id can't be empty!")

        guild = await self.get_guild_by_id(guild_id)
        if not guild:
            raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")

        if not role_id:
            raise ParameterIsNullError("Role id can't be empty!")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" SELECT * FROM GuildAdmin WHERE role_id=:role_id and guild_id=:guild_id """,
                              {'role_id': role_id, 'guild_id': guild_id})
            result = await cur.fetchone()
            if not result:
                raise ObjectDoesntExistsInDBError("Role is not registered as an admin!")
            await cur.execute(""" DELETE FROM GuildAdmin WHERE role_id = ? and guild_id = ? """, (role_id, guild_id))
            await conn.commit()
        return True

    async def add_lead_role(self, guild_id: int, role_id: int):
        """ Insert a new lead role into the GuildLead table. """
        if not guild_id:
            raise ParameterIsNullError("Guild id can't be empty!")
        guild = await self.get_guild_by_id(guild_id)
        if not guild:
            raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")

        if not role_id:
            raise ParameterIsNullError("Role id can't be empty!")
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM GuildLead WHERE role_id=:role_id and guild_id=:guild_id """,
                              {'role_id': role_id, 'guild_id': guild_id})
            result = await cur.fetchone()

            if result:
                raise ObjectExistsInDBError("Role is already setup!")

            await cur.execute(""" INSERT INTO GuildLead(role_id, guild_id) VALUES (:role_id, :guild_id) """,
                              {'role_id': role_id, 'guild_id': guild_id})

            guild_role = GuildRole(guild_id, role_id)

            await conn.commit()

        return guild_role

    async def remove_lead_role(self, guild_id: int, role_id: int):
        """ Remove lead role from server """

        if not guild_id:
            raise ParameterIsNullError("Guild id can't be empty!")

        guild = await self.get_guild_by_id(guild_id)
        if not guild:
            raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")

        if not role_id:
            raise ParameterIsNullError("Role id can't be empty!")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM GuildLead WHERE role_id=:role_id and guild_id=:guild_id """,
                              {'role_id': role_id, 'guild_id': guild_id})
            result = await cur.fetchone()

            if not result:
                raise ObjectDoesntExistsInDBError("Role is not registered as an lead!")

            await cur.execute(""" DELETE FROM GuildLead WHERE role_id = ? and guild_id = ? """, (role_id, guild_id))
            await conn.commit()
        return True

    async def get_guild_admin(self, guild_id: int) -> list:
        """ Gets admin roles for server """
        if not guild_id:
            raise ParameterIsNullError("Guild id can't be empty!")
        guild = await self.get_guild_by_id(guild_id)
        if not guild:
            raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM GuildAdmin WHERE guild_id=:guild_id """, {'guild_id': guild_id})
            results = await cur.fetchall()

        if not results:
            raise ObjectDoesntExistsInDBError(
                "There are no roles set up for your server! Please run **/server addadminrole**")

        guild_role_array = [result for result in results]

        return guild_role_array

    async def get_guild_lead(self, guild_id: int) -> list:
        """ Gets lead roles for server """
        if not guild_id:
            raise ParameterIsNullError("Guild id can't be empty!")
        guild = await self.get_guild_by_id(guild_id)
        if not guild:
            raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM GuildLead WHERE guild_id=:guild_id """, {'guild_id': guild_id})
            results = await cur.fetchall()

        if not results:
            raise ObjectDoesntExistsInDBError(
                "There are no roles set up for your server! Please run **/server addadminrole** and/or **/server addleadrole**")

        guild_role_array = [result for result in results]

        return guild_role_array

    async def create_clan(self, clan_name: str, guild_id: int) -> Clan:
        """ Insert a new Clan into the Clan table. """
        if not (clan_name and guild_id):
            raise ParameterIsNullError("Clan name, Guild id cant be empty")

        guild = await self.get_guild_by_id(guild_id)
        if not guild:
            raise ObjectDoesntExistsInDBError("Server doesn't exist! Please run **/server setup**")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Clan WHERE name=:name and guild_id=:guild_id""",
                              {'name': clan_name, 'guild_id': guild_id})
            result = await cur.fetchone()

            if result:
                raise ObjectExistsInDBError('Clan already exists!')

            await cur.execute(""" INSERT INTO Clan(name, guild_id) VALUES (:name,:guild_id) """,
                              {'name': clan_name, 'guild_id': guild_id})
            clan = Clan(cur.lastrowid, guild_id, clan_name)

            await conn.commit()

        return clan

    async def get_clan_by_id(self, clan_id: int) -> Clan or None:
        """ Gets Clan by Id """
        if not clan_id:
            raise ParameterIsNullError("Clan id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Clan WHERE id=:id """, {'id': clan_id})
            result = await cur.fetchone()

        if not result:
            return None

        return Clan(result[0], result[1], result[2])

    async def get_clan_by_name(self, clan_name: str) -> Clan or None:
        """ Gets Clan by name """
        if not clan_name:
            raise ParameterIsNullError("Clan name can't be empty")
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Clan WHERE name=:name """, {'name': clan_name})
            result = await cur.fetchone()

        if not result:
            raise ObjectDoesntExistsInDBError("Clan doesn't exist!")

        return Clan(result[0], result[1], result[2])

    async def get_clan_by_guild(self, guild_id: int) -> list:
        """ Gets Clan by guild """
        if not guild_id:
            raise ParameterIsNullError("Guild id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Clan WHERE guild_id=:guild """, {'guild': guild_id})
            results = await cur.fetchall()

        if not results:
            ObjectDoesntExistsInDBError('There is no clan for this server')

        return [Clan(result[0], result[1], result[2]) for result in results]

    async def get_clans(self, guild_id: int) -> list:
        """ Gets all clans in guild """
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" SELECT * FROM Clan WHERE guild_id=:guild_id """, {'guild_id': guild_id})
            results = await cur.fetchall()

        if not results:
            ObjectDoesntExistsInDBError('There is no clan for this server')

        return [Clan(result[0], result[1], result[2]) for result in results]

    async def get_clans_paginate(self, limit: int, offset: int) -> list:
        """ Paginate clan table """
        if not limit:
            raise ValueError(f'Parameter limit must be higher then 0')
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" SELECT * FROM Clan LIMIT :limit OFFSET :offset""", {'limit': limit, 'offset': offset})
            results = await cur.fetchall()

        return [Clan(result[0], result[1], result[2]) for result in results]

    async def update_clan(self, clan: Clan) -> Clan:
        """ Update clan table """
        clan_to_be_updated = await self.get_clan_by_id(clan.clan_id)
        if not clan_to_be_updated:
            raise ObjectDoesntExistsInDBError(f'clan id {clan.clan_id}')

        if not (clan.name and clan.guild_id):
            raise ParameterIsNullError("Clan name cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if clan_to_be_updated.name != clan.name:
                await cur.execute(""" SELECT * FROM Clan WHERE name=:name """, {'name': clan.name})
                result = await cur.fetchone()

                if result:
                    raise ObjectExistsInDBError(result)

            await cur.execute(""" UPDATE Clan SET name=:name, guild_id=:guild WHERE id=:id """,
                              {'name': clan.name, 'id': clan.clan_id, 'guild': clan.guild_id})
            await conn.commit()
            await cur.execute("SELECT * FROM Clan WHERE id=:id", {'id': clan.clan_id})
            updated_result = await cur.fetchone()
        return Clan(updated_result[0], updated_result[1], updated_result[2])

    # async def update_clan_name(self, clan: str, new_name: str) -> Clan:
    #     """ Update clan table """
    #     if not clan:
    #         raise ParameterIsNullError("Clan name can't be empty!")
    #     if not new_name:
    #         raise ParameterIsNullError("New clan name can't be empty!")
    #     clan_to_be_updated = await self.get_clan_by_name(clan)
    #     if not clan_to_be_updated:
    #         raise ObjectDoesntExistsInDBError("Clan doesn't exist!")
    #
    #     async with aiosqlite.connect(self.db) as conn:
    #         cur = await conn.cursor()
    #         if clan_to_be_updated.name != new_name:
    #             await cur.execute(""" SELECT * FROM Clan WHERE name=:name """, {'name': new_name})
    #             result = await cur.fetchone()
    #
    #             if result:
    #                 raise ObjectExistsInDBError("Clan with that name already exists!")
    #
    #         await cur.execute(""" UPDATE Clan SET name=:new_name WHERE name=:name """,
    #                           {'new_name': new_name, 'name': clan})
    #         await conn.commit()
    #         await cur.execute("SELECT * FROM Clan WHERE name=:name", {'name': new_name})
    #         updated_result = await cur.fetchone()
    #     return Clan(updated_result[0], updated_result[1], updated_result[2])

    async def create_player(self, player_name: str, dis_id: int, clan_id=0) -> Player:
        """ Insert a new Player into the Player table. Can add player to clan and give role to player"""
        if not (player_name and dis_id):
            raise ParameterIsNullError("Clan name, discord_id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" 
                        SELECT *
                        FROM Player 
                        WHERE name=:player_name"""
                              , {'player_name': player_name}
                              )
            result = await cur.fetchone()

            if result:
                raise ObjectExistsInDBError("Player already exists!")

            await cur.execute(""" 
                        INSERT INTO Player(name,discord_id) VALUES (:name,:discord_id) """
                              , {'name': player_name, 'discord_id': dis_id}
                              )
            player_id = cur.lastrowid
            if clan_id:
                await cur.execute(
                    f""" INSERT INTO ClanPlayer(clan_id,player_id) VALUES ({clan_id}, {player_id}) """)
            await conn.commit()

        return Player(player_id, player_name, dis_id)

    async def remove_player_from_clan(self, clan_id: int, player_id: int) -> list:
        """ Remove player from clan """

        clan = await self.get_clan_by_id(clan_id)

        if not clan:
            raise ObjectDoesntExistsInDBError('This clan doesn\'t exist')

        player = await self.get_player_by_id(player_id)

        if not player:
            raise ObjectDoesntExistsInDBError('This player doesn\'t exist')

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" SELECT * FROM ClanPlayer WHERE clan_id=:clan_id AND player_id=:player_id """,
                              {'player_id': player_id, 'clan_id': clan_id})
            clan_player_result = await cur.fetchone()

            if not clan_player_result:
                raise PlayerNotInClanError('Player is not in the clan')

            await cur.execute(""" DELETE FROM ClanPlayer WHERE clan_id = ? AND player_id = ? """, (clan_id, player_id))
            await conn.commit()
        return await self.get_players_from_clan(clan_id)

    async def get_player_by_id(self, player_id: int) -> Player or None:
        """ Gets Player by Id """
        if not player_id:
            raise ParameterIsNullError("Player id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Player WHERE id=:id """, {'id': player_id})
            result = await cur.fetchone()

        if not result:
            return None

        return Player(result[0], result[1], result[2])

    async def get_player_by_id_and_clan_id(self, player_id: int, clan_id: int) -> Player or None:
        """ Gets Player by Id and clan id """
        if not (player_id and clan_id):
            raise ParameterIsNullError("Player id and clan id cant be empty")
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                                SELECT p.*
                                FROM Player p
                                JOIN ClanPlayer cp ON p.id = cp.player_id
                                WHERE p.id = :player_id AND cp.clan_id = :clan_id""",
                              {'player_id': player_id, 'clan_id': clan_id})
            result = await cur.fetchone()

        if not result:
            raise ObjectDoesntExistsInDBError("Player doesn't exist!")

        return Player(result[0], result[1], result[2])

    async def get_player_by_name_and_clan_id(self, player_name: str, clan_id: int) -> Player or None:
        """ Gets Players by Name and clan id """
        if not (player_name and clan_id):
            raise ParameterIsNullError("Player name and clan id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                                SELECT p.*
                                FROM Player p
                                JOIN ClanPlayer cp ON p.id=cp.player_id
                                WHERE p.name=:player_name AND cp.clan_id=:clan_id""",
                              {'player_name': player_name})
            result = await cur.fetchone()

        if not result:
            raise ObjectDoesntExistsInDBError('Player doesnt exist')

        return Player(result[0], result[1], result[2])

    async def get_player_by_discord_id_and_clan_id(self, discord_id: int, clan_id: int) -> list:
        """ Gets Players by Name and clan id """
        if not (discord_id and clan_id):
            raise ParameterIsNullError("Discord id and clan id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                                SELECT p.*
                                FROM Player p
                                JOIN ClanPlayer cp ON p.id = cp.player_id
                                WHERE p.discord_id = :discord_id AND cp.clan_id = :clan_id""",
                              {'discord_id': discord_id})
            results = await cur.fetchall()
        if not results:
            raise ObjectDoesntExistsInDBError(
                'You haven\'t registered with the bot! Please run **/player create** `name`.')

        return [Player(result[0], result[1], result[2]) for result in results]

    async def get_player_by_name(self, player_name: str) -> Player or None:
        """ Gets Players by Name and clan id """
        if not player_name:
            raise ParameterIsNullError("Player name cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                                SELECT *
                                FROM Player                
                                WHERE name=:player_name""",
                              {'player_name': player_name})
            result = await cur.fetchone()
        if not result:
            raise ObjectDoesntExistsInDBError('Player doesnt exist')
        return Player(result[0], result[1], result[2])

    async def get_player_by_discord_id(self, discord_id: int) -> list:
        """ Gets Player by discord name and id """
        if not discord_id:
            raise ParameterIsNullError("Discord id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                        SELECT * FROM Player WHERE discord_id=:discord_id """,
                              {'discord_id': discord_id}
                              )
            results = await cur.fetchall()

            if not results:
                raise ObjectDoesntExistsInDBError(
                    'You haven\'t registered with the bot! Please run **/player create** `name`.')

        return [Player(result[0], result[1], result[2]) for result in results]

    async def get_players(self) -> list:
        """ Gets all players """
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" SELECT * FROM Player """)
            results = await cur.fetchall()

        return [Player(result[0], result[1], result[2]) for result in results]

    async def get_players_from_clan(self, clan_id: int) -> list:
        """ Gets all players from clan"""
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(f"""
                            SELECT p.*
                            FROM ClanPlayer cp
                            JOIN Player p ON cp.player_id = p.id
                            WHERE cp.clan_id = {clan_id};""")
            results = await cur.fetchall()

        return [Player(result[0], result[1], result[2]) for result in results]

    async def get_players_from_clan_name(self, clan_name: str) -> list:
        """ Gets all players from clan"""
        clan = await self.get_clan_by_name(clan_name)
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(f"""
                            SELECT p.*
                            FROM ClanPlayer cp
                            JOIN Player p ON cp.player_id = p.id
                            WHERE cp.clan_id = {clan.clan_id};""")
            results = await cur.fetchall()

        player_array = [result for result in results]

        return player_array

    async def update_player(self, player: Player) -> Player:
        """ Update entry in player table """

        player_to_be_updated = await self.get_player_by_id(player.player_id)
        if not player_to_be_updated:
            raise ObjectDoesntExistsInDBError(f'player id {player.player_id}')

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if player_to_be_updated.name != player.name:
                await cur.execute("""
                            SELECT * FROM Player WHERE name=:name"""
                                  , {"name": player.name})
                result = await cur.fetchone()

                if result:
                    raise ObjectExistsInDBError(result)
            await cur.execute(""" 
                            UPDATE Player SET name=:name,discord_id=:discord_id WHERE id=:id """
                              , {'id': player.player_id, 'name': player.name, "discord_id": player.discord_id})
            await conn.commit()
            await cur.execute("SELECT * FROM Player WHERE id=:id", {'id': player.player_id})
            updated_result = await cur.fetchone()
        return Player(updated_result[0], updated_result[1], updated_result[2])

    async def delete_player_by_discord_id_name(self, dis_id: int, name: str):
        """ 'deletes' player by discord id and name (removes discord id) """
        players = await self.get_player_by_discord_id(dis_id)
        player = None
        for player_iter in players:
            if player_iter.name == name:
                player = player_iter
        if not player:
            raise ObjectDoesntExistsInDBError(f'You dont have player with name: {name}')

        player.discord_id = None
        await self.update_player(player)

    async def add_player_to_clan(self, clan_id: int, player_id: int) -> tuple:
        """ Add player to clan wih or without role"""
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Clan WHERE id=:id """, {'id': clan_id})
            clan_result = await cur.fetchone()

            if not clan_result:
                raise ObjectDoesntExistsInDBError

            clan = Clan(clan_result[0], clan_result[1], clan_result[2])
            await cur.execute(""" SELECT * FROM Player WHERE id=:id """, {'id': player_id})
            player_result = await cur.fetchone()

            if not player_result:
                raise ObjectDoesntExistsInDBError

            player = Player(player_result[0], player_result[1], player_result[2])

            await cur.execute(""" SELECT * FROM ClanPlayer WHERE player_id=:player_id  """,
                              {'player_id': player_id})
            clan_player_result = await cur.fetchone()

            if clan_player_result:
                raise PlayerAlreadyInClanError('Player is already in another clan')

            await cur.execute(""" SELECT * FROM ClanPlayer WHERE player_id=:player_id AND clan_id=:clan_id """,
                              {'player_id': player_id, 'clan_id': clan_id})
            clan_player_result = await cur.fetchone()

            if clan_player_result:
                raise PlayerAlreadyInClanError('Player is in the clan')

            await cur.execute(""" INSERT INTO ClanPlayer(clan_id, player_id) 
                            VALUES (:clan_id,:player_id) """
                              , {'clan_id': clan_id, 'player_id': player_id})

            await conn.commit()
        # clan_role = await self.get_clan_role_by_id(clan_role_id)
        return clan, player

    async def get_clan_player(self, player_id: int) -> tuple or None:
        """ get clanplayer """
        player = await self.get_player_by_id(player_id)

        if not player:
            raise ObjectDoesntExistsInDBError('This player doesn\'t exist')

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" 
                                SELECT p.*, c.*
                                FROM Player p
                                JOIN ClanPlayer cp ON p.id = cp.player_id
                                JOIN Clan c ON cp.clan_id = c.id
                                WHERE p.id = :player_id""",
                              {'player_id': player_id})
            result = await cur.fetchone()
        if not result:
            raise ObjectDoesntExistsInDBError(f'Player is not in clan')

        return Player(result[0], result[1], result[2]), Clan(result[3], result[4], result[5])

    async def create_clan_battle(self, clan_id: int, cb_name: str, start_date_input: str) -> ClanBattle:
        """ Insert a new cb into the CB table.
            start_date: date format is DD-MM-YYY
        """
        if not (cb_name and clan_id and start_date_input):
            raise ParameterIsNullError("Cb name, start date and clan id cant be empty")
        try:
            start_date_object = datetime.strptime(start_date_input, "%d-%m-%Y").replace(hour=13, minute=0, second=0)
            end_date_object = start_date_object + timedelta(days=4)
            end_date_object = end_date_object.replace(hour=8, minute=0, second=0)
            start_date = start_date_object.strftime("%d-%m-%Y %H:%M:%S")
            end_date = end_date_object.strftime("%d-%m-%Y %H:%M:%S")
        except ValueError as e:
            raise ValueError('Wrong date format')
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM ClanBattle WHERE name=:name AND clan_id=:clan_id""",
                              {'name': cb_name, 'clan_id': clan_id})
            result = await cur.fetchone()

            if result:
                raise ObjectExistsInDBError(f'Clan battle with name {result[1]} already exists')

            await cur.execute(""" INSERT INTO ClanBattle(name, lap, tier, start_date, end_date, active, clan_id) 
                                VALUES (:name,:lap,:tier,:start_date,:end_date,:active,:clan_id) """,
                              {'name': cb_name, 'lap': 1, 'tier': 1, 'clan_id': clan_id, 'start_date': start_date
                                  , 'end_date': end_date, 'active': False})

            cb = ClanBattle(cur.lastrowid, cb_name, clan_id, start_date, end_date, False)

            await conn.commit()

        return cb

    async def get_clan_battle_by_id(self, cb_id: int) -> ClanBattle or None:
        """ Gets cb by Id """
        if not cb_id:
            raise ParameterIsNullError("Cb id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM ClanBattle WHERE id=:id """, {'id': cb_id})
            result = await cur.fetchone()

        if not result:
            return None

        return ClanBattle(result[0], result[1], result[7], result[4], result[5], result[6], lap=result[2],
                          tier=result[3])

    async def exists_cb_in_date_by_clan_id(self, start_date_input: str, clan_id: int) -> str or None:
        """ Gets cb by Id """
        if not (start_date_input and clan_id):
            raise ParameterIsNullError("Date and clan id cant be empty")

        start_date_object = datetime.strptime(start_date_input, "%d-%m-%Y").replace(hour=13, minute=0, second=0)
        start_date = start_date_object.strftime("%d-%m-%Y %H:%M:%S")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM ClanBattle WHERE clan_id=:clan_id 
                                AND :date BETWEEN start_date AND end_date; """,
                              {'date': start_date, 'clan_id': clan_id})
            result = await cur.fetchone()

        if not result:
            return None

        return result[1]

    async def get_clan_battle_by_name_and_clan_id(self, name: str, clan_id: int) -> ClanBattle or None:
        """ Gets cb by name and clan id """
        if not (clan_id and name):
            raise ParameterIsNullError("Cb name and clan id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                        SELECT * FROM ClanBattle WHERE clan_id=:clan_id AND name=:name"""
                              , {'clan_id': clan_id, 'name': name})
            result = await cur.fetchone()

            if not result:
                return None

        return ClanBattle(result[0], result[1], result[7], result[4], result[5], result[6], lap=result[2],
                          tier=result[3])

    async def get_clan_battles_in_clan(self, clan_id: int) -> list:
        """ Gets all cbs from clan"""
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(f"""SELECT * FROM ClanBattle WHERE clan_id=:clan_id""", {'clan_id': clan_id})
            results = await cur.fetchall()

        return [ClanBattle(result[0], result[1], result[7], result[4], result[5], result[6], lap=result[2],
                           tier=result[3]) for result in results]

    async def get_clan_battle_active_by_clan_id(self, clan_id: int) -> ClanBattle or None:
        """ Get clan battle active """
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(f"""SELECT * FROM ClanBattle WHERE clan_id=:clan_id AND active=:active""",
                              {'clan_id': clan_id, 'active': True})
            result = await cur.fetchone()

        if not result:
            raise NoActiveCBError('There is no active clan battle')

        return ClanBattle(result[0], result[1], result[7], result[4], result[5], result[6], lap=result[2],
                          tier=result[3])

    async def set_clan_battle_active_by_name(self, cb_name: str, clan_id: int) -> ClanBattle:
        """ Set clan battle to active """
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(f"""SELECT * FROM ClanBattle WHERE clan_id=:clan_id AND active=:active""",
                              {'clan_id': clan_id, 'active': True})
            result = await cur.fetchone()

            if result:
                raise ThereIsAlreadyActiveCBError(result)

            await cur.execute(""" UPDATE ClanBattle SET active=:active WHERE name=:name AND clan_id=:clan_id """
                              , {'active': True, 'name': cb_name, "clan_id": clan_id})
            await conn.commit()
            await cur.execute("SELECT * FROM ClanBattle WHERE name=:name AND clan_id=:clan_id """
                              , {'name': cb_name, "clan_id": clan_id})
            updated_result = await cur.fetchone()

        return ClanBattle(updated_result[0], updated_result[1], updated_result[7], updated_result[4], updated_result[5],
                          updated_result[6], lap=updated_result[2], tier=updated_result[3])

    async def set_clan_battle_inactive_by_name(self, cb_name: str, clan_id: int) -> ClanBattle:
        """ Set clan battle to inactive """
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" UPDATE ClanBattle SET active=:active WHERE name=:name AND clan_id=:clan_id """
                              , {'active': False, 'name': cb_name, "clan_id": clan_id})
            await conn.commit()
            await cur.execute("SELECT * FROM ClanBattle WHERE name=:name AND clan_id=:clan_id """
                              , {'name': cb_name, "clan_id": clan_id})
            updated_result = await cur.fetchone()

        return ClanBattle(updated_result[0], updated_result[1], updated_result[7], updated_result[4], updated_result[5],
                          updated_result[6], lap=updated_result[2], tier=updated_result[3])

    async def update_clan_batte(self, clan_battle: ClanBattle) -> ClanBattle:
        """ Update entry in clanbattle table """
        clan_battle_to_be_updated = await self.get_clan_battle_by_id(clan_battle.cb_id)

        if not clan_battle_to_be_updated:
            raise ObjectDoesntExistsInDBError(f'cb id {clan_battle_to_be_updated.clan_id}')

        if not (clan_battle.name and clan_battle.lap and clan_battle.tier):
            raise ParameterIsNullError("ClanBattle name, lap, tier cant be empty")
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            if clan_battle_to_be_updated.name != clan_battle.name:

                await cur.execute("""
                               SELECT * FROM ClanBattle WHERE name=:name AND clan_id=:clan_id"""
                                  , {'name': clan_battle.name, 'clan_id': clan_battle.clan_id})
                result = await cur.fetchone()
                if result:
                    raise ObjectExistsInDBError(result)

            await cur.execute(""" UPDATE ClanBattle SET name=:name,lap=:lap,tier=:tier, active=:active WHERE id=:id """
                              , {'name': clan_battle.name, 'lap': clan_battle.lap, "tier": clan_battle.tier,
                                 "id": clan_battle.cb_id, 'active': clan_battle.active})
            await conn.commit()
            await cur.execute("SELECT * FROM ClanBattle WHERE id=:id", {'id': clan_battle.cb_id})
            updated_result = await cur.fetchone()
        return ClanBattle(updated_result[0], updated_result[1], updated_result[7], updated_result[4], updated_result[5],
                          updated_result[6], lap=updated_result[2], tier=updated_result[3])

    async def delete_clan_battle_by_name_and_clan_id(self, cb_name: str, clan_id: int):
        """ Deletes team composition, boss bookings, boss, pcdi connected to cb and cb itself """
        cb = await self.get_clan_battle_by_name_and_clan_id(cb_name, clan_id)
        if not cb:
            raise ObjectDoesntExistsInDBError(f'Clan battle {cb_name} doesnt exists in your clan')
        pcdis = await self.get_pcdis_by_cb_id(cb.cb_id)
        bosses = await self.get_bosses(cb.cb_id)

        for pcdi in pcdis:
            await self.delete_tc_by_pcdi_id(pcdi.pcbdi_id)
        await self.delete_pcdis_by_cb_id(cb.cb_id)

        for boss in bosses:
            await self.delete_bookings_by_boss_id(boss.boss_id)
        await self.delete_bosses_by_cb_id(cb.cb_id)

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                            DELETE FROM ClanBattle WHERE id=:id""",
                              {'id': cb.cb_id})
            await conn.commit()

    async def create_player_cb_day_info(self, cb_id, player_id) -> PlayerCBDayInfo:
        """ Insert a new day info in to table. """
        if not (cb_id and player_id):
            raise ParameterIsNullError("Cb id and player id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(f""" SELECT * FROM PlayerCBDayInfo WHERE player_id={player_id} AND cb_id={cb_id}""")
            result = await cur.fetchall()
            # noinspection PyTypeChecker
            cb_day = len(result)  # pycharm thinks this should be PlayerCBDayInfo because of typehint

            if cb_day >= 5:
                raise PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached(result)

            cb_day += 1

            await cur.execute(""" 
                        INSERT INTO PlayerCBDayInfo(hits, reset, cb_day, player_id, cb_id) 
                        VALUES (:hits,:reset,:cb_day,:player_id,:cb_id) """
                              , {'reset': True, 'hits': 3, 'cb_day': cb_day, 'player_id': player_id, 'cb_id': cb_id})

            pcbdi = PlayerCBDayInfo(cur.lastrowid, cb_day, cb_id, player_id)

            await conn.commit()

        return pcbdi

    async def get_pcdi_by_id(self, pcdi_id: int) -> PlayerCBDayInfo or None:
        """ Gets pcdi by id"""
        if not pcdi_id:
            raise ParameterIsNullError("PCDI id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute("""SELECT * FROM PlayerCBDayInfo WHERE id=:id""", {'id': pcdi_id})
            result = await cur.fetchone()

        if not result:
            return None

        return PlayerCBDayInfo(result[0], result[6], result[7], result[8], overflow=result[1], ovf_time=result[2],
                               ovf_comp=result[3], hits=result[4], reset=result[5])

    async def get_pcdis_by_cb_id(self, cb_id: int) -> list:
        """ Gets pcdis by cb id"""
        if not cb_id:
            raise ParameterIsNullError("Cb id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute("""SELECT * FROM PlayerCBDayInfo WHERE cb_id=:cb_id""", {'cb_id': cb_id})
            results = await cur.fetchall()

        return [PlayerCBDayInfo(result[0], result[6], result[7], result[8], overflow=result[1], ovf_time=result[2],
                                ovf_comp=result[3], hits=result[4], reset=result[5]) for result in results]

    async def get_pcdis_by_player_id(self, player_id: int) -> list:
        """ Gets player by cb id"""
        if not player_id:
            raise ParameterIsNullError("Player id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute("""SELECT * FROM PlayerCBDayInfo WHERE player_id=:player_id""", {'player_id': player_id})
            results = await cur.fetchall()

        return [PlayerCBDayInfo(result[0], result[6], result[7], result[8], overflow=result[1], ovf_time=result[2],
                                ovf_comp=result[3], hits=result[4], reset=result[5]) for result in results]

    async def get_pcdi_by_player_id_and_cb_id_and_day(self, player_id: int, cb_id: int, day: int) -> PlayerCBDayInfo:
        """ Gets pcdi by player id and cb id and day (optional) """
        if not player_id:
            raise ParameterIsNullError("Player id cant be empty")

        if day > 5:
            raise ClanBattleCantHaveMoreThenFiveDaysError(f"Day {day}")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if day:
                await cur.execute("""
                            SELECT * FROM PlayerCBDayInfo WHERE player_id=:player_id AND cb_day=:cb_day AND cb_id=:cb_id""",
                                  {'player_id': player_id, 'cb_day': day, 'cb_id': cb_id})
            else:
                await cur.execute(""" 
                            SELECT * FROM PlayerCBDayInfo WHERE player_id=:player_id AND cb_id=:cb_id""",
                                  {'player_id': player_id, 'cb_id': cb_id})
            result = await cur.fetchone()

        return PlayerCBDayInfo(result[0], result[6], result[7], result[8], overflow=result[1], ovf_time=result[2],
                               ovf_comp=result[3], hits=result[4], reset=result[5])

    async def get_pcdi_by_player_id_and_cb_id(self, player_id: int, cb_id: int) -> list:
        """ Gets pcdis by player id and cb id """
        if not player_id:
            raise ParameterIsNullError("Player id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                        SELECT * FROM PlayerCBDayInfo WHERE player_id=:player_id AND cb_id=:cb_id""",
                              {'player_id': player_id, 'cb_id': cb_id})
            results = await cur.fetchall()

        return [PlayerCBDayInfo(result[0], result[6], result[7], result[8], overflow=result[1], ovf_time=result[2],
                                ovf_comp=result[3], hits=result[4], reset=result[5]) for result in results]

    async def get_all_pcdi_ovf_by_cb_id(self, cb_id: int, ovf: bool, day=0) -> tuple:
        """ Gets pcdi and players by cb id and day (optional) and ovf
            Returns tuple of pcdi list tuple[0] and players list tuple[1]
         """
        if not cb_id:
            raise ParameterIsNullError("Cb id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if day:
                await cur.execute("""
                            SELECT pcdi.*,p.* FROM PlayerCBDayInfo AS pcdi  JOIN Player AS p ON pcdi.player_id = p.id 
                            WHERE pcdi.cb_id=:cb_id AND pcdi.cb_day=:cb_day AND pcdi.overflow=:overflow""",
                                  {'cb_id': cb_id, 'cb_day': day, 'overflow': ovf})
            else:
                await cur.execute(""" 
                            SELECT pcdi.*,p.* FROM PlayerCBDayInfo AS pcdi  JOIN Player AS p ON pcdi.player_id = p.id 
                            WHERE pcdi.cb_id=:cb_id AND pcdi.overflow=:overflow""",
                                  {'cb_id': cb_id, 'cb_day': day, 'overflow': ovf})
            results = await cur.fetchall()

        return tuple(
            [(PlayerCBDayInfo(result[0], result[6], result[7], result[8], overflow=result[1], ovf_time=result[2],
                              ovf_comp=result[3], hits=result[4], reset=result[5]),
              Player(result[8], result[10], result[11])) for result in
             results])

    async def get_pcdi_by_cb_id_and_hits(self, cb_id: int, day: int) -> list:
        """ Gets players and hits left that are more then 0 """
        if not (cb_id and day):
            raise ParameterIsNullError("Cb id and day cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute("""
                                SELECT p.name, pcdi.hits
                                FROM Player p
                                JOIN PlayerCBDayInfo pcdi ON p.id = pcdi.player_id
                                WHERE pcdi.cb_id = :cb_id AND pcdi.hits > 0 AND pcdi.cb_day=:cb_day""",
                              {'cb_id': cb_id, 'cb_day': day})
            results = await cur.fetchall()
        return [result for result in results]

    async def update_pcdi(self, pcdi: PlayerCBDayInfo) -> PlayerCBDayInfo:
        """ Update pcdi table """
        pcdi_to_be_updated = await self.get_pcdi_by_id(pcdi.pcbdi_id)

        if not pcdi_to_be_updated:
            raise ObjectDoesntExistsInDBError(f'pcdi id {pcdi.pcbdi_id}')

        if not pcdi_to_be_updated.cb_day:
            raise ParameterIsNullError("Reset and cb_day cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute("""UPDATE PlayerCBDayInfo SET overflow=:overflow,ovf_time=:ovf_time,ovf_comp=:ovf_comp,
                              hits=:hits,reset=:reset,cb_day=:cb_day WHERE id=:id """,
                              {'overflow': pcdi.overflow, 'ovf_time': pcdi.ovf_time, 'ovf_comp': pcdi.ovf_comp,
                               'hits': pcdi.hits, 'reset': pcdi.reset, 'cb_day': pcdi.cb_day, 'id': pcdi.pcbdi_id})
            await conn.commit()
            await cur.execute("SELECT * FROM PlayerCBDayInfo WHERE id=:id", {'id': pcdi.pcbdi_id})
            updated_result = await cur.fetchone()

        return PlayerCBDayInfo(updated_result[0], updated_result[6], updated_result[7], updated_result[8],
                               overflow=updated_result[1], ovf_time=updated_result[2],
                               ovf_comp=updated_result[3], hits=updated_result[4], reset=updated_result[5])

    async def delete_pcdis_by_cb_id(self, cb_id: int):
        """ deletes all pcdis by cb id"""
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                            DELETE FROM PlayerCBDayInfo WHERE cb_id=:cb_id""",
                              {'cb_id': cb_id})
            await conn.commit()

    async def get_today_hits_left(self, day: int, cb_id: int) -> int or None:
        """ Gets hits left for today """
        if not cb_id:
            raise ParameterIsNullError("Cb id cant be empty")

        if day > 5:
            raise ClanBattleCantHaveMoreThenFiveDaysError(f"Day {day}")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute("""
                               SELECT SUM(hits) FROM PlayerCBDayInfo WHERE cb_day=:cb_day AND cb_id=:cb_id""",
                              {'cb_day': day, 'cb_id': cb_id})

            result = await cur.fetchone()

        if not result:
            raise ValueError()

        return result[0]

    async def create_team_composition(self, name: str, pcdi_id: int, used=False) -> TeamComposition:
        """ Insert a new team the Team Composition table. """
        if not (name and pcdi_id):
            raise ParameterIsNullError("Team name and pcdi_id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT * FROM TeamComposition WHERE name=:name AND pcdi_id=:id",
                              {'id': pcdi_id, 'name': name})
            result = await cur.fetchone()
            if result:
                raise ObjectExistsInDBError(f'You have created team composition {name} already for today')
            await cur.execute(""" INSERT INTO TeamComposition(name, used, pcdi_id) VALUES (:name, :used, :pcdi_id) """,
                              {'name': name, 'pcdi_id': pcdi_id, 'used': used})
            tc = TeamComposition(cur.lastrowid, name, used, pcdi_id)

            await conn.commit()

        return tc

    async def get_team_composition_by_id(self, tc_id: int) -> TeamComposition or None:
        """ Team composition by Id """
        if not tc_id:
            raise ParameterIsNullError("TC id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM TeamComposition WHERE id=:id """, {'id': tc_id})
            result = await cur.fetchone()

        if not result:
            return None

        return TeamComposition(result[0], result[1], result[2], result[3])

    async def get_team_composition_by_comp_name_and_pcdi_id(self, comp_name: str,
                                                            pcdi_id: int) -> TeamComposition or None:
        """ Team composition by comp name and pcdi id"""
        if not (pcdi_id and comp_name):
            raise ParameterIsNullError("Pcdi id cant and comp name be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM TeamComposition WHERE name=:name AND pcdi_id=:pcdi_id """,
                              {'name': comp_name, 'pcdi_id': pcdi_id})
            result = await cur.fetchone()

        if not result:
            return None

        return TeamComposition(result[0], result[1], result[2], result[3])

    async def get_team_compositions_by_pcdi(self, pcdi_id: int) -> list:
        """ Team composition by Id """
        if not pcdi_id:
            raise ParameterIsNullError("PCDI id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM TeamComposition WHERE pcdi_id=:pcdi_id """, {'pcdi_id': pcdi_id})
            results = await cur.fetchall()

        return [TeamComposition(result[0], result[1], result[2], result[3]) for result in results]

    async def update_team_composition(self, tc: TeamComposition) -> TeamComposition:
        """ Update team compositon """

        tc_to_be_updated = await self.get_team_composition_by_id(tc.tc_id)
        if not tc_to_be_updated:
            raise ObjectDoesntExistsInDBError(f'Team composition id {tc.tc_id}')

        if not tc.name:
            raise ParameterIsNullError("Team composition  name, used cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" UPDATE TeamComposition SET name=:name,used=:used WHERE id=:id """,
                              {'name': tc.name, 'used': tc.used, 'id': tc.tc_id})
            await conn.commit()
            await cur.execute("SELECT * FROM TeamComposition WHERE id=:id", {'id': tc.tc_id})
            updated_result = await cur.fetchone()

        return TeamComposition(updated_result[0], updated_result[1], updated_result[2], updated_result[3])

    async def delete_tc_by_pcdi_id(self, pcdi_id: int):
        """ deletes all tc by pcdi id"""
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                            DELETE FROM TeamComposition WHERE pcdi_id=:pcdi_id""",
                              {'pcdi_id': pcdi_id})
            await conn.commit()

    async def create_boss(self, name: str, boss_number: int, ranking: int, cb_id: int) -> Boss:
        """ Insert a new boss into the Boss table. """
        if not (name and boss_number and cb_id):
            raise ParameterIsNullError("Boss name, cb_id and number cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Boss WHERE name=:name AND cb_id=:cb_id""",
                              {'name': name, 'cb_id': cb_id})
            result = await cur.fetchone()

            if result:
                raise ObjectExistsInDBError(result)

            await cur.execute(""" INSERT INTO Boss(name, boss_number, ranking, active, cb_id) 
                            VALUES (:name,:boss_number,:ranking,0,:cb_id) """,
                              {'name': name, 'boss_number': boss_number, 'ranking': ranking, 'cb_id': cb_id})
            boss = Boss(cur.lastrowid, name, boss_number, ranking, False, cb_id)

            await conn.commit()

        return boss

    async def get_boss_by_id(self, boss_id: int) -> Boss or None:
        """ Gets Boss by Id """
        if not boss_id:
            raise ParameterIsNullError("Boss id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Boss WHERE id=:id """, {'id': boss_id})
            result = await cur.fetchone()

        if not result:
            return None

        return Boss(result[0], result[1], result[2], result[3], result[4], result[5])

    async def get_boss_by_boss_number(self, boss_number: int, cb_id: int) -> Boss or None:
        """ Gets Boss by number  and cb"""
        if not (boss_number and cb_id):
            raise ParameterIsNullError("Boss number and cb id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Boss WHERE boss_number=:boss_number AND cb_id=:cb_id""",
                              {'boss_number': boss_number, 'cb_id': cb_id})
            result = await cur.fetchone()

        if not result:
            raise ObjectDoesntExistsInDBError('Boss doesnt exists for this cb')

        return Boss(result[0], result[1], result[2], result[3], result[4], result[5])

    async def get_active_boss_by_cb_id(self, cb_id: int) -> Boss or None:
        """ Gets active boss by cb id"""
        if not cb_id:
            raise ParameterIsNullError("Cb id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Boss WHERE active=:active AND cb_id=:cb_id""",
                              {'active': True, 'cb_id': cb_id})
            result = await cur.fetchone()

        if not result:
            raise ValueError('No boss is active (how?????)')

        return Boss(result[0], result[1], result[2], result[3], result[4], result[5])

    async def get_bosses(self, cb_id) -> list:
        """ Gets all bosses """
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" SELECT * FROM Boss WHERE cb_id=:cb_id""", {'cb_id': cb_id})
            results = await cur.fetchall()

        return [Boss(result[0], result[1], result[2], result[3], result[4], result[5]) for result in results]

    async def update_boss(self, boss: Boss) -> Boss:
        """ Update boss """

        boss_to_be_updated = await self.get_boss_by_id(boss.boss_id)
        if not boss_to_be_updated:
            raise ObjectDoesntExistsInDBError(f'Boss id {boss.boss_id}')

        if not (boss.name and boss.boss_number and boss.ranking):
            raise ParameterIsNullError("Boss name, boss_number, ranking cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                        UPDATE Boss SET name=:name,boss_number=:boss_number,ranking=:ranking,active=:active
                        WHERE id=:id """,
                              {'name': boss.name, 'boss_number': boss.boss_number, 'ranking': boss.ranking,
                               'active': boss.active,
                               'id': boss.boss_id})
            await conn.commit()
            await cur.execute("SELECT * FROM Boss WHERE id=:id", {'id': boss.boss_id})
            updated_result = await cur.fetchone()

        return Boss(updated_result[0], updated_result[1], updated_result[2], updated_result[3], updated_result[4],
                    updated_result[5])

    async def delete_bosses_by_cb_id(self, cb_id: int):
        """ deletes all bosses by cb id"""
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                            DELETE FROM Boss WHERE cb_id=:cb_id""",
                              {'cb_id': cb_id})
            await conn.commit()

    async def create_boss_booking(self, lap: int, curr_lap: int, overflow: bool, comp_name: str,
                                  boss_id: int, player_id: int, cb_id: int, ovf_time='') -> BossBooking:
        """ Insert boss booking into table. """
        if not (lap and comp_name and boss_id and player_id and cb_id):
            raise ParameterIsNullError("Cb lap and comp_name boss_id cant player_id be empty")

        active_boss = await self.get_active_boss_by_cb_id(cb_id)
        boss = await self.get_boss_by_id(boss_id)
        if curr_lap == lap and active_boss.boss_number > boss.boss_number or curr_lap > lap:
            raise CantBookDeadBossError('You cant book dead boss')

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if overflow and not ovf_time:
                raise ParameterIsNullError("Hit is marked as ovf but ovf_time is not set")

            elif overflow and ovf_time:
                await cur.execute(""" INSERT INTO BossBooking(lap, overflow, ovf_time, comp_name, boss_id, player_id) 
                                VALUES (:lap,:overflow,:ovf_time,:comp_name,:boss_id,:player_id) """,
                                  {'lap': lap, 'overflow': overflow, 'ovf_time': ovf_time, 'comp_name': comp_name,
                                   'boss_id': boss_id, 'player_id': player_id})
                bb = BossBooking(cur.lastrowid, lap, comp_name, boss_id, player_id, overflow=overflow,
                                 ovf_time=ovf_time)
            else:
                await cur.execute(""" INSERT INTO BossBooking(lap, comp_name, boss_id, player_id) 
                                VALUES (:lap,:comp_name,:boss_id,:player_id) """,
                                  {'lap': lap, 'comp_name': comp_name, 'boss_id': boss_id,
                                   'player_id': player_id})
                bb = BossBooking(cur.lastrowid, lap, comp_name, boss_id, player_id)

            await conn.commit()

        return bb
    
    async def remove_boss_booking(self, lap: int, curr_lap: int, overflow: bool, comp_name: str,
                                  boss_id: int, player_id: int, cb_id: int, ovf_time='') -> BossBooking:
        """ Remove boss booking from table. """
        if not (lap and comp_name and boss_id and player_id and cb_id):
            raise ParameterIsNullError("Cb lap and comp_name boss_id cant player_id be empty")

        active_boss = await self.get_active_boss_by_cb_id(cb_id)
        boss = await self.get_boss_by_id(boss_id)
        if curr_lap == lap and active_boss.boss_number > boss.boss_number or curr_lap > lap:
            raise CantBookDeadBossError('You cant book dead boss')

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if overflow and not ovf_time:
                raise ParameterIsNullError("Hit is marked as ovf but ovf_time is not set")

            elif overflow and ovf_time:
                bb = BossBooking(cur.lastrowid, lap, comp_name, boss_id, player_id, overflow=overflow,
                                 ovf_time=ovf_time)
                await cur.execute(""" DELETE FROM BossBooking WHERE lap = ? and comp_name = ? and boss_id = ? and player_id = ? """, (lap, comp_name, boss_id, player_id))
            else:
                bb = BossBooking(cur.lastrowid, lap, comp_name, boss_id, player_id)
                await cur.execute(""" DELETE FROM BossBooking WHERE lap = ? and comp_name = ? and boss_id = ? and player_id = ? """, (lap, comp_name, boss_id, player_id))

            await conn.commit()

        return bb

    async def get_boss_booking_by_id(self, bb_id: int) -> BossBooking or None:
        """ Gets boss booking by Id """
        if not bb_id:
            raise ParameterIsNullError("Boss booking id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM BossBooking WHERE id=:id """, {'id': bb_id})
            result = await cur.fetchone()

        if not result:
            return None

        return BossBooking(result[0], result[1], result[4], result[5], result[6], overflow=result[2],
                           ovf_time=result[3])

    async def get_boss_bookings_by_player_id(self, player_id: int) -> list:
        """ Gets boss bookings by player Id """
        if not player_id:
            raise ParameterIsNullError("Player id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM BossBooking WHERE player_id=:player_id """, {'player_id': player_id})
            results = await cur.fetchall()

        return [BossBooking(result[0], result[1], result[4], result[5], result[6], overflow=result[2],
                            ovf_time=result[3]) for result in results]

    async def get_boss_bookings_by_boss_id(self, boss_id: int) -> list:
        """ Gets boss bookings by player Id """
        if not boss_id:
            raise ParameterIsNullError("Boss id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM BossBooking WHERE boss_id=:boss_id """, {'boss_id': boss_id})
            results = await cur.fetchall()

        return [BossBooking(result[0], result[1], result[4], result[5], result[6], overflow=result[2],
                            ovf_time=result[3]) for result in results]

    async def get_all_boss_bookings_by_lap(self, cur_boss: int, desired_boss: int, cur_lap: int, lap: int, cb_id: int) \
            -> tuple:
        """ Gets all boss bookings that are relevant in lap
        Returning tuple [0] booking [1] boss [2] player"""
        if not (cb_id and lap and cur_boss):
            raise ParameterIsNullError("Boss id and current lap and current boss cant be empty")
        if cur_lap == lap and (cur_boss > desired_boss):
            raise DesiredBossIsDeadError('Boss is dead')
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(f"""
                            SELECT bb.*, b.*, p.*
                            FROM BossBooking bb
                            JOIN Boss b ON b.id = bb.boss_id
                            JOIN Player p ON p.id = bb.player_id
                            WHERE b.boss_number={desired_boss} AND b.cb_id={cb_id} AND bb.lap={lap}""")
            results = await cur.fetchall()

        return tuple([(
            BossBooking(result[0], result[1], result[4], result[5], result[6], overflow=result[2],
                        ovf_time=result[3]),
            Boss(result[7], result[8], result[9], result[10], result[1], result[12]),
            Player(result[13], result[14], result[15])
        ) for result in results])

    async def update_boss_booking(self, bb: BossBooking) -> BossBooking:
        """ Update boss booking"""
        bb_to_be_updated = await self.get_boss_booking_by_id(bb.boss_booking_id)
        if not bb_to_be_updated:
            raise ObjectDoesntExistsInDBError(f'Boss booking id {bb.boss_booking_id}')

        if not (bb.lap and bb.comp_name):
            raise ParameterIsNullError("Boss booking lap, comp_name cant be empty")

        if bb.overflow and not bb.ovf_time:
            raise ParameterIsNullError("Hit is marked as ovf but ovf_time is not set")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if bb.overflow and bb.ovf_time:
                await cur.execute(""" 
                               UPDATE BossBooking 
                               SET lap=:lap,overflow=:overflow,ovf_time=:ovf_time,comp_name=:comp_name
                               WHERE id=:id """,
                                  {'lap': bb.lap, 'overflow': bb.overflow, 'ovf_time': bb.ovf_time,
                                   'comp_name': bb.comp_name, 'id': bb.boss_booking_id})
            else:
                await cur.execute(""" 
                                UPDATE BossBooking 
                                SET lap=:lap,comp_name=:comp_name WHERE id=:id """,
                                  {'lap': bb.lap, 'comp_name': bb.comp_name, 'id': bb.boss_booking_id})
            await conn.commit()

            await cur.execute("SELECT * FROM BossBooking WHERE id=:id", {'id': bb.boss_booking_id})
            updated_result = await cur.fetchone()

        return BossBooking(updated_result[0], updated_result[1], updated_result[4], updated_result[5],
                           updated_result[6], overflow=updated_result[2], ovf_time=updated_result[3])

    async def delete_bookings_by_boss_id(self, boss_id: int):
        """ deletes all bookings by boss id """
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                            DELETE FROM BossBooking WHERE boss_id=:boss_id""",
                              {'boss_id': boss_id})
            await conn.commit()
