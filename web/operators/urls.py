from django.urls import path

from . import views

urlpatterns = [
    path('', views.operators_index, name='operators-index'),
    path('new', views.operators_new_lots, name='operators-new-lots'),
    path('pending', views.operators_pending_lots, name='operators-pending-lots'),
    path('settings', views.operators_settings, name='operators-settings'),
]
