class NoEligibleActionError(Exception):
    pass


class ConversionError(Exception):
    def __init__(self, actions):
        self.actions = list(actions)
        super().__init__()
