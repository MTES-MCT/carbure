"""carbure URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from public import views as public_views
from magicauth.urls import urlpatterns as magicauth_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('authtools.urls')),
    path('accounts/', include('accounts.urls')),
    path('', public_views.index, name='index'),

    path('stats', public_views.stats, name='stats'),
    path('api/', include('api.urls')),

    # deprecated - will be removed soon
    path('producers/', include('producers.urls')),
    path('operators/', include('operators.urls')),
    path('traders/', include('traders.urls')),
    path('administrators/', include('administrators.urls')),
    path('core/', include('core.urls')),
    path('annuaire', public_views.annuaire, name='annuaire'),
]

urlpatterns.extend(magicauth_urls)
