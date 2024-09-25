from .approve_fix import ApprouveFixMixin
from .request_fix import RequestFixMixin
from .submit_fix import SubmitFixMixin


class FixMinxin(ApprouveFixMixin, RequestFixMixin, SubmitFixMixin):
    pass
