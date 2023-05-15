from django.urls import path

# from .add import add_lot
from .update import update_lot
from .request_fix import request_fix
from .submit_fix import submit_fix
from .approve_fix import approve_fix

urlpatterns = [
    # path("add", add_lot, name="transactions-lots-add"),
    path("update", update_lot, name="transactions-lots-update"),
    path("request-fix", request_fix, name="transactions-lots-request-fix"),
    path("submit-fix", submit_fix, name="transactions-lots-submit-fix"),
    path("approve-fix", approve_fix, name="transactions-lots-approve-fix"),
]
