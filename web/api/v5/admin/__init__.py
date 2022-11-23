from django.urls import path

from .create_entity import create_entity

urlpatterns = [
    path("create_entity", create_entity, name="api-v5-admin-create-entity"),
]
