from .add import AddCertificateActionMixin
from .check import CheckCertificateActionMixin
from .delete import DeleteCertificateActionMixin
from .reject import RejectCertificateActionMixin
from .set_default import SetDefaultCertificateActionMixin
from .update import UpdateCertificateActionMixin


class ActionMixin(
    AddCertificateActionMixin,
    CheckCertificateActionMixin,
    DeleteCertificateActionMixin,
    RejectCertificateActionMixin,
    SetDefaultCertificateActionMixin,
    UpdateCertificateActionMixin,
):
    pass
