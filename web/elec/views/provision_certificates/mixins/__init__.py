from .import_certificates import ImportActionMixin
from .balance import BalanceActionMixin
from core.filters import FiltersActionFactory
from .transfer import TransferActionMixin
from .excel_export import ExcelExportActionMixin

class ActionMixin(
    BalanceActionMixin,
    TransferActionMixin,
    ImportActionMixin,
    ExcelExportActionMixin,
    FiltersActionFactory()
):
    pass
