from .accept import AcceptMixin
from .add_excel import AddExcelMixin
from .add import AddMixin
from .export import ExportMixin
from .list import ListMixin
from .retrieve import RetrieveMixin
from .send import SendMixin
from .fix import FixMinxin


class ActionMixin(
    AcceptMixin,
    AddMixin,
    AddExcelMixin,
    ExportMixin,
    FixMinxin,
    ListMixin,
    RetrieveMixin,
    SendMixin,
):
    pass
