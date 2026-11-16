from .accept import AcceptActionMixin
from .balance import BalanceActionMixin
from .debts import DebtActionMixin
from .excel_export import ExcelExportActionMixin
from .excel_import import ExcelImportActionMixin
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
    ExcelExportActionMixin,
    OperationDetailExcelExportActionMixin,
    ExcelImportActionMixin,
    DebtActionMixin,
):
    pass
