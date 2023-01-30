from django.urls import path

from .update_many import update_many

urlpatterns = [
    path("update-many", update_many, name="api-v5-admin-lots-update-many"),
]
