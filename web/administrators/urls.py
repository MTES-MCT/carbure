from django.urls import path

from . import views

urlpatterns = [
    path('', views.administrators_index, name='administrators-index'),
    path('annuaire', views.administrators_annuaire, name='administrators-annuaire'),
    path('controles', views.administrators_controles, name='administrators-controles'),
    path('suivi-corrections', views.administrators_suivi_corrections, name='administrators-suivi-corrections'),
    path('settings', views.administrators_settings, name='administrators-settings'),
]
