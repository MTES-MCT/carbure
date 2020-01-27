from django.urls import path

from . import views

urlpatterns = [
    path('', views.producers_index, name='producers-index'),
    path('attestation', views.producers_attestation, name='producers-attestation'),
    path('inbox', views.producers_inbox, name='producers-inbox'),
    path('settings', views.producers_settings, name='producers-settings'),
]
