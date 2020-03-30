from django.urls import path

from . import views

urlpatterns = [
    path('', views.producers_index, name='producers-index'),
    path('attestation/<int:attestation_id>', views.producers_attestation, name='producers-attestation'),
    #path('<slug:producer_name>/attestation/<slug:periode>', views.producers_attestation_userfriendly, name='producers-attestation-user-friendly'),
    path('attestation/<int:attestation_id>/lot/new', views.producers_new_lot, name='producers-attestation-new-lot'),
    path('attestation/<int:attestation_id>/lot/<int:lot_id>/edit', views.producers_edit_lot, name='producers-attestation-edit-lot'),


    path('corrections', views.producers_corrections, name='producers-corrections'),
    path('controles', views.producers_controles, name='producers-controles'),

    # settings
    path('settings', views.producers_settings, name='producers-settings'),
]
