
class ObjectExistsInDBError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class ObjectDoesntExistsInDBError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class PlayerAlreadyInClanError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class PlayerNotInClanError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class ThereIsAlreadyActiveCBError(ValueError):
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
