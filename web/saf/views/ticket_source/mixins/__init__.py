from .assign import AssignActionMixin
from .credit import CreditActionMixin
from .export import ExportActionMixin
from .filter import FilterActionMixin
from .grouped_assign import GroupAssignActionMixin


class ActionMixin(
    AssignActionMixin,
    CreditActionMixin,
    ExportActionMixin,
    FilterActionMixin,
    GroupAssignActionMixin,
):
    pass
