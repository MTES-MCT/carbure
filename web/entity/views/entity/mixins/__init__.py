from .options import OptionActionMixin
from .stats import EntityStatsActionMixin
from .update_info import UpdateInfoActionMixin


class EntityActionMixin(
    OptionActionMixin,
    EntityStatsActionMixin,
    UpdateInfoActionMixin,
):
    pass
