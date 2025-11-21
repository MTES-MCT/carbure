from core.filters import FiltersActionFactory
from .accept import AcceptActionMixin
from .cancel import CancelActionMixin
from .credit_source import CreditActionMixin
from .export import ExportActionMixin
from .reject import RejectActionMixin


class ActionMixin(
    AcceptActionMixin,
    CancelActionMixin,
    CreditActionMixin,
    ExportActionMixin,
    RejectActionMixin,
    FiltersActionFactory(),
):
    pass
