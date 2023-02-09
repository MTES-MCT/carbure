from django.urls import path, include
from .entities import update_entity

urlpatterns = [
    path("update-entity", update_entity, name="api-v5-settings-update-entity"),
]

