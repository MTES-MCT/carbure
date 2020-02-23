from django.urls import path

from . import views

urlpatterns = [
    path('set-default-entity/<int:entity_id>', views.set_default_entity, name='core-set-default-entity'),
]
