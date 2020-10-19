from django.urls import path
from . import views

urlpatterns = [
    # GET
    path('', views.get_stocks, name='api-v3-stocks-get'),
    path('snapshot', views.get_snapshot, name='api-v3-stocks-get-snapshot'),
]
