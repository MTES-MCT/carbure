from django.urls import path
from .views import enable_entity

urlpatterns = [
    path("enable", enable_entity, name="entity-admin-enable"),
]
