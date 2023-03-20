from django.urls import path, include

urlpatterns = [
    path("lots/", include("api.v5.transactions.lots")),
]
