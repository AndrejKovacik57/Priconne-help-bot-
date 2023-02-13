import sqlite3
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached
from db_model.table_classes import Clan, Player, ClanBattle, PlayerCBDayInfo


class Service:
    def __init__(self, db_name: str):
        self.db = f'{db_name}.db'

    def create_clan(self, clan_name: str) -> Clan:
        """ Insert a new Clan into the Clan table. """
        if not clan_name:
            raise ParameterIsNullError("Clan name cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM Clan WHERE name=:name """, {'name': clan_name})
        result = cur.fetchone()

        if result:
            raise ObjectExistsInDBError(result)

        cur.execute(""" INSERT INTO Clan(name) VALUES (:name) """, {'name': clan_name})
        clan = Clan(cur.lastrowid, clan_name)

        conn.commit()
        conn.close()

        return clan

    def get_clan_by_id(self, clan_id: int) -> Clan or None:
        """ Gets Clan by Id """
        if not clan_id:
            raise ParameterIsNullError("Clan id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM Clan WHERE id=:id """, {'id': clan_id})
        result = cur.fetchone()

        if not result:
            conn.close()
            return None

        conn.close()
        return Clan(result[0], result[1])

    def get_clan_by_name(self, clan_name: str) -> Clan or None:
        """ Gets Clan by name """
        if not clan_name:
            raise ParameterIsNullError("Clan name cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM Clan WHERE name=:name """, {'name': clan_name})
        result = cur.fetchone()

        if not result:
            conn.close()
            return None

        conn.close()
        return Clan(result[0], result[1])

    def get_clans(self) -> list:
        """ Gets all clans """
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(""" SELECT * FROM Clan """)
        results = cur.fetchall()

        conn.close()
        return [Clan(result[0], result[1]) for result in results]

    def get_clans_paginate(self, limit: int, offset: int) -> list:
        """ Paginate clan table """
        if not limit:
            raise ValueError(f'Parameter limit must be higher then 0')
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(""" SELECT * FROM Clan LIMIT :limit OFFSET :offset""", {'limit': limit, 'offset': offset})
        results = cur.fetchall()

        conn.close()
        return [Clan(result[0], result[1]) for result in results]

    def update_clan(self, clan: Clan) -> Clan:
        """ Update clan table """
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        clan_to_be_updated = self.get_clan_by_id(clan.clan_id)
        if not clan_to_be_updated:
            conn.close()
            raise TableEntryDoesntExistsError(f'clan id {clan.clan_id}')

        if not clan.name:
            conn.close()
            raise ParameterIsNullError("Clan name cant be empty")

        if clan_to_be_updated.name != clan.name:
            cur.execute(""" SELECT * FROM Clan WHERE name=:name """, {'name': clan.name})
            result = cur.fetchone()

            if result:
                conn.close()
                raise ObjectExistsInDBError(result)

        cur.execute(""" UPDATE Clan SET name=:name WHERE id=:id """, {'name': clan.name, 'id': clan.clan_id})
        conn.commit()
        cur.execute("SELECT * FROM Clan WHERE id=:id", {'id': clan.clan_id})
        updated_result = cur.fetchone()
        conn.close()
        return Clan(updated_result[0], updated_result[1])

    def delete_clan(self):
        # TODO: if implemented i need to create delete function of others tables and delete those before Clan table
        pass

    def create_player(self, player_name: str, dis_id: int, clan_id=0) -> Player:
        """ Insert a new Player into the ClanPlayer table. """
        if not player_name and not dis_id:
            raise ParameterIsNullError("Clan name and discord_id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" 
                    SELECT *
                    FROM Player 
                    WHERE name=:name and discord_id=:discord_id """
                    , {'name': player_name, 'discord_id': dis_id}
                    )
        result = cur.fetchone()

        if result:
            raise ObjectExistsInDBError(result)

        cur.execute(""" 
                    INSERT INTO Player(name,discord_id) VALUES (:name,:discord_id) """
                    , {'name': player_name, 'discord_id': dis_id}
                    )
        player_id = cur.lastrowid
        if clan_id:
            cur.execute(f""" INSERT INTO ClanPlayer(clan_id,player_id) VALUES ({clan_id}, {player_id}) """)

        player = Player(player_id, player_name, dis_id)

        conn.commit()
        conn.close()

        return player

    def get_player_by_id(self, player_id: int) -> Player or None:
        """ Gets Player by Id """
        if not player_id:
            raise ParameterIsNullError("Player id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM PLayer WHERE id=:id """, {'id': player_id})
        result = cur.fetchone()

        if not result:
            conn.close()
            return None

        conn.close()
        return Player(result[0], result[1], result[2])

    def get_player_by_discord_name_and_id(self, discord_name: str, discord_id: int) -> Clan or None:
        """ Gets Player by discord name and id """
        if not discord_name or not discord_id:
            raise ParameterIsNullError("Discord name and id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" 
                    SELECT * FROM Player WHERE name=:name AND discord_id=:discord_id """,
                    {'name': discord_name, 'discord_id': discord_id}
                    )
        result = cur.fetchone()

        if not result:
            conn.close()
            return None

        conn.close()
        return Player(result[0], result[1], result[2])

    def get_players(self) -> list:
        """ Gets all players """
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(""" SELECT * FROM Player """)
        results = cur.fetchall()

        conn.close()
        return [Player(result[0], result[1], result[2]) for result in results]

    def get_players_from_clan(self, clan_id: int) -> list:
        """ Gets all players from clan"""
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(f"""
                        SELECT p.*
                        FROM ClanPlayer cp
                        JOIN Player p ON cp.player_id = p.id
                        WHERE cp.clan_id = {clan_id};""")
        results = cur.fetchall()

        conn.close()
        return [Player(result[0], result[1], result[2]) for result in results]

    def update_player(self, player: Player) -> Player:
        """ Update entry in player table """
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        player_to_be_updated = self.get_player_by_id(player.player_id)
        if not player_to_be_updated:
            conn.close()
            raise TableEntryDoesntExistsError(f'player id {player.player_id}')

        if not player.name or not player.discord_id:
            conn.close()
            raise ParameterIsNullError("Player name and discord_id cant be empty")

        if player_to_be_updated.name != player.name and player_to_be_updated.discord_id != player.discord_id:
            cur.execute("""
                        SELECT * FROM Player WHERE name=:name AND discord_id=:discord_id AND clan_role=:clan_role"""
                        , {'name': player.name, "discord_id": player.discord_id, "clan_role": player.clan_role})
            result = cur.fetchone()

            if result:
                conn.close()
                raise ObjectExistsInDBError(result)

        cur.execute(""" UPDATE Player SET name=:name AND discord_id=:discord_id WHERE id=:id """
                    , {'id': player.player_id, 'name': player.name, "discord_id": player.discord_id})
        conn.commit()
        cur.execute("SELECT * FROM Player WHERE id=:id", {'id': player.player_id})
        updated_result = cur.fetchone()
        conn.close()
        return Player(updated_result[0], updated_result[1], updated_result[2])

    def create_clan_battle(self, clan_id: int, cb_name: str) -> ClanBattle:
        """ Insert a new cb into the CB table. """
        if not cb_name or clan_id:
            raise ParameterIsNullError("Cb name and clan id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM ClanBattle WHERE name=:name """, {'name': cb_name})
        result = cur.fetchone()

        if result:
            raise ObjectExistsInDBError(result)

        cur.execute(""" INSERT INTO ClanBattle(name, lap, tier, clan_id) VALUES (:name,:lap,:tier,:clan_id) """
                    , {'name': cb_name, 'lap': 1, 'tier': 1, 'clan_id': clan_id})

        cb = ClanBattle(cur.lastrowid, cb_name, clan_id)

        conn.commit()
        conn.close()

        return cb

    def get_clan_battle_by_id(self, cb_id: int) -> ClanBattle or None:
        """ Gets cb by Id """
        if not cb_id:
            raise ParameterIsNullError("Cb id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM ClanBattle WHERE id=:id """, {'id': cb_id})
        result = cur.fetchone()

        if not result:
            conn.close()
            return None

        conn.close()
        return ClanBattle(result[0], result[1], result[2])

    def get_clan_battle_by_name_and_clan_id(self, name: str, clan_id: int) -> ClanBattle or None:
        """ Gets cb by name and clan id """
        if not clan_id or not name:
            raise ParameterIsNullError("Cb name and clan id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" 
                    SELECT * FROM ClanBattle WHERE clan_id=:clan_id AND name=:name"""
                    , {'clan_id': clan_id, 'name': name})
        result = cur.fetchone()

        if not result:
            conn.close()
            return None

        conn.close()
        return ClanBattle(result[0], result[1], result[2])

    def get_clan_battles_in_clan(self, clan_id: int) -> list:
        """ Gets all cbs from clan"""
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(f"""SELECT * FROM ClanBattle WHERE clan_id = {clan_id}""")
        results = cur.fetchall()

        conn.close()
        return [ClanBattle(result[0], result[1], result[2]) for result in results]

    def update_clan_batte(self, clan_battle: ClanBattle) -> ClanBattle:
        """ Update entry in clanbattle table """
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        clan_battle_to_be_updated = self.get_clan_battle_by_id(clan_battle.clan_id)
        if not clan_battle_to_be_updated:
            conn.close()
            raise TableEntryDoesntExistsError(f'cb id {clan_battle_to_be_updated.clan_id}')

        if not clan_battle.name or not clan_battle.lap or not clan_battle.tier:
            conn.close()
            raise ParameterIsNullError("ClanBattle name, lap, tier cant be empty")

        if clan_battle_to_be_updated.name != clan_battle.name:
            cur.execute("""
                           SELECT * FROM ClanBattle WHERE name=:name AND clan_id=:clan_id"""
                        , {'name': clan_battle.name, "clan_id": clan_battle.clan_id})
            result = cur.fetchone()

            if result:
                conn.close()
                raise ObjectExistsInDBError(result)

        cur.execute(""" UPDATE ClanBattle SET name=:name AND lap=:lap AND tier=:tier  WHERE id=:id """
                    , {'name': clan_battle.name, 'lap': clan_battle.lap, "tier": clan_battle.tier})
        conn.commit()
        cur.execute("SELECT * FROM ClanBattle WHERE id=:id", {'id': clan_battle.cb_id})
        updated_result = cur.fetchone()
        conn.close()
        return ClanBattle(updated_result[0], updated_result[1], updated_result[2])

    def create_player_cb_day_info(self, cb_id, player_id) -> PlayerCBDayInfo:
        """ Insert a new day info in to table. """
        if not cb_id or player_id:
            raise ParameterIsNullError("Cb id and player id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(f""" SELECT * FROM PlayerCBDayInfo WHERE player_id={player_id} AND cb_id={cb_id}""")
        result = cur.fetchall()
        cb_day = len(result)

        if cb_day >= 5:
            conn.close()
            raise PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached(result)

        cb_day += 1

        cur.execute(""" 
                    INSERT INTO PlayerCBDayInfo(hits, reset, cb_day, player_id, cb_id) 
                    VALUES (:hits,:reset,:cb_day,:player_id,:cb_id) """
                    , {'reset': True, 'hits': 3, 'cb_day': cb_day, 'player_id': player_id, 'cb_id': cb_id})

        pcbdi = PlayerCBDayInfo(cur.lastrowid, cb_day, cb_id, player_id)

        conn.commit()
        conn.close()

        return pcbdi

    def get_pcdi_by_id(self, pcdi_id: int) -> PlayerCBDayInfo:
        """ Gets pcdi by id"""
        if not pcdi_id:
            raise ParameterIsNullError("PCDI id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute("""SELECT * FROM PlayerCBDayInfo WHERE id=:id""", {'id': pcdi_id})
        result = cur.fetchone()
        conn.close()
        return PlayerCBDayInfo(result[0], result[5], result[6], result[7], overflow=result[1], ovf_time=result[2],
                               hits=result[3], reset=result[4])

    def get_all_pcdi_by_clan_player_id(self, player_id: int, day=0) -> list:
        """ Gets pcdi by player id and day (optional) """
        if not player_id:
            raise ParameterIsNullError("Player id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        if day:
            cur.execute("""
                        SELECT * FROM PlayerCBDayInfo WHERE player_id=:player_id AND cb_day=:cb_day""",
                        {'player_id': player_id, 'cb_day': day})
        else:
            cur.execute(""" 
                        SELECT * FROM PlayerCBDayInfo WHERE player_id=:player_id""",
                        {'player_id': player_id, 'cb_day': day})
        results = cur.fetchall()
        conn.close()
        return [PlayerCBDayInfo(
            result[0], result[5], result[6], result[7], overflow=result[1], ovf_time=result[2],
            hits=result[3], reset=result[4]) for result in results]

    def get_all_pcdi_by_cb_id(self, cb_id: int, day: int) -> list:
        """ Gets pcdi by cb id and day (optional) """
        if not cb_id:
            raise ParameterIsNullError("Cb id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        if day:
            cur.execute("""
                        SELECT * FROM PlayerCBDayInfo WHERE cb_id=:cb_id AND cb_day=:cb_day""",
                        {'cb_id': cb_id, 'cb_day': day})
        else:
            cur.execute(""" 
                        SELECT * FROM PlayerCBDayInfo WHERE cb_id=:cb_id""",
                        {'cb_id': cb_id, 'cb_day': day})
        results = cur.fetchall()
        conn.close()
        return [PlayerCBDayInfo(
            result[0], result[5], result[6], result[7], overflow=result[1], ovf_time=result[2],
            hits=result[3], reset=result[4]) for result in results]

    def update_pcdi(self, pcdi: PlayerCBDayInfo) -> PlayerCBDayInfo:
        """ Update pcdi table """
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        pcdi_to_be_updated = self.get_pcdi_by_id(pcdi.pcbdi_id)

        if not pcdi_to_be_updated:
            conn.close()
            raise TableEntryDoesntExistsError(f'pcdi id {pcdi.pcbdi_id}')

        if not (pcdi_to_be_updated.hits and pcdi_to_be_updated.reset and pcdi_to_be_updated.cb_day):
            conn.close()
            raise ParameterIsNullError("Pcdi hits, reset and cb_day cant be empty")

        cur.execute(""" UPDATE PlayerCBDayInfo SET overflow=:overflow AND ovf_time=:ovf_time AND hits=:hits 
                        AND reset=:reset AND cb_day=:cb_day WHERE id=:id """,
                    {'overflow': pcdi.overflow, 'ovf_time': pcdi.ovf_time, 'hits': pcdi.hits, 'reset': pcdi.reset,
                     'cb_day': pcdi.cb_day, 'id': pcdi.pcbdi_id})
        conn.commit()
        cur.execute("SELECT * FROM PlayerCBDayInfo WHERE id=:id", {'id': pcdi.pcbdi_id})
        updated_result = cur.fetchone()
        conn.close()
        return PlayerCBDayInfo(updated_result[0], updated_result[5], updated_result[6], updated_result[7],
                               overflow=updated_result[1], ovf_time=updated_result[2], hits=updated_result[3],
                               reset=updated_result[4])
