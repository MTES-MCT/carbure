from .cancel_transformation import CancelTransformationMixin
from .extract_lots import ExtractLotsMixin
from .filters import FiltesrMixin
from .flush import FlushMixin
from .split import SplitMixin
from .summary import SummaryMixin
from .template import TemplateMixin
from .transform import TransformMixin


class ActionMixins(
    CancelTransformationMixin,
    ExtractLotsMixin,
    FiltesrMixin,
    FlushMixin,
    SplitMixin,
    SummaryMixin,
    TemplateMixin,
    TransformMixin,
):
    pass
