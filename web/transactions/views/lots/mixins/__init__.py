from .accept import AcceptMixin
from .add_comment import AddCommentMixin
from .add_excel import AddExcelMixin
from .crud import CrudActionMixin
from .delcarations import DeclarationMixin
from .duplicate import DuplicateMixin
from .export import ExportMixin
from .filters import FiltersMixin
from .fix import FixMinxin
from .map import MapMixin
from .mark import MarkMixin
from .reject import RejectMixin
from .send import SendMixin
from .summary import SummaryMixin
from .template import TemplateMixin
from .toggle import ToggleActionMixin


class ActionMixin(
    AcceptMixin,
    AddCommentMixin,
    AddExcelMixin,
    CrudActionMixin,
    DeclarationMixin,
    DuplicateMixin,
    ExportMixin,
    FiltersMixin,
    FixMinxin,
    MapMixin,
    MarkMixin,
    RejectMixin,
    SendMixin,
    SummaryMixin,
    TemplateMixin,
    ToggleActionMixin,
):
    pass
