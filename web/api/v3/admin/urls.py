from django.urls import path
from . import views

urlpatterns = [
    path("entities/add", views.add_entity, name="api-v3-admin-add-entity"),  # Utilisé dans les tests uniquement
]
