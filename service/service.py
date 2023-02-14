import sqlite3
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError, \
    PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached
from db_model.table_classes import Clan, Player, ClanBattle, PlayerCBDayInfo, TeamComposition, Boss, BossBooking


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
            conn.close()
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

    def create_team_composition(self, name: str, pcdi_id: int) -> TeamComposition:
        """ Insert a new team the Team Composition table. """
        if not (name and pcdi_id):
            raise ParameterIsNullError("Team name and pcdi_id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" INSERT INTO TeamComposition(name, used, pcdi_id) VALUES (:name, FALSE, :pcdi_id) """,
                    {'name': name, 'pcdi_id': pcdi_id})
        tc = TeamComposition(cur.lastrowid, name, False, pcdi_id)

        conn.commit()
        conn.close()

        return tc

    def get_team_composition_by_id(self, tc_id: int) -> TeamComposition or None:
        """ Team composition by Id """
        if not tc_id:
            raise ParameterIsNullError("TC id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM TeamComposition WHERE id=:id """, {'id': tc_id})
        result = cur.fetchone()

        if not result:
            conn.close()
            return None

        conn.close()
        return TeamComposition(result[0], result[1], result[2], result[3])

    def get_team_compositions_by_pcdi(self, pcdi_id: int) -> list:
        """ Team composition by Id """
        if not pcdi_id:
            raise ParameterIsNullError("PCDI id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM TeamComposition WHERE pcdi_id=:pcdi_id """, {'pcdi_id': pcdi_id})
        results = cur.fetchall()

        conn.close()
        return [TeamComposition(result[0], result[1], result[2], result[3]) for result in results]

    def update_team_composition(self, tc: TeamComposition) -> TeamComposition:
        """ Update team compositon """
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        tc_to_be_updated = self.get_team_composition_by_id(tc.tc_id)
        if not tc_to_be_updated:
            conn.close()
            raise TableEntryDoesntExistsError(f'Team composition id {tc.tc_id}')

        if not (tc.name and tc.used):
            conn.close()
            raise ParameterIsNullError("Team composition  name, used cant be empty")

        cur.execute(""" UPDATE TeamComposition SET name=:name AND used=:used WHERE id=:id """,
                    {'name': tc.name, 'used': tc.used, 'id': tc.tc_id})
        conn.commit()
        cur.execute("SELECT * FROM TeamComposition WHERE id=:id", {'id': tc.tc_id})
        updated_result = cur.fetchone()
        conn.close()
        return TeamComposition(updated_result[0], updated_result[1], updated_result[2], updated_result[3])

    def create_boss(self, name: str, boss_number: int, cb_id: int, ranking: int) -> Boss:
        """ Insert a new boss into the Boss table. """
        if not (name and boss_number and cb_id):
            raise ParameterIsNullError("Boss name, cb_id and number cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM Boss WHERE name=:name and cb_id=:cb_id""", {'name': name, 'cb_id': cb_id})
        result = cur.fetchone()

        if result:
            conn.close()
            raise ObjectExistsInDBError(result)

        cur.execute(""" INSERT INTO Boss(name, boss_number, ranking, active, cb_id) 
                        VALUES (:name,:boss_number,:ranking,0,:cb_id) """,
                    {'name': name, 'boss_number': boss_number, 'ranking': ranking, 'cb_id': cb_id})
        boss = Boss(cur.lastrowid, name, boss_number, ranking, False, cb_id)

        conn.commit()
        conn.close()

        return boss

    def get_boss_by_id(self, boss_id: int) -> Boss or None:
        """ Gets Boss by Id """
        if not boss_id:
            raise ParameterIsNullError("Boss id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM Boss WHERE id=:id """, {'id': boss_id})
        result = cur.fetchone()

        if not result:
            conn.close()
            return None

        conn.close()
        return Boss(result[0], result[1], result[2], result[3], result[4], result[5])

    def get_boss_name(self, boss_name: str, cb_id) -> Boss or None:
        """ Gets Boss by name  and cb"""
        if not (boss_name and cb_id):
            raise ParameterIsNullError("Boss name and cb id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM Boss WHERE name=:name AND cb_id=:cb_id""", {'name': boss_name, 'cb_id': cb_id})
        result = cur.fetchone()

        if not result:
            conn.close()
            return None

        conn.close()
        return Boss(result[0], result[1], result[2], result[3], result[4], result[5])

    def get_bosses(self, cb_id) -> list:
        """ Gets all bosses """
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(""" SELECT * FROM Boss WHERE cb_id=:cb_id""", {'cb_id': cb_id})
        results = cur.fetchall()

        conn.close()
        return [Boss(result[0], result[1], result[2], result[3], result[4], result[5]) for result in results]

    def update_boss(self, boss: Boss) -> Boss:
        """ Update boss """
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        boss_to_be_updated = self.get_boss_by_id(boss.boss_id)
        if not boss_to_be_updated:
            conn.close()
            raise TableEntryDoesntExistsError(f'Boss id {boss.boss_id}')

        if not (boss.name and boss.boss_number and boss.ranking and boss.active):
            conn.close()
            raise ParameterIsNullError("Boss name, boss_number, ranking, active cant be empty")

        cur.execute(""" 
                    UPDATE Boss SET name=:name AND boss_number=:boss_number AND ranking=:ranking AND active=:active
                    WHERE id=:id """,
                    {'name': boss.name, 'boss_number': boss.boss_number, 'ranking': boss.ranking, 'active': boss.active,
                     'id': boss.boss_id})
        conn.commit()
        cur.execute("SELECT * FROM Boss WHERE id=:id", {'id': boss.boss_id})
        updated_result = cur.fetchone()
        conn.close()
        return Boss(updated_result[0], updated_result[1], updated_result[2], updated_result[3], updated_result[4],
                    updated_result[5])

    def create_boss_booking(self, lap: int, overflow: bool, ovf_time: str, comp_name: str, exp_damage: int,
                            boss_id: int, player_id: int) -> BossBooking:
        """ Insert boss booking into table. """
        if not (lap and comp_name and exp_damage and boss_id and player_id):
            raise ParameterIsNullError("Cb lap and comp_name exp_damage boss_id cant player_id be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        if overflow and not ovf_time:
            conn.close()
            raise ParameterIsNullError("Hit is marked as ovf but ovf_time is not set")

        elif overflow and ovf_time:
            cur.execute(""" INSERT INTO BossBooking(lap, overflow, ovf_time, comp_name, exp_damage, boss_id, player_id) 
                            VALUES (:lap,:overflow,:ovf_time,:comp_name,:exp_damage,:boss_id,:player_id) """,
                        {'lap': lap, 'overflow': overflow, 'ovf_time': ovf_time, 'comp_name': comp_name,
                         'exp_damage': exp_damage, 'boss_id': boss_id, 'player_id': player_id})
            bb = BossBooking(cur.lastrowid, lap, comp_name, exp_damage, boss_id, player_id, overflow=overflow,
                             ovf_time=ovf_time)
        else:
            cur.execute(""" INSERT INTO BossBooking(lap, comp_name, exp_damage, boss_id, player_id) 
                            VALUES (:lap,:comp_name,:exp_damage,:boss_id,:player_id) """,
                        {'lap': lap, 'comp_name': comp_name,'exp_damage': exp_damage, 'boss_id': boss_id,
                         'player_id': player_id})
            bb = BossBooking(cur.lastrowid, lap, comp_name, exp_damage, boss_id, player_id)

        conn.commit()
        conn.close()

        return bb

    def get_boss_booking_by_id(self, bb_id: int) -> BossBooking or None:
        """ Gets boss booking by Id """
        if not bb_id:
            raise ParameterIsNullError("Boss booking id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM BossBooking WHERE id=:id """, {'id': bb_id})
        result = cur.fetchone()

        if not result:
            conn.close()
            return None

        conn.close()
        return BossBooking(result[0], result[1], result[4], result[5], result[6], result[7], overflow=result[2],
                           ovf_time=result[3])

    def get_boss_bookings_by_player_id(self, player_id: int) -> list:
        """ Gets boss bookings by player Id """
        if not player_id:
            raise ParameterIsNullError("Player id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM BossBooking WHERE player_id=:player_id """, {'player_id': player_id})
        results = cur.fetchall()

        conn.close()
        return [BossBooking(result[0], result[1], result[4], result[5], result[6], result[7], overflow=result[2],
                            ovf_time=result[3]) for result in results]

    def get_boss_bookings_by_boss_id(self, boss_id: int) -> list:
        """ Gets boss bookings by player Id """
        if not boss_id:
            raise ParameterIsNullError("Boss id cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT * FROM BossBooking WHERE boss_id=:boss_id """, {'boss_id': boss_id})
        results = cur.fetchall()

        conn.close()
        return [BossBooking(result[0], result[1], result[4], result[5], result[6], result[7], overflow=result[2],
                            ovf_time=result[3]) for result in results]

    def get_all_boss_bookings_relevant(self, cur_boss: int, cur_lap: int, cb_id: int) -> list:
        """ Gets all boss bookings that are relevant """
        if not (cb_id and cur_lap and cur_boss):
            raise ParameterIsNullError("Boss id and current lap and current boss cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        # retrieve bookings for current lap ignoring downed bosses
        cur.execute(f"""
                        SELECT bb.*
                        FROM BossBooking bb
                        JOIN Boss b ON b.id = bb.boss_id
                        WHERE b.boss_number>={cur_boss} AND b.cb_id={cb_id} AND bb.lap={cur_lap} and """,)
        results = cur.fetchall()
        # retrieve bookings for laps after current one
        cur.execute(f"""
                        SELECT bb.*
                        FROM BossBooking bb
                        JOIN Boss b ON b.id = bb.boss_id
                        WHERE b.cb_id={cb_id} AND bb.lap>={cur_lap+1} and """,)
        results += cur.fetchall()
        conn.close()
        return [BossBooking(result[0], result[1], result[4], result[5], result[6], result[7], overflow=result[2],
                            ovf_time=result[3]) for result in results]

    def update_boss_booking(self, bb: BossBooking) -> BossBooking:
        """ Update boss booking"""
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        bb_to_be_updated = self.get_boss_booking_by_id(bb.boss_booking_id)
        if not bb_to_be_updated:
            conn.close()
            raise TableEntryDoesntExistsError(f'Boss booking id {bb.boss_booking_id}')

        if not (bb.lap and bb.comp_name and bb.exp_damage):
            conn.close()
            raise ParameterIsNullError("Boss booking lap, comp_name, exp_damage cant be empty")

        if bb.overflow and not bb.ovf_time:
            conn.close()
            raise ParameterIsNullError("Hit is marked as ovf but ovf_time is not set")
        elif bb.overflow and bb.ovf_time:
            cur.execute(""" 
                           UPDATE BossBooking 
                           SET lap=:lap AND overflow=:overflow AND ovf_time=:ovf_time AND comp_name=:comp_name 
                           AND exp_damage=:exp_damage
                           WHERE id=:id """,
                        {'lap': bb.lap, 'overflow': bb.overflow, 'ovf_time': bb.ovf_time, 'comp_name': bb.comp_name,
                         'exp_damage': bb.exp_damage, 'id': bb.boss_booking_id})
        else:
            cur.execute(""" 
                            UPDATE BossBooking 
                            SET lap=:lap AND comp_name=:comp_name AND exp_damage=:exp_damage
                            WHERE id=:id """,
                        {'lap': bb.lap, 'comp_name': bb.comp_name, 'exp_damage': bb.exp_damage,
                         'id': bb.boss_booking_id})
        conn.commit()

        cur.execute("SELECT * FROM BossBooking WHERE id=:id", {'id': bb.boss_booking_id})
        updated_result = cur.fetchone()
        conn.close()
        return BossBooking(updated_result[0], updated_result[1], updated_result[4], updated_result[5],
                           updated_result[6], updated_result[7], overflow=updated_result[2], ovf_time=updated_result[3])
