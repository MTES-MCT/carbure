from django.urls import path

from . import views

urlpatterns = [
    path('<slug:producer_name>/', views.producers_index, name='producers-index'),
    path('<slug:producer_name>/controles', views.producers_controles, name='producers-controles'),
    path('<slug:producer_name>/settings', views.producers_settings, name='producers-settings'),



    path('v2/<slug:producer_name>/', views.producers_index_v2, name='producers-index-v2'),

]
