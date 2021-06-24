from django.urls import path
from . import views

urlpatterns = [
    # GET
    path('lots', views.get_lots, name='api-v3-auditor-lots-get'),
    path('details', views.get_details, name='api-v3-auditor-lots-get-details'),
    path('filters', views.get_filters, name='api-v3-auditor-lots-get-filters'),
    path('snapshot', views.get_snapshot, name='api-v3-auditor-lots-get-snapshot'),
    path('summary', views.get_lots_summary, name='api-v3-auditor-lots-get-summary'),


    # POST
    # auditor actions
    path('lots/hide-transactions', views.hide_transactions, name='api-v3-auditor-hide-transactions'),
    path('lots/highlight-transactions', views.highlight_transactions, name='api-v3-auditor-highlight-transactions'),
]
