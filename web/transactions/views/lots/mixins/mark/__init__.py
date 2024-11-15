from .mark_conform import MarkConformMixin
from .mark_nonconform import MarkNonConformMixin


class MarkMixin(MarkConformMixin, MarkNonConformMixin):
    pass
