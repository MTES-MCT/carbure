from django.urls import path

from . import views

urlpatterns = [
    path('<slug:trader_name>/', views.traders_index, name='traders-index'),
    path('<slug:trader_name>/mass-balance', views.traders_mb, name='traders-mb'),
    path('<slug:trader_name>/histo', views.traders_histo, name='traders-histo'),
    path('import-documentation', views.import_doc, name='traders-import-documentation'),
]
