class NoEligibleActionError(Exception):
    pass


class ActionNotDeletableError(Exception):
    """Raised when an action cannot be hard-deleted."""
