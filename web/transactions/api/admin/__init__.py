from django.urls import include, path
from .map import map
from transactions.api.admin.declarations import get_declarations

urlpatterns = [
    path("flow-map", map, name="transactions-admin-flow-map"),
    path("declarations", get_declarations, name="transactions-admin-declarations"),
    path("entities/", include("transactions.api.admin.entities")),
]
