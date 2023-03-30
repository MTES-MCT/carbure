from django.urls import path
from .stocks import get_stocks
from .summary import get_stocks_summary


urlpatterns = [
    path("", get_stocks, name="transactions-stocks"),
    path("summary", get_stocks_summary, name="transactions-stocks-summary"),
]
