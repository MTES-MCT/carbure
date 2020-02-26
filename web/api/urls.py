from django.urls import path

from . import views

urlpatterns = [
    path('lot/validate', views.lot_validate, name='api-lot-validate'),
    path('lot/save', views.lot_save, name='api-lot-save'),
]
