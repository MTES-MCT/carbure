from .filter import FilterActionMixin
from .accept import AcceptActionMixin
from .reject import RejectActionMixin

class ActionMixin(
    FilterActionMixin,
    AcceptActionMixin,
    RejectActionMixin
):
    pass