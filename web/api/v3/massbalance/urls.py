from django.urls import path
from . import views

urlpatterns = [
    # APIView    
    path('get-pending-transactions', views.get_pending_transactions_list),
    path('add-pending-transactions', views.add_pending_transactions),

    # files
    path('download-template', views.download_template, name='api-v3-mb-download-template-dae-list'),
    path('upload-dae-list', views.upload_dae_list, name='api-v3-mb-upload-dae-list'),
]
