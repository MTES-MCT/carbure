from django.urls import path
from .users import get_users
from .rights_requests import get_rights_requests
from .update_right_request import update_right_request

urlpatterns = [
    path("rights-requests", get_rights_requests, name="admin-entities-users-rights-requests"),
    path("update-right-request", update_right_request, name="admin-entities-update-rights-requests"),
]
