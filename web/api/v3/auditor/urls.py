from django.urls import path
from . import views

urlpatterns = [
    # GET
    path('', views.get_lots, name='api-v3-auditor-lots-get'),
    path('details', views.get_details, name='api-v3-auditor-lots-get-details'),
    path('snapshot', views.get_snapshot, name='api-v3-auditor-lots-get-snapshot'),


    # POST
    # auditor actions

]
