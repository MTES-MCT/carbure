from django.urls import path
from .stocks import get_stocks

urlpatterns = [
    path("", get_stocks, name="transactions-stocks"),
]
