
class Clan:
    def __init__(self, clan_id, guild_id, name):
        self.clan_id = clan_id
        self.guild_id = guild_id
        self.name = name

    def __str__(self):
        return (f"clan_id: {self.clan_id}\n"
                f"guild_id: {self.guild_id}\n"
                f"name: {self.name}\n")

    def __eq__(self, other):
        return self.clan_id == other.clan_id

    def __ne__(self, other):
        return self.clan_id != other.clan_id

    def __lt__(self, other):
        return self.clan_id < other.clan_id

    def __le__(self, other):
        return self.clan_id <= other.clan_id

    def __gt__(self, other):
        return self.clan_id > other.clan_id

    def __ge__(self, other):
        return self.clan_id >= other.clan_id


class Guild:
    def __init__(self, guild_id):
        self.guild_id = guild_id

    def __str__(self):
        return (f"guild_id: {self.guild_id}\n")


class GuildRole:
    def __init__(self, guild_id, role_id):
        self.guild_id = guild_id
        self.role_id = role_id

    def __str__(self):
        return (f"guild_id: {self.guild_id}\n"
                f"role_id: {self.role_id}\n")


class Player:
    def __init__(self, player_id, name, discord_id,):
        self.player_id = player_id
        self.name = name
        self.discord_id = discord_id

    def __str__(self):
        return (f"player_id: {self.player_id}\n"
                f"name: {self.name}\n"
                f"discord_id: {self.discord_id}\n")


class ClanPlayer:
    def __init__(self, clan_id, player_id):
        self.clan_id = clan_id
        self.player_id = player_id

    def __str__(self):
        return (f"Clan ID: {self.clan_id}\n"
                f"Player ID: {self.player_id}\n")


class ClanRole:
    def __init__(self, role_id, role, clan_id,):
        self.role_id = role_id
        self.role = role
        self.clan_id = clan_id

    def __str__(self):
        return (f"role_id: {self.role_id}\n"
                f"role: {self.role}\n"
                f"clan_id: {self.clan_id}\n")


class ClanBattle:
    def __init__(self, cb_id, name, clan_id, start_date, end_date, active, lap=1, tier=1):
        self.cb_id = cb_id
        self.name = name
        self.lap = lap
        self.tier = tier
        self.start_date = start_date
        self.end_date = end_date
        self.active = active
        self.clan_id = clan_id

    def __str__(self):
        return (f"cb_id: {self.cb_id}\n"
                f"name: {self.name}\n"
                f"lap: {self.lap}\n"
                f"tier: {self.tier}\n"
                f"start_date: {self.start_date}\n"
                f"end_date: {self.end_date}\n"
                f"active: {self.active}\n"
                f"clan_id: {self.clan_id}\n")


class PlayerCBDayInfo:
    def __init__(self, pcbdi_id, cb_day, player_id, cb_id, overflow=False, ovf_time='', ovf_comp='', hits=3,
                 reset=True):
        self.pcbdi_id = pcbdi_id
        self.overflow = overflow
        self.ovf_time = ovf_time
        self.ovf_comp = ovf_comp
        self.hits = hits
        self.reset = reset
        self.cb_day = cb_day
        self.player_id = player_id
        self.cb_id = cb_id

    def __str__(self):
        return (f"pcbdi_id: {self.pcbdi_id}\n"
                f"overflow: {self.overflow}\n"
                f"ovf_time: {self.ovf_time}\n"
                f"hits: {self.hits}\n"
                f"reset: {self.reset}\n"
                f"cb_day: {self.cb_day}\n"
                f"player_id: {self.player_id}\n"
                f"cb_id: {self.cb_id}\n")


class TeamComposition:
    def __init__(self, tc_id, name, used, pcdi_id):
        self.tc_id = tc_id
        self.name = name
        self.used = used
        self.pcdi_id = pcdi_id

    def __str__(self):
        return(f'tc_id: {self.tc_id}\n'
               f'name: {self.name}\n'
               f'used: {self.used}\n'
               f'pcdi_id: {self.pcdi_id}\n')


class Boss:
    def __init__(self, boss_id, name, boss_number, ranking, active, cb_id):
        self.boss_id = boss_id
        self.name = name
        self.boss_number = boss_number
        self.ranking = ranking
        self.active = active
        self.cb_id = cb_id

    def __str__(self):
        return (f"boss_id: {self.boss_id}\n"
                f"name: {self.name}\n"
                f"boss_number: {self.boss_number}\n"
                f"ranking: {self.ranking}\n"
                f"active: {self.active}\n"
                f"cb_id: {self.cb_id}\n")


class BossBooking:
    def __init__(self, boss_booking_id, lap, comp_name, boss_id, player_id, overflow=False, ovf_time=''):
        self.boss_booking_id = boss_booking_id
        self.lap = lap
        self.overflow = overflow
        self.ovf_time = ovf_time
        self.comp_name = comp_name
        self.boss_id = boss_id
        self.player_id = player_id

    def __str__(self):
        return (
            f"boss_booking_id: {self.boss_booking_id}\n"
            f"lap: {self.lap}\n"
            f"overflow: {self.overflow}\n"
            f"ovf_time: {self.ovf_time}\n"
            f"comp_name: {self.comp_name}\n"
            f"boss_id: {self.boss_id}\n"
            f"player_id: {self.player_id}\n"
        )