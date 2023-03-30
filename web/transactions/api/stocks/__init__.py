from django.urls import path
from .stocks import get_stocks
from .summary import get_stocks_summary
from .details import get_stock_details
from .cancel_transformation import stock_cancel_transformation
from .transform import stock_transform

urlpatterns = [
    path("", get_stocks, name="transactions-stocks"),
    path("summary", get_stocks_summary, name="transactions-stocks-summary"),
    path("details", get_stock_details, name="transactions-stocks-details"),
    path("transform", stock_transform, name="transactions-stocks-transform"),
    path("cancel-transformation", stock_cancel_transformation, name="transactions-stocks-cancel-transformation"),
]
