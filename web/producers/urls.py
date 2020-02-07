from django.urls import path

from . import views

urlpatterns = [
    path('', views.producers_index, name='producers-index'),
    path('attestation', views.producers_attestation, name='producers-attestation'),
    path('corrections', views.producers_corrections, name='producers-corrections'),
    path('controles', views.producers_controles, name='producers-controles'),
    path('settings', views.producers_settings, name='producers-settings'),
]
