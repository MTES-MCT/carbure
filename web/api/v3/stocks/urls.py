from django.urls import path
from . import views

urlpatterns = [
    # GET
    path('', views.get_stocks, name='api-v3-stocks-get'),
    path('snapshot', views.get_snapshot, name='api-v3-stocks-get-snapshot'),
    path('depots', views.get_depots, name='api-v3-stocks-get-depots'),
    path('summary', views.get_stocks_summary, name='api-v3-stocks-get-summary'),
    path('filters', views.get_filters, name='api-v3-stocks-get-filters'),

    # POST
    path('generate-batch', views.generate_batch, name='api-v3-stocks-generate-batch'),
    path('create-drafts', views.create_drafts, name='api-v3-stocks-create-drafts'),
    path('send-drafts', views.send_drafts, name='api-v3-stocks-send-drafts'),
    path('convert-to-etbe', views.convert_to_etbe, name='api-v3-stocks-convert-to-etbe'),
    path('forward', views.forward, name='api-v3-stocks-forward'),

    # files
    path('download-template-mass-balance', views.get_template_mass_balance, name='api-v3-template-mass-balance'),
    path('download-template-mass-balance-bcghg', views.get_template_mass_balance_bcghg, name='api-v3-template-mass-balance-bcghg'),
    path('upload-mass-balance', views.upload_mass_balance, name='api-v3-upload-mass-balance'),

]
