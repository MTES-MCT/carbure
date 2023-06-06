from django.urls import path
from . import views

urlpatterns = [
    # GET
    path("agreements", views.get_agreements, name="api-v3-doublecount-get-agreements"),
    path("agreement", views.get_agreement, name="api-v3-doublecount-get-agreement"),
    path("admin/agreement", views.get_agreement_admin, name="api-v3-doublecount-get-agreement-admin"),
    # path("admin/agreements", views.get_agreements_admin, name="api-v3-doublecount-get-agreements-admin"),
    path(
        "admin/agreements-snapshot",
        views.get_agreements_snapshot_admin,
        name="api-v3-doublecount-get-agreements-snapshot-admin",
    ),
    path("admin/quotas", views.get_production_site_quotas_admin, name="api-v3-doublecount-get-quotas-admin"),
    path("admin/quotas-snapshot", views.get_quotas_snapshot_admin, name="api-v3-doublecount-get-quotas-snapshot-admin"),
    path("admin/upload-decision", views.upload_decision_admin, name="api-v3-doublecount-upload-decision-admin"),
    path("admin/download-decision", views.admin_download_admin_decision, name="api-v3-doublecount-download-decision-admin"),
    path("get-template", views.get_template, name="api-v3-doublecount-get-template"),
    path("quotas", views.get_production_site_quotas, name="api-v3-doublecount-get-quotas"),
    # POST
    path("agreement/remove-sourcing", views.remove_sourcing, name="api-v3-doublecount-remove-sourcing"),
    path("agreement/update-sourcing", views.update_sourcing, name="api-v3-doublecount-update-sourcing"),
    path("agreement/add-sourcing", views.add_sourcing, name="api-v3-doublecount-add-sourcing"),
    path("agreement/remove-production", views.remove_production, name="api-v3-doublecount-remove-production"),
    path("agreement/update-production", views.update_production, name="api-v3-doublecount-update-production"),
    path("agreement/add-production", views.add_production, name="api-v3-doublecount-add-production"),
    path("upload", views.upload_file, name="api-v3-doublecount-upload-file"),
    path("upload-documentation", views.upload_documentation, name="api-v3-doublecount-upload-doc"),
    path("download-documentation", views.download_documentation, name="api-v3-doublecount-download-doc"),
    path("download-admin-decision", views.download_admin_decision, name="api-v3-doublecount-download-admin-decision"),
    path("admin/download-documentation", views.admin_download_documentation, name="api-v3-doublecount-admin-download-doc"),
    path("admin/approve", views.approve_dca, name="api-v3-doublecount-approve-dca"),
    path("admin/reject", views.reject_dca, name="api-v3-doublecount-reject-dca"),
    path(
        "admin/agreement/update-approved-quotas",
        views.admin_update_approved_quotas,
        name="api-v3-doublecount-admin-update-approved-quotas",
    ),
]
