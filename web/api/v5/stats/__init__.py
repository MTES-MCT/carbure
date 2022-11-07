from django.urls import path
from .entity import get_entity

urlpatterns = [
    path("entity", get_entity, name="api-v5-stats-entity"),
]
