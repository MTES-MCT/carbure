from django.urls import path

from . import views

urlpatterns = [
    # ADMIN
    path("admin/upload-decision", views.upload_decision_admin, name="api-v3-doublecount-upload-decision-admin"),
    path("admin/download-decision", views.admin_download_admin_decision, name="api-v3-doublecount-download-decision-admin"),
    # PRODUCER
    path("download-admin-decision", views.download_admin_decision, name="api-v3-doublecount-download-admin-decision"),
]
