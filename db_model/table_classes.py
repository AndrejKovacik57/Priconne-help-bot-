
class Clan:
    def __init__(self, clan_id, name):
        self.clan_id = clan_id
        self.name = name


class Player:
    def __init__(self, player_id, name, discord_id):
        self.player_id = player_id
        self.name = name
        self.discord_id = discord_id


class ClanBattle:
    def __init__(self, cb_id, name, clan_id, lap=1, tier=1):
        self.cb_id = cb_id
        self.name = name
        self.lap = lap
        self.tier = tier
        self.clan_id = clan_id
