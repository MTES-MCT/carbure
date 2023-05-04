from django.urls import path, include

urlpatterns = [
    path("lots/", include("transactions.api.lots")),
    path("stocks/", include("transactions.api.stocks")),
]
