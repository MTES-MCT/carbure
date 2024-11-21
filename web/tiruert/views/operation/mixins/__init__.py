from .accept import AcceptActionMixin
from .reject import RejectActionMixin
from .balance import BalanceActionMixin 


class ActionMixin(
    AcceptActionMixin,
    RejectActionMixin,
    BalanceActionMixin
):
    pass