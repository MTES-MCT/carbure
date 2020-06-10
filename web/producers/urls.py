from django.urls import path

from . import views
from . import v2

urlpatterns = [
    #path('<slug:producer_name>/', views.producers_index, name='producers-index'),
    path('<slug:producer_name>/controles', views.producers_controles, name='producers-controles'),
    path('<slug:producer_name>/settings', views.producers_settings, name='producers-settings'),



    path('v2/<slug:producer_name>/', v2.producers_index_v2, name='producers-index'),
    path('v2/import-documentation', v2.producers_import_doc, name='producers-import-documentation'),
]
