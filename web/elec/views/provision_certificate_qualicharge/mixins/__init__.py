
from .bulk_create import BulkCreateMixin
from .bulk_update import BulkUpdateMixin
from .filter import FilterActionMixin
from .transfer import TransferMixin


class ActionMixin(
    BulkCreateMixin,
    BulkUpdateMixin,
    TransferMixin,
    FilterActionMixin,
):
    pass