from .balance import BalanceActionMixin
from .filters import FiltersActionMixin
from .transfer import TransferActionMixin

class ActionMixin(
    BalanceActionMixin,
    FiltersActionMixin,
    TransferActionMixin
):
    pass
