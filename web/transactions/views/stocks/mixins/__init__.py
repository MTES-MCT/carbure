from .cancel_transformation import CancelTransformationMixin
from .filters import FiltesrMixin
from .flush import FlushMixin
from .split import SplitMixin
from .summary import SummaryMixin
from .template import TemplateMixin
from .transform import TransformMixin


class ActionMixins(
    CancelTransformationMixin,
    FiltesrMixin,
    FlushMixin,
    SplitMixin,
    SummaryMixin,
    TemplateMixin,
    TransformMixin,
):
    pass
