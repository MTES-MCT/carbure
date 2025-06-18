from .filters import FiltersActionMixin
from .balance import BalanceActionMixin

class ActionMixin(
    FiltersActionMixin,
    BalanceActionMixin
):
    pass
