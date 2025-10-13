from .accept import AcceptActionMixin
from .reject import RejectActionMixin
from .cancel import CancelActionMixin
from core.filters import FiltersActionFactory
from .excel_export import ExcelExportActionMixin


class ActionMixin(
    AcceptActionMixin,
    RejectActionMixin,
    CancelActionMixin,
    ExcelExportActionMixin,
    FiltersActionFactory()

):
    pass
