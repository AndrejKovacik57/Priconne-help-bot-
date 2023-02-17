import aiosqlite
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached, ClanBattleCantHaveMoreThenFiveDays, ObjectDoesntExistsInDBError, \
    PlayerAlreadyInClanError, PlayerNotInClanError
from db_model.table_classes import Clan, Player, ClanPlayer, ClanBattle, PlayerCBDayInfo, TeamComposition, Boss, \
    BossBooking, \
    ClanRole


class Service:
    def __init__(self, db_name: str):
        self.db = f'{db_name}.db'

    async def create_clan(self, clan_name: str, guild: int) -> Clan:
        """ Insert a new Clan into the Clan table. """
        if not clan_name:
            raise ParameterIsNullError("Clan name cant be empty")
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Clan WHERE name=:name and guild=:guild""",
                              {'name': clan_name, 'guild': guild})
            result = await cur.fetchone()

            if result:
                raise ObjectExistsInDBError(result)

            await cur.execute(""" INSERT INTO Clan(name, guild) VALUES (:name,:guild) """,
                              {'name': clan_name, 'guild': guild})
            clan = Clan(cur.lastrowid, guild, clan_name)

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
            raise ParameterIsNullError("Clan name cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Clan WHERE name=:name """, {'name': clan_name})
            result = await cur.fetchone()

        if not result:
            return None

        return Clan(result[0], result[1], result[2])

    async def get_clan_by_guild(self, guild: int) -> Clan or None:
        """ Gets Clan by guil """
        if not guild:
            raise ParameterIsNullError("Guild cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Clan WHERE guild=:guild """, {'guild': guild})
            result = await cur.fetchone()

        if not result:
            return None

        return Clan(result[0], result[1], result[2])

    async def get_clans(self) -> list:
        """ Gets all clans """
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" SELECT * FROM Clan """)
            results = await cur.fetchall()

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
            raise TableEntryDoesntExistsError(f'clan id {clan.clan_id}')

        if not (clan.name and clan.guild):
            raise ParameterIsNullError("Clan name cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if clan_to_be_updated.name != clan.name:
                await cur.execute(""" SELECT * FROM Clan WHERE name=:name """, {'name': clan.name})
                result = await cur.fetchone()

                if result:
                    raise ObjectExistsInDBError(result)

            await cur.execute(""" UPDATE Clan SET name=:name, guild=:guild WHERE id=:id """,
                              {'name': clan.name, 'id': clan.clan_id, 'guild': clan.guild})
            await conn.commit()
            await cur.execute("SELECT * FROM Clan WHERE id=:id", {'id': clan.clan_id})
            updated_result = await cur.fetchone()
        return Clan(updated_result[0], updated_result[1], updated_result[2])

    def delete_clan(self):
        # TODO: if implemented i need to create delete function of others tables and delete those before Clan table
        pass

    async def create_clan_role(self, role_name: str, clan_id: int) -> ClanRole:
        """ Insert a new Clan role into the Clan role table. """
        if not role_name:
            raise ParameterIsNullError("Role name cant be empty")

        clan = await self.get_clan_by_id(clan_id)

        if not clan:
            raise ObjectDoesntExistsInDBError(f'Clan with id {clan_id} doesnt exist')

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM ClanRole WHERE  clan_role=:clan_role AND clan_id=:clan_id""",
                              {'clan_role': role_name, 'clan_id': clan_id})
            result = await cur.fetchone()
            if result:
                raise ObjectExistsInDBError(result)

            await cur.execute(""" INSERT INTO ClanRole(clan_role, clan_id) VALUES (:clan_role,:clan_id) """,
                              {'clan_role': role_name, 'clan_id': clan_id})

            clan_role = ClanRole(cur.lastrowid, role_name, clan_id)

            await conn.commit()
        return clan_role

    async def get_clan_role_by_id(self, clan_role_id: int) -> ClanRole or None:
        """ Gets Clan role by Id """
        if not clan_role_id:
            raise ParameterIsNullError("Clan role id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM ClanRole WHERE id=:id """, {'id': clan_role_id})
            result = await cur.fetchone()

        if not result:
            return None

        return ClanRole(result[0], result[1], result[2])

    async def get_clan_role_by_name_and_clan_id(self, clan_role_name: str, clan_id: int) -> ClanRole or None:
        """ Gets Clan role by name """
        if not clan_role_name:
            raise ParameterIsNullError("Clan role name cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM ClanRole WHERE clan_role=:name AND clan_id=:clan_id""",
                              {'name': clan_role_name, 'clan_id': clan_id})
            result = await cur.fetchone()

        if not result:
            return None

        return ClanRole(result[0], result[1], result[2])

    async def get_clan_roles_by_clan_id(self, clan_id: int) -> list:
        """ Gets all clan roles in clan """
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" SELECT * FROM ClanRole WHERE clan_id=:clan_id""", {'clan_id': clan_id})
            results = await cur.fetchall()

        return [ClanRole(result[0], result[1], result[2]) for result in results]

    async def create_player(self, player_name: str, dis_id: int, clan_id=0, clan_role_id=0) -> Player:
        """ Insert a new Player into the Player table. Can add player to clan and give role to player"""
        if not (player_name and dis_id):
            raise ParameterIsNullError("Clan name, discord_id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" 
                        SELECT *
                        FROM Player 
                        WHERE discord_id=:discord_id"""
                              , {'discord_id': dis_id}
                              )
            result = await cur.fetchone()

            if result:
                raise ObjectExistsInDBError(result)

            await cur.execute(""" 
                        INSERT INTO Player(name,discord_id) VALUES (:name,:discord_id) """
                              , {'name': player_name, 'discord_id': dis_id}
                              )
            player_id = cur.lastrowid
            if clan_id:
                if clan_role_id:
                    await cur.execute(""" INSERT INTO ClanPlayer(clan_id, player_id, clan_role_id) 
                                    VALUES (:clan_id,:player_id,:clan_role_id) """
                                      , {'clan_id': clan_id, 'player_id': player_id, 'clan_role_id': clan_role_id})
                else:
                    await cur.execute(
                        f""" INSERT INTO ClanPlayer(clan_id,player_id) VALUES ({clan_id}, {player_id}) """)
            await conn.commit()

        return Player(player_id, player_name, dis_id)

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

    async def get_player_by_name(self, player_name: str) -> Player or None:
        """ Gets Player by Name """
        if not player_name:
            raise ParameterIsNullError("Player name cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Player WHERE name=:name """, {'name': player_name})
            result = await cur.fetchone()

        if not result:
            return None

        return Player(result[0], result[1], result[2])

    async def get_player_by_discord_id(self, discord_id: int) -> Player or None:
        """ Gets Player by discord name and id """
        if not discord_id:
            raise ParameterIsNullError("Discord id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" 
                        SELECT * FROM Player WHERE discord_id=:discord_id """,
                              {'discord_id': discord_id}
                              )
            result = await cur.fetchone()

            if not result:
                raise ObjectDoesntExistsInDBError('This player doesn\'t exist')

        return Player(result[0], result[1], result[2])

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

    async def update_player(self, player: Player) -> Player:
        """ Update entry in player table """

        player_to_be_updated = await self.get_player_by_id(player.player_id)
        if not player_to_be_updated:
            raise TableEntryDoesntExistsError(f'player id {player.player_id}')

        if not (player.name and player.discord_id):
            raise ParameterIsNullError("Player name and discord_id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if player_to_be_updated.discord_id != player.discord_id:
                await cur.execute("""
                            SELECT * FROM Player WHERE discord_id=:discord_id"""
                                  , {"discord_id": player.discord_id})
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

    async def add_player_to_clan(self, clan_id: int, player_id: int, clan_role_id=0) -> tuple:
        """ Add player to clan wih or without role"""
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Clan WHERE id=:id """, {'id': clan_id})
            clan_result = await cur.fetchone()

            if not clan_result:
                raise ObjectDoesntExistsInDBError

            clan = Clan(clan_result[0], clan_result[1])
            await cur.execute(""" SELECT * FROM Player WHERE id=:id """, {'id': player_id})
            player_result = cur.fetchone()

            if not player_result:
                raise ObjectDoesntExistsInDBError

            player = Player(player_result[0], player_result[1], player_result[2])
            await cur.execute(""" SELECT * FROM ClanPlayer WHERE player_id=:player_id AND clan_id=:clan_id """,
                              {'player_id': player_id, 'clan_id': clan_id})
            clan_player_result = await cur.fetchone()

            if clan_player_result:
                raise PlayerAlreadyInClanError('Player is in the clan')

            if clan_role_id:
                await cur.execute(""" INSERT INTO ClanPlayer(clan_id, player_id, clan_role_id) 
                                VALUES (:clan_id,:player_id,:clan_role_id) """
                                  , {'clan_id': clan_id, 'player_id': player_id, 'clan_role_id': clan_role_id})
            else:
                await cur.execute(""" INSERT INTO ClanPlayer(clan_id, player_id) VALUES (:clan_id,:player_id) """
                                  , {'clan_id': clan_id, 'player_id': player_id})

            await conn.commit()
        clan_role = await self.get_clan_role_by_id(clan_role_id)
        return clan, player, clan_role

    async def remove_player_from_clan(self, clan_id: int, player_id: int) -> list:
        """ Remove player from clan """

        clan = await self.get_clan_by_id(clan_id)

        if not clan:
            raise ObjectDoesntExistsInDBError('This clan doesnt exist')

        player = self.get_player_by_id(player_id)

        if not player:
            raise ObjectDoesntExistsInDBError('This player doesnt exist')

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" SELECT * FROM ClanPlayer WHERE player_id=:player_id AND clan_id=:clan_id """,
                              {'player_id': player_id, 'clan_id': clan_id})
            clan_player_result = await cur.fetchone()

            if not clan_player_result:
                raise PlayerNotInClanError('Player is not in the clan')

            await cur.execute(""" DELETE FROM ClanPlayer WHERE clan_id=:clan_id AND player_id=:player_id """, {
                {'clan_id': clan_id, 'player_id': player_id}
            })
            await conn.commit()
        return await self.get_players_from_clan(clan_id)

    async def get_clan_player(self, player_id: int) -> ClanPlayer:
        """ get clanplayer """
        player = await self.get_player_by_id(player_id)

        if not player:
            raise ObjectDoesntExistsInDBError('This player doesn\'t exist')

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(""" SELECT * FROM ClanPlayer WHERE player_id=:player_id """,
                              {'player_id': player_id})
            result = await cur.fetchone()

            if not result:
                raise PlayerNotInClanError('Player is not in a clan')

            await conn.commit()
        return ClanPlayer(result[0], result[1], result[2])

    async def create_clan_battle(self, clan_id: int, cb_name: str) -> ClanBattle:
        """ Insert a new cb into the CB table. """
        if not (cb_name and clan_id):
            raise ParameterIsNullError("Cb name and clan id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM ClanBattle WHERE name=:name AND clan_id=:clan_id""",
                              {'name': cb_name, 'clan_id': clan_id})
            result = await cur.fetchone()

            if result:
                raise ObjectExistsInDBError(result)

            await cur.execute(""" INSERT INTO ClanBattle(name, lap, tier, clan_id) 
                                VALUES (:name,:lap,:tier,:clan_id) """,
                              {'name': cb_name, 'lap': 1, 'tier': 1, 'clan_id': clan_id})

            cb = ClanBattle(cur.lastrowid, cb_name, clan_id)

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

        return ClanBattle(result[0], result[1], result[4], lap=result[2], tier=result[3])

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

        return ClanBattle(result[0], result[1], result[4], lap=result[2], tier=result[3])

    async def get_clan_battles_in_clan(self, clan_id: int) -> list:
        """ Gets all cbs from clan"""
        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            await cur.execute(f"""SELECT * FROM ClanBattle WHERE clan_id=:clan_id""", {'clan_id': clan_id})
            results = await cur.fetchall()

        return [ClanBattle(result[0], result[1], result[4], lap=result[2], tier=result[3]) for result in results]

    async def update_clan_batte(self, clan_battle: ClanBattle) -> ClanBattle:
        """ Update entry in clanbattle table """
        clan_battle_to_be_updated = await self.get_clan_battle_by_id(clan_battle.cb_id)

        if not clan_battle_to_be_updated:
            raise TableEntryDoesntExistsError(f'cb id {clan_battle_to_be_updated.clan_id}')

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

            await cur.execute(""" UPDATE ClanBattle SET name=:name,lap=:lap,tier=:tier WHERE id=:id """
                              , {'name': clan_battle.name, 'lap': clan_battle.lap, "tier": clan_battle.tier,
                                 "id": clan_battle.cb_id})
            await conn.commit()
            await cur.execute("SELECT * FROM ClanBattle WHERE id=:id", {'id': clan_battle.cb_id})
            updated_result = await cur.fetchone()
        return ClanBattle(updated_result[0], updated_result[1], updated_result[4],
                          lap=updated_result[2], tier=updated_result[3])

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

        return PlayerCBDayInfo(result[0], result[5], result[6], result[7], overflow=result[1], ovf_time=result[2],
                               hits=result[3], reset=result[4])

    async def get_all_pcdi_by_player_id(self, player_id: int, day=0) -> list:
        """ Gets pcdi by player id and day (optional) """
        if not player_id:
            raise ParameterIsNullError("Player id cant be empty")

        if day > 5:
            raise ClanBattleCantHaveMoreThenFiveDays(f"Day {day}")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if day:
                await cur.execute("""
                            SELECT * FROM PlayerCBDayInfo WHERE player_id=:player_id AND cb_day=:cb_day""",
                                  {'player_id': player_id, 'cb_day': day})
            else:
                await cur.execute(""" 
                            SELECT * FROM PlayerCBDayInfo WHERE player_id=:player_id""",
                                  {'player_id': player_id, 'cb_day': day})
            results = await cur.fetchall()

        return [PlayerCBDayInfo(
            result[0], result[5], result[6], result[7], overflow=result[1], ovf_time=result[2],
            hits=result[3], reset=result[4]) for result in results]

    async def get_all_pcdi_by_cb_id(self, cb_id: int, day=0) -> list:
        """ Gets pcdi by cb id and day (optional) """
        if not cb_id:
            raise ParameterIsNullError("Cb id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if day:
                await cur.execute("""
                            SELECT * FROM PlayerCBDayInfo WHERE cb_id=:cb_id AND cb_day=:cb_day""",
                                  {'cb_id': cb_id, 'cb_day': day})
            else:
                await cur.execute(""" 
                            SELECT * FROM PlayerCBDayInfo WHERE cb_id=:cb_id""",
                                  {'cb_id': cb_id, 'cb_day': day})
            results = await cur.fetchall()

        return [PlayerCBDayInfo(
            result[0], result[5], result[6], result[7], overflow=result[1], ovf_time=result[2],
            hits=result[3], reset=result[4]) for result in results]

    async def update_pcdi(self, pcdi: PlayerCBDayInfo) -> PlayerCBDayInfo:
        """ Update pcdi table """
        pcdi_to_be_updated = await self.get_pcdi_by_id(pcdi.pcbdi_id)

        if not pcdi_to_be_updated:
            raise TableEntryDoesntExistsError(f'pcdi id {pcdi.pcbdi_id}')

        if not (pcdi_to_be_updated.hits and pcdi_to_be_updated.cb_day):
            raise ParameterIsNullError("Pcdi hits, reset and cb_day cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" UPDATE PlayerCBDayInfo SET overflow=:overflow,ovf_time=:ovf_time,hits=:hits,reset=:reset,
                            cb_day=:cb_day WHERE id=:id """,
                              {'overflow': pcdi.overflow, 'ovf_time': pcdi.ovf_time, 'hits': pcdi.hits,
                               'reset': pcdi.reset,
                               'cb_day': pcdi.cb_day, 'id': pcdi.pcbdi_id})
            await conn.commit()
            await cur.execute("SELECT * FROM PlayerCBDayInfo WHERE id=:id", {'id': pcdi.pcbdi_id})
            updated_result = await cur.fetchone()

        return PlayerCBDayInfo(updated_result[0], updated_result[5], updated_result[6], updated_result[7],
                               overflow=updated_result[1], ovf_time=updated_result[2], hits=updated_result[3],
                               reset=updated_result[4])

    async def create_team_composition(self, name: str, pcdi_id: int) -> TeamComposition:
        """ Insert a new team the Team Composition table. """
        if not (name and pcdi_id):
            raise ParameterIsNullError("Team name and pcdi_id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" INSERT INTO TeamComposition(name, used, pcdi_id) VALUES (:name, FALSE, :pcdi_id) """,
                              {'name': name, 'pcdi_id': pcdi_id})
            tc = TeamComposition(cur.lastrowid, name, False, pcdi_id)

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
            raise TableEntryDoesntExistsError(f'Team composition id {tc.tc_id}')

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

    async def create_boss(self, name: str, boss_number: int, ranking: int, cb_id: int) -> Boss:
        """ Insert a new boss into the Boss table. """
        if not (name and boss_number and cb_id):
            raise ParameterIsNullError("Boss name, cb_id and number cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Boss WHERE name=:name and cb_id=:cb_id""",
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

    async def get_boss_by_name(self, boss_name: str, cb_id: int) -> Boss or None:
        """ Gets Boss by name  and cb"""
        if not (boss_name and cb_id):
            raise ParameterIsNullError("Boss name and cb id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM Boss WHERE name=:name AND cb_id=:cb_id""",
                              {'name': boss_name, 'cb_id': cb_id})
            result = await cur.fetchone()

        if not result:
            return None

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
            raise TableEntryDoesntExistsError(f'Boss id {boss.boss_id}')

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

    async def create_boss_booking(self, lap: int, overflow: bool, ovf_time: str, comp_name: str, exp_damage: int,
                                  boss_id: int, player_id: int) -> BossBooking:
        """ Insert boss booking into table. """
        if not (lap and comp_name and exp_damage and boss_id and player_id):
            raise ParameterIsNullError("Cb lap and comp_name exp_damage boss_id cant player_id be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if overflow and not ovf_time:
                raise ParameterIsNullError("Hit is marked as ovf but ovf_time is not set")

            elif overflow and ovf_time:
                await cur.execute(""" INSERT INTO BossBooking(lap, overflow, ovf_time, comp_name, exp_damage, boss_id, player_id) 
                                VALUES (:lap,:overflow,:ovf_time,:comp_name,:exp_damage,:boss_id,:player_id) """,
                                  {'lap': lap, 'overflow': overflow, 'ovf_time': ovf_time, 'comp_name': comp_name,
                                   'exp_damage': exp_damage, 'boss_id': boss_id, 'player_id': player_id})
                bb = BossBooking(cur.lastrowid, lap, comp_name, exp_damage, boss_id, player_id, overflow=overflow,
                                 ovf_time=ovf_time)
            else:
                await cur.execute(""" INSERT INTO BossBooking(lap, comp_name, exp_damage, boss_id, player_id) 
                                VALUES (:lap,:comp_name,:exp_damage,:boss_id,:player_id) """,
                                  {'lap': lap, 'comp_name': comp_name, 'exp_damage': exp_damage, 'boss_id': boss_id,
                                   'player_id': player_id})
                bb = BossBooking(cur.lastrowid, lap, comp_name, exp_damage, boss_id, player_id)

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

        return BossBooking(result[0], result[1], result[4], result[5], result[6], result[7], overflow=result[2],
                           ovf_time=result[3])

    async def get_boss_bookings_by_player_id(self, player_id: int) -> list:
        """ Gets boss bookings by player Id """
        if not player_id:
            raise ParameterIsNullError("Player id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM BossBooking WHERE player_id=:player_id """, {'player_id': player_id})
            results = await cur.fetchall()

        return [BossBooking(result[0], result[1], result[4], result[5], result[6], result[7], overflow=result[2],
                            ovf_time=result[3]) for result in results]

    async def get_boss_bookings_by_boss_id(self, boss_id: int) -> list:
        """ Gets boss bookings by player Id """
        if not boss_id:
            raise ParameterIsNullError("Boss id cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()

            await cur.execute(""" SELECT * FROM BossBooking WHERE boss_id=:boss_id """, {'boss_id': boss_id})
            results = await cur.fetchall()

        return [BossBooking(result[0], result[1], result[4], result[5], result[6], result[7], overflow=result[2],
                            ovf_time=result[3]) for result in results]

    async def get_all_boss_bookings_relevant(self, cur_boss: int, cur_lap: int, cb_id: int) -> list:
        """ Gets all boss bookings that are relevant """
        if not (cb_id and cur_lap and cur_boss):
            raise ParameterIsNullError("Boss id and current lap and current boss cant be empty")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            # retrieve bookings for current lap ignoring downed bosses
            await cur.execute(f"""
                            SELECT bb.*
                            FROM BossBooking bb
                            JOIN Boss b ON b.id = bb.boss_id
                            WHERE b.boss_number>={cur_boss} AND b.cb_id={cb_id} AND bb.lap={cur_lap}""")
            results = await cur.fetchall()
            # retrieve bookings for laps after current one
            await cur.execute(f"""
                            SELECT bb.*
                            FROM BossBooking bb
                            JOIN Boss b ON b.id = bb.boss_id
                            WHERE b.cb_id={cb_id} AND bb.lap>={cur_lap + 1}""")
            results += await cur.fetchall()

        return [BossBooking(result[0], result[1], result[4], result[5], result[6], result[7], overflow=result[2],
                            ovf_time=result[3]) for result in results]

    async def update_boss_booking(self, bb: BossBooking) -> BossBooking:
        """ Update boss booking"""
        bb_to_be_updated = await self.get_boss_booking_by_id(bb.boss_booking_id)
        if not bb_to_be_updated:
            raise TableEntryDoesntExistsError(f'Boss booking id {bb.boss_booking_id}')

        if not (bb.lap and bb.comp_name and bb.exp_damage):
            raise ParameterIsNullError("Boss booking lap, comp_name, exp_damage cant be empty")

        if bb.overflow and not bb.ovf_time:
            raise ParameterIsNullError("Hit is marked as ovf but ovf_time is not set")

        async with aiosqlite.connect(self.db) as conn:
            cur = await conn.cursor()
            if bb.overflow and bb.ovf_time:
                await cur.execute(""" 
                               UPDATE BossBooking 
                               SET lap=:lap,overflow=:overflow,ovf_time=:ovf_time,comp_name=:comp_name,exp_damage=:exp_damage
                               WHERE id=:id """,
                            {'lap': bb.lap, 'overflow': bb.overflow, 'ovf_time': bb.ovf_time, 'comp_name': bb.comp_name,
                             'exp_damage': bb.exp_damage, 'id': bb.boss_booking_id})
            else:
                await cur.execute(""" 
                                UPDATE BossBooking 
                                SET lap=:lap,comp_name=:comp_name,exp_damage=:exp_damage WHERE id=:id """,
                            {'lap': bb.lap, 'comp_name': bb.comp_name, 'exp_damage': bb.exp_damage,
                             'id': bb.boss_booking_id})
            await conn.commit()

            await cur.execute("SELECT * FROM BossBooking WHERE id=:id", {'id': bb.boss_booking_id})
            updated_result = await cur.fetchone()

        return BossBooking(updated_result[0], updated_result[1], updated_result[4], updated_result[5],
                           updated_result[6], updated_result[7], overflow=updated_result[2], ovf_time=updated_result[3])
