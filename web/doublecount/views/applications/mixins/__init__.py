from .files import ApplicationFilesMixin
from .add_application import AddActionMixin
from .approve_application import ApproveActionMixin
from .check_file import CheckFileActionMixin
from .export import ExportActionMixin
from .generate_decision import GenerateDecisionActionMixin
from .lists import ListActionMixin
from .reject_application import RejectActionMixin
from .update_quotas import UpdateQuotaActionMixin
from .filter import FilterActionMixin
from .download_all_documents import DownloadAllDocumentsMixin


class ActionMixin(
    ApplicationFilesMixin,
    AddActionMixin,
    ApproveActionMixin,
    CheckFileActionMixin,
    ExportActionMixin,
    GenerateDecisionActionMixin,
    ListActionMixin,
    RejectActionMixin,
    UpdateQuotaActionMixin,
    FilterActionMixin,
    DownloadAllDocumentsMixin,
):
    pass
