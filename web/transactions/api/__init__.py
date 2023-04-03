from django.urls import path, include

urlpatterns = [
    path("stocks/", include("transactions.api.stocks")),
]
