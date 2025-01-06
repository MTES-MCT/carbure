from .accept import AcceptActionMixin
from .reject import RejectActionMixin
from .balance import BalanceActionMixin
from .simulate import SimulateActionMixin


class ActionMixin(
    AcceptActionMixin,
    RejectActionMixin,
    BalanceActionMixin,
    SimulateActionMixin
):
    pass