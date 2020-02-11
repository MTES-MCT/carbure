from django.urls import path

from . import views

urlpatterns = [
    path('', views.administrators_index, name='administrators-index'),
    path('export', views.administrators_export, name='administrators-export'),
    path('controles', views.administrators_controles, name='administrators-controles'),
    path('settings', views.administrators_settings, name='administrators-settings'),
]
