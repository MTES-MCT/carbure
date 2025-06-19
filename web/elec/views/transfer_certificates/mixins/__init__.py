from .accept import AcceptActionMixin
from .reject import RejectActionMixin
from .cancel import CancelActionMixin
from .filters import FiltersActionMixin


class ActionMixin(
    FiltersActionMixin,
    AcceptActionMixin,
    RejectActionMixin,
    CancelActionMixin
):
    pass
