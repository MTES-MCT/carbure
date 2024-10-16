from .accept import AcceptActionMixin
from .cancel import CancelActionMixin
from .credit_source import CreditActionMixin
from .export import ExportActionMixin
from .filter import FilterActionMixin
from .reject import RejectActionMixin


class ActionMixin(
    AcceptActionMixin,
    CancelActionMixin,
    CreditActionMixin,
    ExportActionMixin,
    FilterActionMixin,
    RejectActionMixin,
):
    pass
