from django.urls import path

from . import views

urlpatterns = [
    path('<slug:operator_name>/', views.operators_index, name='operators-index'),
    path('<slug:operator_name>/declaration/<int:declaration_id>', views.operators_declaration, name='operators-declaration'),
    path('<slug:operator_name>/affiliations', views.operators_affiliations, name='operators-affiliations'),
    path('<slug:operator_name>/controles', views.operators_controles, name='operators-controles'),
]
