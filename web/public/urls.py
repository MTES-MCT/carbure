from django.urls import path

from . import views

urlpatterns = [
    path('home', views.home, name='home'), # LOGIN_REDIRECT_URL: will dispatch to either /producers/, /operators/ or /administrators/ depending on account type
    path('htmlreference', views.htmlreference, name='htmlreference'),
]
