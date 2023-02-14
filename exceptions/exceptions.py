
class ObjectExistsInDBError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class ParameterIsNullError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class TableEntryDoesntExistsError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached(ValueError):
    def __init__(self, message):
        super().__init__(message)


class ClanBattleCantHaveMoreThenFiveDays(ValueError):
    def __init__(self, message):
        super().__init__(message)
