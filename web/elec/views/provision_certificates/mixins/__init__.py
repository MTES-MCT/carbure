from .import_certificates import ImportActionMixin
from .balance import BalanceActionMixin
from core.filters import FiltersActionMixin
from .transfer import TransferActionMixin
from .excel_export import ExcelExportActionMixin

class ActionMixin(
    BalanceActionMixin,
    FiltersActionMixin,
    TransferActionMixin,
    ImportActionMixin,
    ExcelExportActionMixin

):
    pass
