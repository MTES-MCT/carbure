from django.urls import path

from . import views

urlpatterns = [
    path('', views.administrators_index, name='administrators-index'),
    path('controles', views.administrators_controles, name='administrators-controles'),
    path('suivi-corrections', views.administrators_suivi_corrections, name='administrators-suivi-corrections'),
    path('suivi-certificats', views.administrators_suivi_certificats, name='administrators-suivi-certificats'),
    path('suivi-certificats/<int:id>', views.administrators_certificate_details, name='administrators-certificate-details'),
    path('gestion-utilisateurs', views.administrators_gestion_utilisateurs, name='administrators-gestion-utilisateurs'),
    path('settings', views.administrators_settings, name='administrators-settings'),


    # TODO: move to API
    # api-style urls
    path('suivi-certificats/validate/<int:id>', views.administrators_validate_certificate, name='administrators-validate-certificate'),
    path('suivi-certificats/validate-input/<int:crtid>/<int:inputid>', views.administrators_validate_input, name='administrators-validate-input'),
    path('suivi-certificats/validate-output/<int:crtid>/<int:outputid>', views.administrators_validate_output, name='administrators-validate-output'),
    path('suivi-certificats/delete-input/<int:crtid>/<int:inputid>', views.administrators_delete_input, name='administrators-delete-input'),
    path('suivi-certificats/delete-output/<int:crtid>/<int:outputid>', views.administrators_delete_output, name='administrators-delete-output'),


    path('users/add-entity', views.administrators_add_entity, name='administrators-add-entity'),
    path('users/add-user', views.administrators_add_user, name='administrators-add-user'),
    path('users/add-right', views.administrators_add_right, name='administrators-add-right'),
    path('users/delete-right', views.administrators_delete_right, name='administrators-delete-right'),
    path('users/reset-password/<int:uid>', views.administrators_reset_user_password, name='administrators-reset-user-password'),
]

