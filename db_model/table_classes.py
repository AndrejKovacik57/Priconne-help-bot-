
class Clan:
    def __init__(self, clan_id, name):
        self.clan_id = clan_id
        self.name = name

    def __str__(self):
        return (f"clan_id: {self.clan_id}\n"
                f"name: {self.name}\n")


class Player:
    def __init__(self, player_id, name, discord_id, clan_role):
        self.player_id = player_id
        self.name = name
        self.clan_role = clan_role
        self.discord_id = discord_id

    def __str__(self):
        return (f"player_id: {self.player_id}\n"
                f"name: {self.name}\n"
                f"clan_role: {self.clan_role}\n"
                f"discord_id: {self.discord_id}\n")


class ClanBattle:
    def __init__(self, cb_id, name, clan_id):
        self.cb_id = cb_id
        self.name = name
        self.lap = 1
        self.tier = 1
        self.clan_id = clan_id

    def __str__(self):
        return (f"cb_id: {self.cb_id}\n"
                f"name: {self.name}\n"
                f"lap: {self.lap}\n"
                f"tier: {self.tier}\n"
                f"clan_id: {self.clan_id}\n")


class PlayerCBDayInfo:
    def __init__(self, pcbdi_id, cb_day, player_id, cb_id, overflow=False, ovf_time='', hits=3, reset=True):
        self.pcbdi_id = pcbdi_id
        self.overflow = overflow
        self.ovf_time = ovf_time
        self.hits = hits
        self.reset = reset
        self.cb_day = cb_day
        self.player_id = player_id
        self.cb_id = cb_id

    def __str__(self):
        return (f"pcbdi_id: {self.pcbdi_id}\n"
                f"cb_day: {self.cb_day}\n"
                f"player_id: {self.player_id}\n"
                f"cb_id: {self.cb_id}\n"
                f"overflow: {self.overflow}\n"
                f"ovf_time: {self.ovf_time}\n"
                f"hits: {self.hits}\n"
                f"reset: {self.reset}\n")


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
    