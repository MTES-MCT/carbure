from .accept import AcceptActionMixin
from .balance import BalanceActionMixin
from .correct import CorrectActionMixin
from .excel_export import ExcelExportActionMixin
from .filter import FilterActionMixin
from .operation_detail_excel_export import OperationDetailExcelExportActionMixin
from .reject import RejectActionMixin
from .repay_debt import RepayDebtActionMixin
from .simulate import SimulateActionMixin
from .excel_import import ExcelImportActionMixin

class ActionMixin(
    AcceptActionMixin,
    RejectActionMixin,
    BalanceActionMixin,
    SimulateActionMixin,
    FilterActionMixin,
    CorrectActionMixin,
    ExcelExportActionMixin,
    OperationDetailExcelExportActionMixin,
    ExcelImportActionMixin,
    RepayDebtActionMixin,
):
    pass
