from .list import ListActionMixin
from .public_list import AgreementPublicListActionMixin
from .list_admin import AgreementAdminListActionMixin
from .export import ExportActionMixin
from .retrieve import AgreementRetrieveActionMixin
from .filter import FilterActionMixin

class ActionMixin(
    ListActionMixin,
    ExportActionMixin,
    AgreementAdminListActionMixin,
    AgreementPublicListActionMixin,
    AgreementRetrieveActionMixin,
    FilterActionMixin
):
    pass
