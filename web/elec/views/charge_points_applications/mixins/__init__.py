from .accept import AcceptActionMixin
from .export import ExportActionMixin
from .filter import FilterActionMixin
from .generate_sample import GenereateSampleActionMixin
from .get_sample import GetSampleActionMixin
from .reject import RejectActionMixin


class ActionMixin(
    AcceptActionMixin,
    ExportActionMixin,
    FilterActionMixin,
    GenereateSampleActionMixin,
    GetSampleActionMixin,
    RejectActionMixin,
):
    pass
