from django.urls import path

from .update_many import update_many
from .delete_many import delete_many

urlpatterns = [
    path("update-many", update_many, name="admin-lots-update-many"),
    path("delete-many", delete_many, name="admin-lots-delete-many"),
]
