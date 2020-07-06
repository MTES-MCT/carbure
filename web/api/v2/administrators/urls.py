from django.urls import path

from . import admin_files
from . import admin_get

urlpatterns = [
    # files
    path('export/lots/histo', admin_files.export_histo, name='api-v2-admin-export-histo'),

    # GET
    path('lots/out', admin_get.get_out, name='api-v2-admin-get-out'),
]
