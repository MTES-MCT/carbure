
from .bulk_create import BulkCreateMixin
from .bulk_update import BulkUpdateMixin
from .filter import FilterActionMixin

class ActionMixin(
    BulkCreateMixin,
    BulkUpdateMixin,
    FilterActionMixin,
):
    pass