from .filter import FilterActionMixin
from .accept import AcceptActionMixin
from .reject import RejectActionMixin
from .balance import BalanceActionMixin

class ActionMixin(
    FilterActionMixin,
    AcceptActionMixin,
    RejectActionMixin,
    BalanceActionMixin
):
    pass