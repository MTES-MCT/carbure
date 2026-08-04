from .accept import AcceptActionMixin
from .balance import BalanceActionMixin
from .excel_export import ExcelExportActionMixin
from .filter import FilterActionMixin
from .reject import RejectActionMixin


class ActionMixin(FilterActionMixin, AcceptActionMixin, RejectActionMixin, BalanceActionMixin, ExcelExportActionMixin):
    pass
