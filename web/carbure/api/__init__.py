from django.urls import path
from .home_stats import get_home_stats

urlpatterns = [
    path("home-stats", get_home_stats, name="carbure-home-stats"),
]
