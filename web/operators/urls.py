from django.urls import path

from . import views

urlpatterns = [
    path('<slug:operator_name>/', views.operators_index, name='operators-index'),
    path('declaration/<int:declaration_id>', views.operators_declaration, name='operators-declaration'),
    path('affiliations', views.operators_affiliations, name='operators-affiliations'),
    path('controles', views.operators_controles, name='operators-controles'),
    path('settings', views.operators_settings, name='operators-settings'),
]
