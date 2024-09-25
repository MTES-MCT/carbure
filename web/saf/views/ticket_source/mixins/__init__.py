from .assign import AssignActionMixin
from .export import ExportActionMixin
from .filter import FilterActionMixin
from .grouped_assign import GroupAssignActionMixin


class ActionMixin(
    AssignActionMixin,
    ExportActionMixin,
    FilterActionMixin,
    GroupAssignActionMixin,
):
    pass
