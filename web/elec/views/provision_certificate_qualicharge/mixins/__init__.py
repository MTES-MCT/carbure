
from .bulk_create import BulkCreateMixin
from .bulk_update import BulkUpdateMixin

class ActionMixin(
    BulkCreateMixin,
    BulkUpdateMixin
):
    pass
    