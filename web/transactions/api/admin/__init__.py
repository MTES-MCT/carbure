from django.urls import path
from .map import map

urlpatterns = [
    path("flow-map", map, name="transactions-admin-flow-map"),
]
