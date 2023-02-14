from django.urls import path, include

from .create_entity import create_entity

urlpatterns = [
    path("lots/", include("api.v5.admin.lots")),
    path("create-entity", create_entity, name="api-v5-admin-create-entity"),
]
