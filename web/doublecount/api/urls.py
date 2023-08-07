from django.urls import path

from . import views

urlpatterns = [
    # GET
    path("applications", views.get_applications, name="api-v3-doublecount-get-applications"),
    path("application", views.get_application, name="api-v3-doublecount-get-application"),
    # path("admin/quotas", views.get_production_site_quotas_admin, name="api-v3-doublecount-get-quotas-admin"),
    path("admin/quotas-snapshot", views.get_quotas_snapshot_admin, name="api-v3-doublecount-get-quotas-snapshot-admin"),
    path("admin/upload-decision", views.upload_decision_admin, name="api-v3-doublecount-upload-decision-admin"),
    path("admin/download-decision", views.admin_download_admin_decision, name="api-v3-doublecount-download-decision-admin"),
    path("get-template", views.get_template, name="api-v3-doublecount-get-template"),
    path("quotas", views.get_production_site_quotas, name="api-v3-doublecount-get-quotas"),
    # POST
    path("application/remove-sourcing", views.remove_sourcing, name="api-v3-doublecount-remove-sourcing"),
    path("application/update-sourcing", views.update_sourcing, name="api-v3-doublecount-update-sourcing"),
    path("application/add-sourcing", views.add_sourcing, name="api-v3-doublecount-add-sourcing"),
    path("application/remove-production", views.remove_production, name="api-v3-doublecount-remove-production"),
    path("application/update-production", views.update_production, name="api-v3-doublecount-update-production"),
    path("application/add-production", views.add_production, name="api-v3-doublecount-add-production"),
    path("upload", views.upload_file, name="api-v3-doublecount-upload-file"),
    path("upload-documentation", views.upload_documentation, name="api-v3-doublecount-upload-doc"),
    path("download-documentation", views.download_documentation, name="api-v3-doublecount-download-doc"),
    path("download-admin-decision", views.download_admin_decision, name="api-v3-doublecount-download-admin-decision"),
]
