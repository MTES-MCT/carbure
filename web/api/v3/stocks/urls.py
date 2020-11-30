from django.urls import path
from . import views

urlpatterns = [
    # GET
    path('', views.get_stocks, name='api-v3-stocks-get'),
    path('snapshot', views.get_snapshot, name='api-v3-stocks-get-snapshot'),
    path('send-lot', views.send_lot, name='api-v3-stocks-send-lot'),

    path('download-template-mass-balance', views.get_template_mass_balance, name='api-v3-template-mass-balance'),
    path('download-template-mass-balance-bcghg', views.get_template_mass_balance_bcghg, name='api-v3-template-mass-balance-bcghg'),

]
