from django.urls import path

from . import views

urlpatterns = [
    path('annuaire', views.annuaire, name='annuaire'),
]
