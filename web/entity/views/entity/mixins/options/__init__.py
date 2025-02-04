from .create import CreateEntityActionMixin
from .details import EntityDetailActionMixin
from .direct_deliveries import DirectDeliveriesActionMixin
from .electricity import ToggleElecActionMixin
from .lists import EntityListActionMixin
from .release_for_consumption import ToggleRFCActionMixin
from .stocks import ToggleStocksActionMixin
from .trading import ToggleTradingActionMixin
from .unit import UnitActionMixin


class OptionActionMixin(
    CreateEntityActionMixin,
    EntityDetailActionMixin,
    EntityListActionMixin,
    DirectDeliveriesActionMixin,
    ToggleElecActionMixin,
    ToggleRFCActionMixin,
    ToggleStocksActionMixin,
    ToggleTradingActionMixin,
    UnitActionMixin,
):
    pass
