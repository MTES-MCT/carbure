from django.urls import path
# from .add import add_lot
from .request_fix import request_fix
from .submit_fix import submit_fix
from .approve_fix import approve_fix

urlpatterns = [
    # path("add", add_lot, name="api-v5-transactions-lots-add"),
    path("request-fix", request_fix, name="api-v5-transactions-lots-request-fix"),
    path("submit-fix", submit_fix, name="api-v5-transactions-lots-submit-fix"),
    path("approve-fix", approve_fix, name="api-v5-transactions-lots-approve-fix"),
]
