from .accept import AcceptActionMixin
from .reject import RejectActionMixin
from .filters import FiltersActionMixin


class ActionMixin(
    FiltersActionMixin,
    AcceptActionMixin,
    RejectActionMixin
):
    pass
