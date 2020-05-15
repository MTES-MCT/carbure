from django.urls import path

from . import views

urlpatterns = [
    path('<slug:operator_name>/', views.operators_index, name='operators-index'),
    path('<slug:operator_name>/controles', views.operators_controles, name='operators-controles'),
]
