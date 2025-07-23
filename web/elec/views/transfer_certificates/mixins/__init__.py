from .accept import AcceptActionMixin
from .reject import RejectActionMixin
from .cancel import CancelActionMixin
from .filters import FiltersActionMixin
from .excel_export import ExcelExportActionMixin


class ActionMixin(
    FiltersActionMixin,
    AcceptActionMixin,
    RejectActionMixin,
    CancelActionMixin,
    ExcelExportActionMixin
):
    pass
