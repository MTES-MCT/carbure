from core.filters import FiltersActionFactory
from .assign import AssignActionMixin
from .export import ExportActionMixin
from .grouped_assign import GroupAssignActionMixin


class ActionMixin(
    AssignActionMixin,
    ExportActionMixin,
    GroupAssignActionMixin,
    FiltersActionFactory(),
):
    pass
