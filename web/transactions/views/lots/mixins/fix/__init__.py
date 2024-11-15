from .approve_fix import ApproveFixMixin
from .request_fix import RequestFixMixin
from .submit_fix import SubmitFixMixin


class FixMinxin(ApproveFixMixin, RequestFixMixin, SubmitFixMixin):
    pass
