from .accept import AcceptActionMixin
from .reject import RejectActionMixin
from .balance import BalanceActionMixin
from .simulate import SimulateActionMixin
from .filter import FilterActionMixin


class ActionMixin(
    AcceptActionMixin,
    RejectActionMixin,
    BalanceActionMixin,
    SimulateActionMixin,
    FilterActionMixin,
):
    pass