from django.urls import path
from . import views

urlpatterns = [
    path('users', views.get_users, name='api-v3-admin-get-users'),
    path('users/rights-requests', views.get_rights_requests, name='api-v3-admin-get-rights-requests'),
    path('users/update-right-request', views.update_right_request, name='api-v3-admin-update-right-request'),

    path('entities', views.get_entities, name='api-v3-admin-get-entities'),
    path('entities/add', views.add_entity, name='api-v3-admin-add-entity'),
    path('entities/del', views.delete_entity, name='api-v3-admin-delete-entity'),


    path('certificates', views.get_certificates, name='api-v3-admin-get-certificates'),
    path('certificates/update-certificate', views.update_certificate, name='api-v3-admin-update-certificate'),

    path('controls', views.get_controls, name='api-v3-admin-get-controls'),
    path('controls/open', views.open_control, name='api-v3-admin-open-control'),
    path('controls/close', views.close_control, name='api-v3-admin-close-control'),

    path('dashboard/declarations', views.get_declarations, name='api-v3-admin-get-declarations'),
    path('dashboard/declaration/send-reminder', views.send_declaration_reminder, name='api-v3-admin-send-declaration-reminder'),
    path('dashboard/declaration/check', views.check_declaration, name='api-v3-admin-check-declaration'),
    path('dashboard/declaration/uncheck', views.uncheck_declaration, name='api-v3-admin-uncheck-declaration'),


    
    path('lots', views.get_lots, name='api-v3-admin-get-lots'),
    path('lots/details', views.get_details, name='api-v3-admin-get-lot-details'),
    path('lots/snapshot', views.get_snapshot, name='api-v3-admin-get-snapshot'),

]
