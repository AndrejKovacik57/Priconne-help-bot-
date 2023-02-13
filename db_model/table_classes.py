
class Clan:
    def __init__(self, clan_id, name):
        self.clan_id = clan_id
        self.name = name

    def __str__(self):
        return f'clan id: {self.clan_id} \n' \
               f'clan name: {self.name}'


class Player:
    def __init__(self, player_id, name, discord_id):
        self.player_id = player_id
        self.name = name
        self.discord_id = discord_id


class ClanBattle:
    def __init__(self, cb_id, name, clan_id):
        self.cb_id = cb_id
        self.name = name
        self.lap = 1
        self.tier = 1
        self.clan_id = clan_id


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
