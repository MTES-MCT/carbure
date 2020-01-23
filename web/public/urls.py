from django.urls import path

from . import views

urlpatterns = [
    path('htmlreference', views.htmlreference, name='htmlreference'),
]
