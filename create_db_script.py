import sqlite3

conn = sqlite3.connect('priconne_database.db')
cur = conn.cursor()

cur.execute("""DROP TABLE IF EXISTS Guild""")
cur.execute("""DROP TABLE IF EXISTS GuildAdmin""")
cur.execute("""DROP TABLE IF EXISTS GuildLead""")
cur.execute("""DROP TABLE IF EXISTS Clan""")
cur.execute("""DROP TABLE IF EXISTS Role""")
cur.execute("""DROP TABLE IF EXISTS Player""")
cur.execute("""DROP TABLE IF EXISTS ClanPlayer""")
cur.execute("""DROP TABLE IF EXISTS ClanBattle""")
cur.execute("""DROP TABLE IF EXISTS PlayerCBDayInfo""")
cur.execute("""DROP TABLE IF EXISTS TeamComposition""")
cur.execute("""DROP TABLE IF EXISTS CBDay""")
cur.execute("""DROP TABLE IF EXISTS Boss""")
cur.execute("""DROP TABLE IF EXISTS BossBooking""")

cur.execute("""
        CREATE TABLE Guild (
            server_id INTEGER PRIMARY KEY
        )
    """)

cur.execute("""
        CREATE TABLE GuildAdmin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            FOREIGN KEY (guild_id) REFERENCES Guild(server_id)
        )
    """)

cur.execute("""
        CREATE TABLE GuildLead (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            FOREIGN KEY (guild_id) REFERENCES Guild(server_id)
        )
    """)

cur.execute("""
        CREATE TABLE Clan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            name TEXT UNIQUE NOT NULL,
            FOREIGN KEY (guild_id) REFERENCES Guild(server_id)
        )
    """)

cur.execute("""
        CREATE TABLE Role (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild INTEGER NOT NULL,
            name TEXT UNIQUE NOT NULL
        )
    """)

cur.execute("""
        CREATE TABLE Player (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            discord_id INTEGER NULL 
        )
    """)

cur.execute("""
        CREATE TABLE ClanPlayer (
            clan_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            FOREIGN KEY (clan_id) REFERENCES Clan(id), 
            FOREIGN KEY (player_id) REFERENCES Player(id)
        )
    """)

cur.execute("""
        CREATE TABLE ClanBattle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            lap INTEGER NOT NULL,
            tier INTEGER NOT NULL,
            start_date DATETIME NOT NULL,
            end_date DATETIME NOT NULL,
            active INTEGER NOT NULL,
            clan_id INTEGER NOT NULL,
            FOREIGN KEY (clan_id) REFERENCES Clan(id)
        )
    """)
cur.execute("""
        CREATE TABLE PlayerCBDayInfo(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            overflow INTEGER NULL,
            ovf_time TEXT NULL,
            ovf_comp TEXT NULL,
            hits INTEGER NOT NULL,
            reset INTEGER NOT NULL,
            cb_day INTEGER NOT NULL,
            player_id INTEGER NULL,
            cb_id INTEGER NOT NULL,
            FOREIGN KEY (player_id) REFERENCES Player(id),
            FOREIGN KEY (cb_id) REFERENCES ClanBattle(id)
        )
    """)
cur.execute("""
        CREATE TABLE TeamComposition(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            used INTEGER NOT NULL,
            pcdi_id INTEGER NOT NULL,
            FOREIGN KEY (pcdi_id) REFERENCES PlayerCBDayInfo(id)

        )
    """)
cur.execute("""
        CREATE TABLE Boss (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            boss_number INTEGER NOT NULL,
            ranking INTEGER NOT NULL,
            active INTEGER NOT NULL,
            cb_id INTEGER NOT NULL,
            FOREIGN KEY (cb_id) REFERENCES ClanBattle(id)
        )
    """)
cur.execute("""
        CREATE TABLE BossBooking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lap INTEGER NOT NULL,
            overflow INTEGER NULL,
            ovf_time TEXT NULL,
            comp_name TEXT NOT NULL,
            boss_id INTEGER NOT NULL,
            player_id INTEGER NULL,
            FOREIGN KEY (boss_id) REFERENCES Boss(id),
            FOREIGN KEY (player_id) REFERENCES Player(id)
        )
    """)
conn.commit()
conn.close()
