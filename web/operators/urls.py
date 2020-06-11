from django.urls import path

from . import views

urlpatterns = [
    path('<slug:operator_name>/', views.operators_index, name='operators-index'),
    path('<slug:operator_name>/controles', views.operators_controles, name='operators-controles'),
    path('import-documentation', views.import_doc, name='operators-import-documentation'),
]
