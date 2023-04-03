from django.urls import path
from .declarations import get_declarations

urlpatterns = [
    path("declarations", get_declarations, name="admin-dashboard-declarations"),
]
