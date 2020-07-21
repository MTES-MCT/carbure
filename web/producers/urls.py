from django.urls import path

from . import views
from . import v2

urlpatterns = [
    path('<slug:producer_name>/controles', views.producers_controles, name='producers-controles'),
    path('<slug:producer_name>/settings', views.producers_settings, name='producers-settings'),
    path('v2/<slug:producer_name>/', v2.producers_index_v2, name='producers-index'),
    path('v2/<slug:producer_name>/mass-balance', v2.producers_mass_balance, name='producers-mb'),
    path('v2/<slug:producer_name>/archives', v2.producers_histo, name='producers-histo'),
    path('v2/import-documentation', v2.producers_import_doc, name='producers-import-documentation'),
    path('v2/<slug:producer_name>/stats', v2.stats, name='producers-stats'),
    path('v2/new_design', v2.new_design, name='producers-new-design'),

]
