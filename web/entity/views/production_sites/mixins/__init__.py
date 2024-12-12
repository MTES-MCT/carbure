from .add import AddProductionSiteMixin
from .delete import DeleteActionMixin
from .set_biofuels import SetBioFuelsActionMixin
from .set_certificates import SetCertificateActionMixin
from .set_feedstocks import SetFeedstocksActionMixin
from .update import UpdateProductionSiteMixin


class ActionMixin(
    AddProductionSiteMixin,
    DeleteActionMixin,
    SetBioFuelsActionMixin,
    SetCertificateActionMixin,
    SetFeedstocksActionMixin,
    UpdateProductionSiteMixin,
):
    pass
