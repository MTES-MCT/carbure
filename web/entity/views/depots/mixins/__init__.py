from .add import AddDepotActionMixin
from .create import CreateDepotActionMixin
from .delete import DeleteDepotActionMixin


class DepotActionMixin(
    AddDepotActionMixin, CreateDepotActionMixin, DeleteDepotActionMixin
):
    pass
