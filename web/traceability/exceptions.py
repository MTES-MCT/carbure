class NoEligibleActionError(Exception):
    pass


class ConversionError(Exception):
    def __init__(self, actions):
        self.actions = list(actions)
        super().__init__()


class ActionNotDeletableError(Exception):
    """Raised when an action cannot be hard-deleted."""
