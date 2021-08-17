from django.urls import path
from . import views

from rest_framework import routers
from api.v3.massbalance.views import OutTransactionViewSet

router = routers.SimpleRouter()
router.register(r'get-dae-list', OutTransactionViewSet, basename='dae-list')


urlpatterns = [
    # GET

    # POST
    path('create-dae', views.create_dae, name='api-v3-mb-create-dae'),

    # files
    path('download-template', views.download_template, name='api-v3-mb-download-template-dae-list'),
    path('upload-dae-list', views.upload_dae_list, name='api-v3-mb-upload-dae-list'),
]

urlpatterns += router.urls
