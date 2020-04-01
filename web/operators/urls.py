from django.urls import path

from . import views

urlpatterns = [
    path('', views.operators_index, name='operators-index'),
    path('declaration/<int:declaration_id>', views.operators_declaration, name='operators-declaration'),
    path('lot', views.operators_lot, name='operators-lot'),
    path('affiliations', views.operators_affiliations, name='operators-affiliations'),
    path('controles', views.operators_controles, name='operators-controles'),
    path('settings', views.operators_settings, name='operators-settings'),
]
