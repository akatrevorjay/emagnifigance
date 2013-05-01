

class EmagError(Exception):
    pass


class TestFailureError(EmagError):
    pass


class RecipientBlockedError(EmagError):
    pass
