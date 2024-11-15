from .add import AddMixin
from .bulk_create import BulkCreateMixin
from .delete import DeleteLotsMixin
from .delete_many import DeleteLotsManyMixin
from .list import ListMixin
from .retrieve import RetrieveMixin
from .update_many import UpdateManyMixin
from .update import UpdateMixin


class CrudActionMixin(
    AddMixin,
    BulkCreateMixin,
    DeleteLotsMixin,
    DeleteLotsManyMixin,
    ListMixin,
    RetrieveMixin,
    UpdateManyMixin,
    UpdateMixin,
):
    pass
