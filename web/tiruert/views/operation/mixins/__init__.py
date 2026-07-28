from .accept import AcceptActionMixin
from .balance import BalanceActionMixin
from .correct import CorrectActionMixin
from .excel_export import ExcelExportActionMixin
from .filter import FilterActionMixin
from .operation_detail_excel_export import OperationDetailExcelExportActionMixin
from .reject import RejectActionMixin
from .simulate import SimulateActionMixin


class ActionMixin(
    AcceptActionMixin,
    RejectActionMixin,
    BalanceActionMixin,
    SimulateActionMixin,
    FilterActionMixin,
    CorrectActionMixin,
    ExcelExportActionMixin,
    OperationDetailExcelExportActionMixin,
):
    pass
