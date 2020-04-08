from django.urls import path

from . import views

urlpatterns = [
    path('<slug:producer_name>/', views.producers_index, name='producers-index'),
    path('<slug:producer_name>/attestation/<slug:attestation_period>', views.producers_attestation, name='producers-attestation'),
    path('<slug:producer_name>/corrections', views.producers_corrections, name='producers-corrections'),
    path('<slug:producer_name>/controles', views.producers_controles, name='producers-controles'),
    # settings
    path('<slug:producer_name>/settings', views.producers_settings, name='producers-settings'),
]
