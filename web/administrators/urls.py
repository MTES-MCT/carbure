from django.urls import path

from . import views

urlpatterns = [
    path('', views.administrators_index, name='administrators-index'),
    path('controles', views.administrators_controles, name='administrators-controles'),
    path('suivi-corrections', views.administrators_suivi_corrections, name='administrators-suivi-corrections'),
    path('suivi-certificats', views.administrators_suivi_certificats, name='administrators-suivi-certificats'),
    path('gestion-utilisateurs', views.administrators_gestion_utilisateurs, name='administrators-gestion-utilisateurs'),
    path('settings', views.administrators_settings, name='administrators-settings'),


    # api-style urls
    path('suivi-certificats/validate/<int:id>', views.administrators_validate_certificate, name='administrators-validate-certificate'),


    path('users/add-entity', views.administrators_add_entity, name='administrators-add-entity'),
    path('users/add-user', views.administrators_add_user, name='administrators-add-user'),
    path('users/add-right', views.administrators_add_right, name='administrators-add-right'),
]

