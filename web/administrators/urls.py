from django.urls import path

from . import views

urlpatterns = [
    path('', views.administrators_index, name='administrators-index'),
    path('annuaire', views.administrators_annuaire, name='administrators-annuaire'),
    path('controles', views.administrators_controles, name='administrators-controles'),
    path('suivi-corrections', views.administrators_suivi_corrections, name='administrators-suivi-corrections'),
    path('suivi-certificats', views.administrators_suivi_certificats, name='administrators-suivi-certificats'),
    path('gestion-utilisateurs', views.administrators_gestion_utilisateurs, name='administrators-gestion-utilisateurs'),
    path('settings', views.administrators_settings, name='administrators-settings'),
]
