from .accept import AcceptActionMixin
from .reject import RejectActionMixin


class ActionMixin(
    AcceptActionMixin,
    RejectActionMixin,
):
    pass