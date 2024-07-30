from django.urls import path
from .depots import get_depots
from .add import add_depot
from .delete import delete_depot
from .create import create_depot

urlpatterns = [
    path("", get_depots, name="entity-depots"),
    path("add", add_depot, name="entity-depots-add"),
    path("delete", delete_depot, name="entity-depots-delete"),  # TODO Tests à reparer
    path("create", create_depot, name="depot-create"),
]
