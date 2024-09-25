from .accept import AcceptMixin
from .add_comment import AddCommentMixin
from .add_excel import AddExcelMixin
from .crud import AddMixin, DeleteLotsMixin, ListMixin, RetrieveMixin, UpdateMixin
from .duplicate import DuplicateMixin
from .export import ExportMixin
from .filters import FiltesrMixin
from .fix import FixMinxin
from .reject import RejectMixin
from .send import SendMixin
from .summary import SummaryMixin
from .template import TemplateMixin
from .toggle_warning import ToggleWarningMixin


class ActionMixin(
    AcceptMixin,
    AddMixin,
    AddCommentMixin,
    AddExcelMixin,
    DeleteLotsMixin,
    DuplicateMixin,
    ExportMixin,
    FiltesrMixin,
    FixMinxin,
    ListMixin,
    RejectMixin,
    RetrieveMixin,
    SendMixin,
    SummaryMixin,
    TemplateMixin,
    ToggleWarningMixin,
    UpdateMixin,
):
    pass
