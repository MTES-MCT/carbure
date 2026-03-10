
from .excel_export import ExcelExportActionMixin
from .bulk_create import BulkCreateMixin
from .bulk_update import BulkUpdateMixin
from .filter import FilterActionMixin



class ActionMixin(
    BulkCreateMixin,
    BulkUpdateMixin,
    FilterActionMixin,
    ExcelExportActionMixin,
):
    pass