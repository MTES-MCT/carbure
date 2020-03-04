from django.urls import path

from . import views

urlpatterns = [
    path('', views.producers_index, name='producers-index'),
    path('export', views.producers_export, name='producers-export'),
    path('annuaire', views.producers_annuaire, name='producers-annuaire'),
    path('attestation/<int:attestation_id>', views.producers_attestation, name='producers-attestation'),
    path('corrections', views.producers_corrections, name='producers-corrections'),
    path('controles', views.producers_controles, name='producers-controles'),

    # settings
    path('settings', views.producers_settings, name='producers-settings'),
    path('settings/add-certif', views.producers_settings_add_certif, name='producers-settings-add-certif'),
]
