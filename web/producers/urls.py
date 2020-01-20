from django.urls import path

from . import views

urlpatterns = [
    path('', views.producers_index, name='producers-index'),
]
