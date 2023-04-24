from django.urls import path
from .stats import get_stats

urlpatterns = [
    path("", get_stats, name="stats"),
]
