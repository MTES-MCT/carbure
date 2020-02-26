from django.urls import path

from . import views

urlpatterns = [
    path('', views.operators_index, name='operators-index'),
    path('declaration', views.operators_declaration, name='operators-declaration'),
    path('lot', views.operators_lot, name='operators-lot'),
    path('export', views.operators_export, name='operators-export'),
    path('annuaire', views.operators_annuaire, name='operators-annuaire'),
    path('affiliations', views.operators_affiliations, name='operators-affiliations'),
    path('corrections', views.operators_corrections, name='operators-corrections'),
    path('controles', views.operators_controles, name='operators-controles'),
    path('settings', views.operators_settings, name='operators-settings'),
]
