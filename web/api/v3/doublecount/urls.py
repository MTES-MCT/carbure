from django.urls import path
from . import views

urlpatterns = [
    # GET
    path('agreements', views.get_agreements, name='api-v3-doublecount-get-agreements'),
    path('agreement', views.get_agreement, name='api-v3-doublecount-get-agreement'),
    path('admin/agreement', views.get_agreement_admin, name='api-v3-doublecount-get-agreement-admin'),
    path('admin/agreements', views.get_agreements_admin, name='api-v3-doublecount-get-agreements-admin'),            
    path('template', views.get_template, name='api-v3-doublecount-get-template'),
    
    # POST
    path('upload', views.upload_file, name='api-v3-doublecount-upload-file'),
    path('approve', views.approve_dca, name='api-v3-doublecount-approve-dca'),
    path('reject', views.reject_dca, name='api-v3-doublecount-reject-dca'),
]
