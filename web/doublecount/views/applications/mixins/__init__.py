from .add_application import AddActionMixin
from .approve_application import ApprouveActionMixin
from .check_files import CheckAdminFilesActionMixin
from .check_file import CheckFileActionMixin
from .export import ExportActionMixin
from .export_application import ExportApplicationActionMixin
from .get_file_link import GetLinkActionMixin
from .lists import ListActionMixin
from .reject_application import RejectActionMixin
from .update_quotas import UpdateQuotaActionMixin


class ActionMixin(
    AddActionMixin,
    ApprouveActionMixin,
    CheckAdminFilesActionMixin,
    CheckFileActionMixin,
    ExportActionMixin,
    GetLinkActionMixin,
    ExportApplicationActionMixin,
    ListActionMixin,
    RejectActionMixin,
    UpdateQuotaActionMixin,
):
    pass
