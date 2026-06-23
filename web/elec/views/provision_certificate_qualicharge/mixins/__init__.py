
from .excel_export import ExcelExportActionMixin
from .bulk_create import BulkCreateMixin
from .bulk_update import BulkUpdateMixin
from .bulk_transfer import BulkTransferMixin
from .filter import FilterActionMixin



class ActionMixin(
    BulkCreateMixin,
    BulkUpdateMixin,
    BulkTransferMixin,
    FilterActionMixin,
    ExcelExportActionMixin,
):
    pass