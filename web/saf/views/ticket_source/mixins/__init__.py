from core.filters import FiltersActionFactory
from .assign import AssignActionMixin
from .export import ExportActionMixin
from .export_foreign import ExportForeignActionMixin
from .grouped_assign import GroupAssignActionMixin


class ActionMixin(
    AssignActionMixin,
    ExportActionMixin,
    ExportForeignActionMixin,
    GroupAssignActionMixin,
    FiltersActionFactory(),
):
    pass
