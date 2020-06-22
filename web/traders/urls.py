from django.urls import path

from . import views

urlpatterns = [
    path('<slug:trader_name>/', views.traders_index, name='traders-index'),
    path('import-documentation', views.import_doc, name='traders-import-documentation'),
]
