from django.urls import path

from . import views

urlpatterns = [
    path('', views.operators_index, name='operators-index'),
]
