import sqlite3
from exceptions.exceptions import ParameterIsNullError, ObjectExistsInDBError, TableEntryDoesntExistsError
from db_model.table_classes import Clan, Player


class Service:
    def __init__(self, db_name: str):
        self.db = f'{db_name}.db'

    def create_clan(self, clan_name: str) -> Clan:
        """ Insert a new Clan into the Clan table. """
        if not clan_name:
            raise ParameterIsNullError("Clan name cant be empty")

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        cur.execute(""" SELECT id, name FROM Clan WHERE name=:name """, {'name': clan_name})
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

        cur.execute(""" SELECT id, name FROM Clan WHERE id=:id """, {'id': clan_id})
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

        cur.execute(""" SELECT id, name FROM Clan WHERE name=:name """, {'name': clan_name})
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
        cur.execute(""" SELECT id, name FROM Clan """)
        results = cur.fetchall()

        conn.close()
        return [Clan(result[0], result[1]) for result in results]

    def get_clans_paginate(self, limit: int, offset: int) -> list:
        """ Paginate clan table """
        if not limit:
            raise ValueError(f'Parameter limit must be higher then 0')
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute(""" SELECT id, name FROM Clan LIMIT :limit OFFSET :offset""", {'limit': limit, 'offset': offset})
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
            cur.execute(""" SELECT id, name FROM Clan WHERE name=:name """, {'name': clan.name})
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

        cur.execute(""" SELECT id, name, discord_id  FROM ClanPlayer WHERE name=:name """, {'name': player_name})
        result = cur.fetchone()

        if result:
            raise ObjectExistsInDBError(result)

        cur.execute(""" INSERT INTO Player(name,discord_id) VALUES (:name,:discord_id) """, {'name': player_name, 'discord_id': dis_id})
        player_id = cur.lastrowid
        if clan_id:
            cur.execute(""" INSERT INTO ClanPlayer(clan_id,player_id) VALUES (player_id,clan_id) """)

        player = Player(player_id, player_name, dis_id)

        conn.commit()
        conn.close()

        return player
