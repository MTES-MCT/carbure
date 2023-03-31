from django.urls import path
from .map import map

urlpatterns = [
    path("", map, name="admin-map"),
]
