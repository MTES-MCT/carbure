from .accept import AcceptActionMixin
from .reject import RejectActionMixin
from .balance import BalanceActionMixin
from .simulate import SimulateActionMixin
from .filter import FilterActionMixin
from .correct import CorrectActionMixin


class ActionMixin(
    AcceptActionMixin,
    RejectActionMixin,
    BalanceActionMixin,
    SimulateActionMixin,
    FilterActionMixin,
    CorrectActionMixin,
):
    pass