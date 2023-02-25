
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


class PlayerCBDayInfoLimitOfEntriesForPlayerAndCBReached(ValueError):
    def __init__(self, message):
        super().__init__(message)


class ClanBattleCantHaveMoreThenFiveDaysError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class DesiredBossIsDeadError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class CantBookDeadBossError(ValueError):
    def __init__(self, message):
        super().__init__(message)


class NoActiveCBError(ValueError):
    def __init__(self, message):
        super().__init__(message)
