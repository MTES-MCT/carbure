from django.urls import path
from .stocks import get_stocks
from .details import get_stock_details
from .summary import get_stocks_summary
from .filters import get_stock_filters


urlpatterns = [
    path("", get_stocks, name="admin-controls-stocks"),
    path("details", get_stock_details, name="admin-controls-stock-details"),
    path("summary", get_stocks_summary, name="admin-controls-stocks-summary"),
    path("filters", get_stock_filters, name="admin-controls-stocks-filters"),
]
